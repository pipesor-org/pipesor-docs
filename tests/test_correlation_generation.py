"""DD-023 source/renderer regression checks; SQL behavior is checked separately."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools/generators'))
from correlation_constraints import FIELDS, MEMBERSHIPS, TABLES
from domain_validation import validate_domain
from to_dbml import generate_dbml
from to_sql import generate_extras, validate_export


class CorrelationGenerationTests(unittest.TestCase):
    def setUp(self):
        self.model = yaml.safe_load((ROOT / 'model/domain.yml').read_text())
        self.architecture = yaml.safe_load((ROOT / 'model/architecture.yml').read_text())

    def entity(self, name):
        return next(e for e in self.model['entities'] if e['table'] == name)

    def rejected(self, fragment):
        errors = validate_domain(self.model, self.architecture)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_approved_metadata_is_exact_and_technical_retention_is_not_invented(self):
        self.assertEqual(validate_domain(self.model, self.architecture), [])
        self.assertEqual(self.model['model_version'], '1.9.0')
        self.assertEqual(len(self.model['entities']), 35)
        for name in TABLES:
            self.assertEqual(set(FIELDS[name]), {a['name'] for a in self.entity(name)['attributes']})
            if name != 'correlated_contexts':
                self.assertIsNone(self.entity(name)['retention_policy'])
        self.assertEqual(self.entity('pipeline_access_grants')['status'], 'inferred')
        self.assertTrue(all(q['status'] == 'open_question' for q in self.model['open_questions']))

    def test_unapproved_payload_fields_and_changed_ownership_are_rejected(self):
        for name in TABLES:
            with self.subTest(table=name):
                entity = self.entity(name)
                entity['attributes'].append(dict(entity['attributes'][0], name='raw_body', pk=False))
                self.rejected('only approved correlation metadata')
                entity['attributes'].pop()
                entity['owner_container'] = 'log_event_service'
                self.rejected('correlation owner/status')
                entity['owner_container'] = 'evidence_correlation_engine'
        self.entity('correlation_groups')['retention_policy'] = 'RET-001'
        self.rejected('no technical receipt/group retention')

    def test_required_fields_and_natural_receipt_key_cannot_be_weakened(self):
        for name in TABLES:
            for attr in self.entity(name)['attributes']:
                with self.subTest(table=name, field=attr['name']):
                    original = deepcopy(attr)
                    attr['nullable'] = not attr['nullable']
                    self.rejected('approved type/nullability')
                    attr.update(original)
        receipt = self.entity('correlation_receipts')
        self.assertEqual([a['name'] for a in receipt['attributes'] if a['pk']],
                         ['scope_key', 'producer_key', 'message_id'])
        receipt['attributes'][0]['pk'] = False
        self.rejected('approved correlation primary key')

    def test_signal_columns_and_each_required_check_cannot_be_weakened(self):
        context = self.entity('correlated_contexts')
        self.assertEqual(len(context['attributes']), 16)
        for attr in context['attributes']:
            if not attr['name'].startswith('signal_'):
                continue
            with self.subTest(field=attr['name']):
                attr['type'] = 'jsonb'
                self.rejected('approved type/nullability')
                attr['type'] = 'text'
        for check in list(context['checks']):
            with self.subTest(check=check['name']):
                context['checks'].remove(check)
                self.rejected('approved correlation CHECK')
                context['checks'].append(check)
        dbml = generate_dbml(self.model)
        for field in ('signal_stage', 'signal_summary', 'signal_content'):
            self.assertIn(f'{field} text [not null', dbml)
        self.assertIn("signal_stage IN ('BUILD', 'TESTING', 'QUALITY_GATE', 'DEPLOYMENT', 'CONTAINER', 'INFRASTRUCTURE')", dbml)
        self.assertIn('NEW.signal_stage IS NULL OR NEW.signal_summary IS NULL OR NEW.signal_content IS NULL',
                      generate_extras(self.model))

    def test_scope_is_typed_nullable_pipeline_and_frozen_per_operation(self):
        context = self.entity('correlated_contexts')
        attrs = {a['name']: a for a in context['attributes']}
        self.assertTrue(attrs['scope_pipeline_id']['nullable'])
        self.assertEqual(attrs['scope_pipeline_id']['logical_ref'], 'ops.pipelines.id')
        extras = generate_extras(self.model)
        self.assertIn('NEW.scope_tenant_id IS NULL', extras)
        self.assertIn('correlated_contexts_scope_binding_ck', extras)
        binding = extras.split("Correlation snapshot scope does not match its group")[0].rsplit('IF ROW(',1)[1]
        self.assertNotIn('scope_revision', binding)
        self.assertEqual(attrs['scope_revision']['type'], 'text')

    def test_checks_membership_and_lifecycle_markers_cannot_be_removed(self):
        for name in TABLES:
            entity = self.entity(name)
            for field, fragment in [('checks', 'approved correlation CHECK'),
                                    ('domain_constraints', 'correlation_lifecycle')]:
                original = entity[field]
                entity[field] = []
                self.rejected(fragment)
                entity[field] = original
        for name, _, _, _ in MEMBERSHIPS:
            entity = self.entity(name)
            original = entity['foreign_keys']
            entity['foreign_keys'] = []
            self.rejected('approved correlation membership')
            entity['foreign_keys'] = original
        self.entity('correlation_groups')['unique_constraints'] = []
        self.rejected('missing approved uniqueness')

    def test_foreign_owners_remain_logical_and_context_fk_stays_owned(self):
        for table, column in [('correlation_groups', 'execution_id'),
                              ('correlation_groups', 'incident_id'),
                              ('correlation_receipts', 'evidence_id')]:
            attr = next(a for a in self.entity(table)['attributes'] if a['name'] == column)
            attr['fk'] = attr.pop('logical_ref')
            self.rejected('required logical_ref')
            attr['logical_ref'] = attr.pop('fk')
        attr = next(a for a in self.entity('correlation_receipts')['attributes'] if a['name'] == 'context_id')
        attr.pop('fk')
        self.rejected('required fk to evidence.correlated_contexts.id')

    def test_generated_guards_cover_chain_confirmation_receipt_and_statement_mutation(self):
        sql = generate_extras(self.model)
        for fragment in ('correlated_contexts_group_revision_uq', 'group_id, cardinality(evidence_ids)',
                         'correlation_receipts_context_evidence_idx',
                         'ON evidence.correlation_receipts (context_id, evidence_id)',
                         'WHERE id = NEW.group_id FOR UPDATE', 'count(DISTINCT member)',
                         'cardinality(NEW.evidence_ids) <> cardinality(previous.evidence_ids) + 1',
                         'NOT NEW.evidence_ids @> previous.evidence_ids',
                         'g.confirmed_context_id IS DISTINCT FROM previous.id',
                         'next_revision <> COALESCE(previous_revision, 0) + 1',
                         'NEW.updated_at IS DISTINCT FROM OLD.updated_at',
                         'correlation_receipts_original_context_ck', 'correlated_contexts_receipt_ck',
                         'DEFERRABLE INITIALLY DEFERRED'):
            self.assertIn(fragment, sql)
        for name in TABLES:
            operations = 'DELETE OR TRUNCATE' if name == 'correlation_groups' else 'UPDATE OR DELETE OR TRUNCATE'
            self.assertIn(f'BEFORE {operations} ON evidence.{name}', sql)
        correlation = sql[sql.index('-- DD-023:'):]
        self.assertNotIn('FROM ops.', correlation)
        self.assertNotIn('FROM evidence.evidence_items', correlation)
        for line in correlation.splitlines():
            if 'RAISE EXCEPTION' in line:
                self.assertNotIn('%', line)
        self.assertNotIn('evidence.guard_correlation', generate_dbml(self.model))

    def test_dbml_exposes_compound_memberships_and_export_requires_the_natural_pk(self):
        dbml = generate_dbml(self.model)
        self.assertIn('evidence.correlation_groups.(id, confirmed_context_id) > evidence.correlated_contexts.(group_id, id)', dbml)
        self.assertIn('evidence.correlated_contexts.(group_id, incident_id, execution_id) > evidence.correlation_groups.(id, incident_id, execution_id)', dbml)
        # The exporter may succeed with a partial PK; that output must still be rejected.
        model = {'entities': [self.entity('correlation_receipts')]}
        sql = 'CREATE TABLE "evidence"."correlation_receipts" ("message_id" uuid PRIMARY KEY);'
        with self.assertRaisesRegex(ValueError, 'omitted composite primary key'):
            validate_export(sql, model)
