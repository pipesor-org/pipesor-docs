"""Capture ledger SSOT contracts; no live GitHub or broker calls."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools/generators'))
from domain_validation import validate_domain
from capture_constraints import TABLES
from to_sql import generate_extras


class CaptureGenerationTests(unittest.TestCase):
    def setUp(self):
        self.model = yaml.safe_load((ROOT/'model/domain.yml').read_text())
        self.architecture = yaml.safe_load((ROOT/'model/architecture.yml').read_text())

    def entity(self, name):
        return next(e for e in self.model['entities'] if e['table'] == name)

    def test_only_four_capture_tables_are_added_under_ingestion_ownership(self):
        self.assertEqual(validate_domain(self.model, self.architecture), [])
        self.assertEqual(len(self.model['entities']), 36)
        for table in TABLES:
            self.assertEqual(self.entity(table)['owner_container'], 'ingestion_normalization_service')
            self.assertIsNone(self.entity(table)['retention_policy'])
        self.entity('capture_receipts')['attributes'].append(dict(self.entity('capture_receipts')['attributes'][2], name='raw_body'))
        self.assertTrue(any('raw inputs' in e for e in validate_domain(self.model, self.architecture)))

    def test_only_declared_ingestion_tables_are_accepted(self):
        extra = deepcopy(self.entity('repository_admissions'))
        extra['id'] = extra['table'] = 'unapproved_admissions'
        self.model['entities'].append(extra)
        self.assertTrue(any('ingestion requires only' in e for e in validate_domain(self.model, self.architecture)))

    def test_reserved_uuids_lossless_instants_and_membership_are_required(self):
        for table, field in [('capture_receipts', 'snapshot_message_id'), ('capture_observations', 'observed_at_submicro')]:
            with self.subTest(field=field):
                attribute = next(a for a in self.entity(table)['attributes'] if a['name'] == field)
                attribute['nullable'] = True
                self.assertTrue(validate_domain(self.model, self.architecture))
                attribute['nullable'] = False
        for field in ('unique_constraints', 'foreign_keys'):
            with self.subTest(field=field):
                original = self.entity('capture_receipts')[field]
                self.entity('capture_receipts')[field] = []
                self.assertTrue(any('missing approved capture' in e for e in validate_domain(self.model, self.architecture)))
                self.entity('capture_receipts')[field] = original

    def test_capture_guards_and_closed_plan_are_exported(self):
        sql = generate_extras(self.model)
        for fragment in ('capture_context_ck', 'capture_plan_ck', 'capture_receipts_guard_ck',
                         'publication_outputs_guard_ck', 'OLD.lease_until <= NEW.updated_at',
                         'OLD.payload_recover_until', 'linked.tenant_id,linked.app_id',
                         'capture_observations_immutable BEFORE UPDATE OR DELETE OR TRUNCATE'):
            self.assertIn(fragment, sql)
        self.entity('publication_outputs')['partial_unique_constraints'] = []
        self.assertTrue(any('output uniqueness' in e for e in validate_domain(self.model, self.architecture)))
