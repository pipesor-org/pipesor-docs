#!/usr/bin/env python3
"""Run generated DDL against an owned, disposable PostgreSQL+pgvector container.

No host ports, mounts, credentials, production URL, or application data. Docker
access and an available image are prerequisites. Missing prerequisites fail.
"""
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
import uuid

import yaml

ROOT = Path(__file__).resolve().parents[1]
IMAGE = os.environ.get('POSTGRES_TEST_IMAGE', 'pgvector/pgvector@sha256:0dd3149a06e4579a0d70d8fef9945636cd514005e7237deb27f9b67886f8dc4f')
ONE = '00000000-0000-0000-0000-000000000001'
TWO = '00000000-0000-0000-0000-000000000002'


class PersistenceTests(unittest.TestCase):
    container = None

    @classmethod
    def sql(cls, sql):
        return subprocess.run(['docker', 'exec', '-i', cls.container, 'psql', '-U', 'postgres',
                               '-X', '-v', 'ON_ERROR_STOP=1', '-v', 'VERBOSITY=verbose'],
                              input=sql, text=True, capture_output=True, timeout=30)

    @classmethod
    def setUpClass(cls):
        cls.container = 'pipesor-sql-test-' + uuid.uuid4().hex
        subprocess.run(['docker', 'run', '-d', '--network=none', '--name', cls.container,
                        '-e', 'POSTGRES_HOST_AUTH_METHOD=trust', IMAGE], check=True, capture_output=True)
        cls.addClassCleanup(subprocess.run, ['docker', 'rm', '-f', cls.container], check=True, capture_output=True)
        for _ in range(60):
            ready = subprocess.run(['docker', 'exec', cls.container, 'pg_isready', '-h', '127.0.0.1', '-U', 'postgres'], capture_output=True)
            if ready.returncode == 0:
                break
            time.sleep(0.5)
        else:
            raise RuntimeError('Disposable PostgreSQL did not become ready')
        ddl = (ROOT / 'build/schema.sql').read_text() + '\n' + (ROOT / 'build/extras.sql').read_text()
        result = cls.sql(ddl)
        if result.returncode:
            raise RuntimeError(result.stderr)
        model = yaml.safe_load((ROOT / 'model/domain.yml').read_text())
        enums = {e['id']: e['values'][0] for e in model['enums']}
        inserts = []
        for entity in model['entities']:
            if entity['schema'] == 'ingestion' or entity['table'] in ('correlation_groups', 'correlated_contexts', 'correlation_receipts'):
                continue  # DD-020 needs coherent lifecycle metadata, not generic scalar values.
            cols, values = [], []
            for c in entity['attributes']:
                if c['nullable'] and c['name'] != 'reviewed_incident_id':
                    continue
                cols.append(c['name'])
                if c.get('enum'):
                    value = "'" + enums[c['enum']] + "'"
                elif c['name'] == 'content_hash':
                    value = "repeat('a',64)"
                else:
                    value = {'uuid': f"'{ONE}'", 'uuid[]': f"ARRAY['{ONE}'::uuid]", 'text': "'synthetic'",
                             'integer': '1', 'bigint': '1', 'boolean': 'TRUE', 'timestamptz': 'now()',
                             'jsonb': "'{}'::jsonb"}[c['type']]
                values.append(value)
            inserts.append(f"INSERT INTO {entity['schema']}.{entity['table']} ({','.join(cols)}) VALUES ({','.join(values)});")
        inserts.append(cls.connector_fixture())
        inserts.append(cls.correlation_fixture())
        result = cls.sql('BEGIN;\n' + '\n'.join(inserts) + '\nCOMMIT;')
        if result.returncode:
            raise RuntimeError(result.stderr)
        print(cls.sql("SELECT version(); SELECT extversion FROM pg_extension WHERE extname='vector';").stdout)

    @classmethod
    def correlation_fixture(cls):
        return f"""
INSERT INTO evidence.correlation_groups(id,scope_key,execution_id,incident_id,created_at,updated_at)
VALUES ('{ONE}','synthetic','{ONE}','{ONE}','2026-11-11 00:00:00+00','2026-11-11 00:00:00+00');
INSERT INTO evidence.correlated_contexts(id,incident_id,execution_id,evidence_ids,summary,correlation_id,created_at,group_id,signal_stage,signal_summary,signal_content)
VALUES ('{ONE}','{ONE}','{ONE}',ARRAY['{ONE}'::uuid],'synthetic','synthetic','2026-11-11 00:00:00+00','{ONE}',
 'BUILD','synthetic protected build summary','synthetic protected build content');
INSERT INTO evidence.correlation_receipts(scope_key,producer_key,message_id,evidence_id,correlation_id,context_id,input_fingerprint,created_at)
VALUES ('synthetic','synthetic','{ONE}','{ONE}','synthetic','{ONE}','v1:sha256:'||repeat('a',64),'2026-11-11 00:00:00+00');
"""

    @classmethod
    def connector_fixture(cls):
        return f"""
INSERT INTO ingestion.github_connections(id,tenant_id,entra_object_id,revision,created_at,updated_at)
VALUES ('{ONE}','{ONE}','{ONE}',0,now(),now());
INSERT INTO ingestion.github_connection_generations(id,connection_id,github_user_id,state,secret_object_ref,
 active_secret_version_ref,access_expires_at,refresh_expires_at,activated_at,revision,created_at,updated_at)
VALUES ('{ONE}','{ONE}','synthetic-user','ACTIVE','generation:{ONE}','synthetic-version',
 now()+interval '1 hour',now()+interval '1 day',now(),0,now(),now());
UPDATE ingestion.github_connections SET active_generation_id='{ONE}',revision=1 WHERE id='{ONE}';
INSERT INTO ingestion.github_connection_generations(id,connection_id,state,secret_object_ref,revision,created_at,updated_at)
VALUES ('{TWO}','{ONE}','PREPARING','generation:{TWO}',0,now(),now());
INSERT INTO ingestion.github_authorization_attempts(id,connection_id,tenant_id,entra_object_id,expected_connection_revision,
 expected_generation_id,target_generation_id,state_digest,expires_at,phase,pkce_secret_object_ref,
 pkce_secret_version_ref,pkce_cleanup_state,approved_return_ref,correlation_id,created_at,updated_at)
VALUES ('{ONE}','{ONE}','{ONE}','{ONE}',1,'{ONE}','{TWO}',decode('01','hex'),now()+interval '1 hour',
 'READY','pkce:{ONE}','synthetic-pkce-version','HELD','synthetic-return','synthetic-correlation',now(),now());
INSERT INTO ingestion.github_credential_operations(id,connection_id,generation_id,expected_connection_revision,
 expected_generation_revision,kind,phase,fence,created_at,updated_at)
VALUES ('{ONE}','{ONE}','{ONE}',1,0,'REFRESH','PENDING',0,now(),now());
"""

    def test_connector_membership_and_active_pointer_are_transactional(self):
        self.rejected(f"UPDATE ingestion.github_connections SET active_generation_id='{TWO}',revision=2")
        self.rejected("UPDATE ingestion.github_connection_generations SET state='INVALIDATED',revision=1 WHERE state='ACTIVE'")
        self.accepted("UPDATE ingestion.github_connection_generations SET state='INVALIDATED',revision=1 WHERE state='ACTIVE'; UPDATE ingestion.github_connections SET active_generation_id=NULL,revision=2")
        self.rejected("UPDATE ingestion.github_connections SET tenant_id='00000000-0000-0000-0000-000000000003',revision=2")

    def test_connector_attempt_and_remote_phase_require_claim_and_exact_versions(self):
        self.rejected("UPDATE ingestion.github_authorization_attempts SET phase='COMPLETED',consumed_at=now(),pkce_cleanup_state='PENDING'")
        self.accepted("UPDATE ingestion.github_authorization_attempts SET phase='CLAIMED',consumed_at=now(); UPDATE ingestion.github_authorization_attempts SET phase='COMPLETED',pkce_cleanup_state='PENDING'")
        claim=f"UPDATE ingestion.github_credential_operations SET phase='CLAIMED',owner_id='{ONE}',fence=1,started_at=now(),deadline_at=now()+interval '1 hour'"
        self.rejected(claim+"; UPDATE ingestion.github_credential_operations SET phase='VERSION_SAVED',candidate_secret_version_ref='synthetic-new-version'")
        self.accepted(claim+"; UPDATE ingestion.github_credential_operations SET phase='REQUEST_MAY_BE_IN_FLIGHT'; UPDATE ingestion.github_credential_operations SET phase='VERSION_SAVED',candidate_secret_version_ref='synthetic-new-version'")
        for invalid in ('latest',' LATEST ',' '):
            with self.subTest(version=invalid):
                self.rejected(f"UPDATE ingestion.github_connection_generations SET active_secret_version_ref='{invalid}',revision=1 WHERE state='ACTIVE'")
                self.rejected(f"UPDATE ingestion.github_credential_operations SET candidate_secret_version_ref='{invalid}'")

    def test_connector_secret_object_ownership_cannot_be_reused_or_cross_kind(self):
        third='00000000-0000-0000-0000-000000000003'
        for wrong in (f'generation:{ONE}',f'pkce:{ONE}'):
            self.rejected(f"INSERT INTO ingestion.github_connection_generations(id,connection_id,state,secret_object_ref,revision,created_at,updated_at) VALUES ('{third}','{ONE}','PREPARING','{wrong}',0,now(),now())")
        self.rejected(f"INSERT INTO ingestion.github_connection_generations(id,connection_id,state,secret_object_ref,revision,created_at,updated_at) VALUES ('{third}','{ONE}','PREPARING','generation:{third}',0,now(),now()); INSERT INTO ingestion.github_authorization_attempts SELECT '{TWO}',connection_id,tenant_id,entra_object_id,expected_connection_revision,expected_generation_id,'{third}',decode('02','hex'),expires_at,phase,consumed_at,pkce_secret_object_ref,pkce_secret_version_ref,pkce_cleanup_state,pkce_cleanup_result,approved_return_ref,correlation_id,created_at,updated_at FROM ingestion.github_authorization_attempts")

    def accepted(self, statement):
        result = self.sql('BEGIN; ' + statement + '; SET CONSTRAINTS ALL IMMEDIATE; ROLLBACK;')
        self.assertEqual(result.returncode, 0, result.stderr)

    def rejected(self, statement, code='23514', constraint=None):
        # Each psql session rolls its failed transaction back on disconnect.
        result = self.sql('BEGIN; ' + statement + '; SET CONSTRAINTS ALL IMMEDIATE; ROLLBACK;')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(code, result.stderr)
        if constraint is not None:
            self.assertIn(constraint, result.stderr)

    @staticmethod
    def capture_fixture():
        return """
INSERT INTO ingestion.capture_receipts
(id,capture_domain,tenant_id,source,body_digest,app_id,account_id,installation_id,repository_id,workflow_id,run_id,
 run_attempt,scope_revision,correlation_id,snapshot_message_id,evidence_message_id,phase,revision,claim_fence,created_at,updated_at,replay_until)
VALUES ('00000000-0000-4000-8000-000000000010','synthetic-domain','00000000-0000-4000-8000-000000000011',
 'github',repeat('a',64),'1','2','3','4','5','6',1,'scope-1','synthetic-correlation',
 '00000000-0000-4000-8000-000000000012','00000000-0000-4000-8000-000000000013',
 'ACCEPTED',0,0,'2026-11-08 00:00:00+00','2026-11-08 00:00:00+00','2026-11-10 00:00:00+00');
INSERT INTO ingestion.capture_delivery_aliases(id,capture_domain,source,delivery_id,receipt_id,created_at)
VALUES ('00000000-0000-4000-8000-000000000014','synthetic-domain','github','synthetic-delivery',
 '00000000-0000-4000-8000-000000000010','2026-11-08 00:00:00+00');
UPDATE ingestion.capture_receipts SET revision=1,claim_fence=1,claim_owner='00000000-0000-4000-8000-000000000015',
 lease_until='2026-11-08 00:01:00+00',updated_at='2026-11-08 00:00:01+00';
INSERT INTO ingestion.capture_observations
(id,capture_domain,source,observation_key,protected_content_digest,origin_receipt_id,repository_id,workflow_id,run_id,
 run_attempt,observed_at,observed_at_submicro,source_updated_at,source_updated_at_submicro,normalizer_version,
 protection_policy_version,correlation_id,required_output_count,created_at)
VALUES ('00000000-0000-4000-8000-000000000016','synthetic-domain','github',repeat('d',64),repeat('b',64),
 '00000000-0000-4000-8000-000000000010','4','5','6',1,'2026-11-08 00:00:00.123456+00',789,
 '2026-11-08 00:00:00.999999+00',999,'v1','v1','synthetic-correlation',1,'2026-11-08 00:00:02+00');
INSERT INTO ingestion.publication_outputs
(id,observation_id,event_type,schema_major,payload,payload_digest,phase,revision,claim_fence,attempt_count,
 payload_recover_until,created_at,updated_at)
VALUES ('00000000-0000-4000-8000-000000000012','00000000-0000-4000-8000-000000000016',
 'execution.snapshot',1,decode('7b7d','hex'),repeat('c',64),'PENDING',0,0,0,
 '2026-11-09 00:00:00+00','2026-11-08 00:00:02+00','2026-11-08 00:00:02+00');
UPDATE ingestion.capture_receipts SET phase='PREPARED',revision=2,claim_owner=NULL,lease_until=NULL,
 observation_id='00000000-0000-4000-8000-000000000016',prepared_at='2026-11-08 00:00:02+00',updated_at='2026-11-08 00:00:02+00';
"""

    @staticmethod
    def output_claim():
        return """UPDATE ingestion.publication_outputs SET phase='CLAIMED',revision=1,claim_fence=1,attempt_count=1,
 claim_owner='00000000-0000-4000-8000-000000000015',lease_until='2026-11-08 00:01:00+00',
 last_attempt_at='2026-11-08 00:00:03+00',updated_at='2026-11-08 00:00:03+00';"""

    def test_capture_closed_plan_reserved_ids_and_source_instants(self):
        fixture=self.capture_fixture()
        self.accepted(fixture)
        self.rejected(fixture.replace("repeat('d',64)", "'opaque-key'"), constraint='capture_observations_observation_key_ck')
        self.rejected(fixture.replace("'synthetic-correlation',1,'2026-11-08 00:00:02+00'", "'synthetic-correlation',2,'2026-11-08 00:00:02+00'"))
        self.rejected(fixture.replace("00:00:00.123456+00',789", "00:00:00.123456+00',1000"))
        self.rejected(fixture + "UPDATE ingestion.capture_receipts SET phase='PUBLISHED',published_at='2026-11-08 00:00:03+00',revision=3,updated_at='2026-11-08 00:00:03+00'")
        self.rejected(fixture.replace("'execution.snapshot',1,decode", "'protected_workflow_evidence',2,decode"))

    def test_capture_context_alias_membership_and_append_only_guards(self):
        fixture=self.capture_fixture()
        for statement in ("UPDATE ingestion.capture_observations SET correlation_id='changed'",
                          "UPDATE ingestion.capture_delivery_aliases SET delivery_id='changed'",
                          "DELETE FROM ingestion.publication_outputs", "SET CONSTRAINTS ALL IMMEDIATE; TRUNCATE ingestion.capture_receipts CASCADE",
                          "UPDATE ingestion.capture_receipts SET tenant_id='00000000-0000-4000-8000-000000000099',revision=3"):
            with self.subTest(statement=statement): self.rejected(fixture+statement)
        self.rejected(fixture.replace("'synthetic-domain','github','synthetic-delivery'", "'other-domain','github','synthetic-delivery'"), '23503')
        self.rejected(fixture.replace("'4','5','6',1,'2026-11-08", "'9','5','6',1,'2026-11-08"))

    def test_capture_blocking_cannot_bypass_preparation_and_acceptance_horizon(self):
        fixture=self.capture_fixture()
        bypass=fixture.replace("SET phase='PREPARED',revision=2", "SET phase='BLOCKED',blocked_reason='SYNTHETIC',revision=2")
        self.rejected(bypass, constraint='capture_receipts_association_ck')
        acceptance=fixture[:fixture.index('INSERT INTO ingestion.capture_delivery_aliases')]
        self.rejected(acceptance+"UPDATE ingestion.capture_receipts SET replay_until='2026-11-11 00:00:00+00',revision=1,updated_at='2026-11-08 00:00:01+00'", constraint='capture_receipts_replay_horizon_ck')
        self.rejected(acceptance.replace("'2026-11-10 00:00:00+00'", 'NULL'), '23502')
        self.rejected(acceptance.replace("'2026-11-10 00:00:00+00'", "'2026-11-07 00:00:00+00'"), constraint='capture_receipts_lifecycle_times_ck')

    def test_capture_equivalent_receipt_preserves_origin_context_and_rejects_other_tenant(self):
        fixture=self.capture_fixture()
        duplicate=fixture[:fixture.index('INSERT INTO ingestion.capture_delivery_aliases')]
        for old,new in [('000000000010','000000000020'),('000000000012','000000000022'),
                        ('000000000013','000000000023'),("repeat('a',64)","repeat('d',64)"),
                        ('synthetic-correlation','other-correlation'),('scope-1','scope-2')]:
            duplicate=duplicate.replace(old,new)
        prepare="""
UPDATE ingestion.capture_receipts SET revision=1,claim_fence=1,claim_owner='00000000-0000-4000-8000-000000000015',
 lease_until='2026-11-08 00:01:00+00',updated_at='2026-11-08 00:00:03+00'
 WHERE id='00000000-0000-4000-8000-000000000020';
UPDATE ingestion.capture_receipts SET phase='PREPARED',revision=2,claim_owner=NULL,lease_until=NULL,
 observation_id='00000000-0000-4000-8000-000000000016',prepared_at='2026-11-08 00:00:04+00',updated_at='2026-11-08 00:00:04+00'
 WHERE id='00000000-0000-4000-8000-000000000020';
"""
        self.accepted(fixture+duplicate+prepare)
        for old,new in [('000000000011','000000000099'),("'1','2','3','4','5','6'","'1','2','9','4','5','6'")]:
            with self.subTest(context=old): self.rejected(fixture+duplicate.replace(old,new)+prepare)

    def test_capture_output_fences_retry_and_confirmed_purge(self):
        fixture=self.capture_fixture()+self.output_claim()
        self.rejected(fixture+"UPDATE ingestion.publication_outputs SET phase='CONFIRMED',confirmed_at='2026-11-08 00:02:00+00',claim_owner=NULL,lease_until=NULL,revision=2,updated_at='2026-11-08 00:02:00+00'")
        self.rejected(fixture+"UPDATE ingestion.publication_outputs SET revision=2,claim_fence=2,attempt_count=2,last_attempt_at='2026-11-08 00:00:04+00',updated_at='2026-11-08 00:00:04+00'")
        self.accepted(fixture+"UPDATE ingestion.publication_outputs SET phase='PENDING',claim_owner=NULL,lease_until=NULL,revision=2,next_attempt_at='2026-11-08 00:00:05+00',updated_at='2026-11-08 00:00:04+00'")
        confirmed=fixture+"UPDATE ingestion.publication_outputs SET phase='CONFIRMED',claim_owner=NULL,lease_until=NULL,revision=2,confirmed_at='2026-11-08 00:00:04+00',updated_at='2026-11-08 00:00:04+00';"
        self.accepted(confirmed+"UPDATE ingestion.capture_receipts SET phase='PUBLISHED',revision=3,published_at='2026-11-08 00:00:04+00',updated_at='2026-11-08 00:00:04+00'")
        self.rejected(confirmed+"UPDATE ingestion.publication_outputs SET payload=decode('ff','hex'),revision=3")
        self.rejected(confirmed+"UPDATE ingestion.publication_outputs SET payload=NULL,payload_removed_at='2026-11-08 01:00:00+00',updated_at='2026-11-08 01:00:00+00',revision=3")
        purged=confirmed+"UPDATE ingestion.publication_outputs SET payload=NULL,payload_removed_at='2026-11-09 01:00:00+00',updated_at='2026-11-09 01:00:00+00',revision=3;"
        self.accepted(purged)
        self.rejected(purged+"UPDATE ingestion.publication_outputs SET payload=decode('7b7d','hex'),payload_removed_at=NULL,revision=4")

    @staticmethod
    def next_correlation_snapshot():
        return f"""
INSERT INTO evidence.correlated_contexts(id,incident_id,execution_id,evidence_ids,summary,correlation_id,created_at,group_id,signal_stage,signal_summary,signal_content)
VALUES ('{TWO}','{ONE}','{ONE}',ARRAY['{ONE}'::uuid,'{TWO}'::uuid],'synthetic next','synthetic next',now(),'{ONE}',
 'TESTING','synthetic protected test summary','synthetic protected test content');
INSERT INTO evidence.correlation_receipts(scope_key,producer_key,message_id,evidence_id,correlation_id,context_id,input_fingerprint,created_at)
VALUES ('synthetic','synthetic','{TWO}','{TWO}','synthetic next','{TWO}','v1:sha256:'||repeat('b',64),now());
"""

    def test_correlation_required_columns_keep_native_not_null_rejection(self):
        model = yaml.safe_load((ROOT / 'model/domain.yml').read_text())
        for entity in model['entities']:
            if entity['table'] not in ('correlation_groups', 'correlated_contexts', 'correlation_receipts'):
                continue
            columns = [a['name'] for a in entity['attributes']]
            for attr in entity['attributes']:
                if attr['nullable']:
                    continue
                with self.subTest(table=entity['table'], column=attr['name']):
                    values = ['NULL' if c == attr['name'] else c for c in columns]
                    self.rejected(f"INSERT INTO evidence.{entity['table']} ({','.join(columns)}) "
                                  f"SELECT {','.join(values)} FROM evidence.{entity['table']}", '23502')

    def test_correlation_chain_requires_confirmed_predecessor_and_atomic_receipt(self):
        next_snapshot = self.next_correlation_snapshot()
        confirm = f"UPDATE evidence.correlation_groups SET confirmed_context_id='{ONE}',updated_at=now();"
        self.rejected(next_snapshot, constraint='correlated_contexts_chain_ck')
        self.accepted(confirm + next_snapshot)
        self.rejected(confirm + next_snapshot.split('INSERT INTO evidence.correlation_receipts')[0],
                      constraint='correlated_contexts_receipt_ck')
        self.rejected(confirm + next_snapshot.replace(f"ARRAY['{ONE}'::uuid,'{TWO}'::uuid]", f"ARRAY['{TWO}'::uuid]"),
                      constraint='correlated_contexts_chain_ck')
        self.rejected(confirm + next_snapshot.replace(f"ARRAY['{ONE}'::uuid,'{TWO}'::uuid]",
                      f"ARRAY['{ONE}'::uuid,'{TWO}'::uuid,'00000000-0000-0000-0000-000000000003'::uuid]"),
                      constraint='correlated_contexts_chain_ck')

    def test_correlation_signal_is_required_nonblank_and_immutable(self):
        confirm = f"UPDATE evidence.correlation_groups SET confirmed_context_id='{ONE}',updated_at=now();"
        snapshot = self.next_correlation_snapshot()
        for stage in ('BUILD', 'TESTING', 'QUALITY_GATE', 'DEPLOYMENT', 'CONTAINER', 'INFRASTRUCTURE'):
            with self.subTest(stage=stage):
                self.accepted(confirm + snapshot.replace("'TESTING'", f"'{stage}'"))
        for stage in ("'COMPILE'", "'testing'", "''", "' '", "E'\\t\\n'"):
            with self.subTest(stage=stage):
                self.rejected(confirm + snapshot.replace("'TESTING'", stage),
                              constraint='correlated_contexts_signal_stage_ck')
        for field, original in (('signal_summary', "'synthetic protected test summary'"),
                                ('signal_content', "'synthetic protected test content'")):
            for blank in ("''", "' '", "E'\\t\\n'"):
                with self.subTest(field=field, blank=blank):
                    self.rejected(confirm + snapshot.replace(original, blank),
                                  constraint=f'correlated_contexts_{field}_ck')
        for field, value in (('signal_stage', 'TESTING'), ('signal_summary', 'changed summary'),
                             ('signal_content', 'changed protected content')):
            self.rejected(f"UPDATE evidence.correlated_contexts SET {field}='{value}'",
                          constraint='correlation_immutable_ck')

    def test_correlation_snapshot_sets_and_immutable_history(self):
        confirm = f"UPDATE evidence.correlation_groups SET confirmed_context_id='{ONE}',updated_at=now();"
        for values in ("ARRAY[]::uuid[]", f"ARRAY['{ONE}'::uuid,'{ONE}'::uuid]",
                       f"ARRAY['{ONE}'::uuid,NULL]", f"ARRAY[['{ONE}'::uuid,'{TWO}'::uuid]]",
                       f"'[0:1]={{{ONE},{TWO}}}'::uuid[]"):
            with self.subTest(values=values):
                statement = self.next_correlation_snapshot().replace(f"ARRAY['{ONE}'::uuid,'{TWO}'::uuid]", values)
                self.rejected(confirm + statement, constraint='correlated_contexts_evidence_set_ck')
        for table in ('correlated_contexts', 'correlation_receipts'):
            for op in (f'UPDATE evidence.{table} SET created_at=now()', f'DELETE FROM evidence.{table}',
                       f'TRUNCATE evidence.{table} CASCADE'):
                with self.subTest(op=op): self.rejected(op, constraint='correlation_immutable_ck')
        for op in ('DELETE FROM evidence.correlation_groups', 'TRUNCATE evidence.correlation_groups CASCADE'):
            self.rejected(op, constraint='correlation_immutable_ck')

    def test_correlation_receipts_preserve_source_scope_membership_and_original_context(self):
        receipt = f"""INSERT INTO evidence.correlation_receipts
(scope_key,producer_key,message_id,evidence_id,correlation_id,context_id,input_fingerprint,created_at)
VALUES ('synthetic','another-producer','{TWO}','{ONE}','original-source','{ONE}',
 'v1:sha256:'||repeat('c',64),now());"""
        self.accepted(receipt)  # another message/producer reuses the exact original member context
        self.rejected(receipt.replace("'synthetic','another-producer'", "'other-scope','another-producer'"),
                      constraint='correlation_receipts_membership_ck')
        self.rejected(receipt.replace(f"'{TWO}','{ONE}','original-source'", f"'{TWO}','{TWO}','original-source'"),
                      constraint='correlation_receipts_membership_ck')
        self.rejected(receipt.replace("'v1:sha256:'||repeat('c',64)", "repeat('c',64)"),
                      constraint='correlation_receipts_fingerprint_ck')
        confirm = f"UPDATE evidence.correlation_groups SET confirmed_context_id='{ONE}',updated_at=now();"
        later_receipt = receipt.replace(f"'{TWO}','{ONE}','original-source','{ONE}'",
                                       f"'00000000-0000-0000-0000-000000000003','{ONE}','original-source','{TWO}'")
        self.rejected(confirm + self.next_correlation_snapshot() + later_receipt,
                      constraint='correlation_receipts_original_context_ck')
        duplicate = receipt.replace("another-producer", "synthetic").replace(f"'{TWO}','{ONE}'", f"'{ONE}','{ONE}'")
        self.rejected(duplicate, '23505')

    def test_correlation_group_identity_and_confirmation_only_advance_adjacent(self):
        confirm = f"UPDATE evidence.correlation_groups SET confirmed_context_id='{ONE}',updated_at=now();"
        self.accepted(confirm)
        self.accepted(confirm + confirm)  # repeated confirmation does not advance or change timestamp
        self.rejected('UPDATE evidence.correlation_groups SET updated_at=now()', constraint='correlation_groups_updated_ck')
        self.rejected(f"UPDATE evidence.correlation_groups SET scope_key='other',confirmed_context_id='{ONE}',updated_at=now()",
                      constraint='correlation_groups_identity_ck')
        for column in ('id', 'execution_id', 'incident_id'):
            self.rejected(f"UPDATE evidence.correlation_groups SET {column}='{TWO}'",
                          constraint='correlation_groups_identity_ck')
        self.rejected("UPDATE evidence.correlation_groups SET created_at=created_at-interval '1 second'",
                      constraint='correlation_groups_identity_ck')
        columns = ['scope_key', 'producer_key', 'message_id', 'evidence_id', 'correlation_id',
                   'context_id', 'input_fingerprint', 'created_at']
        for column in ('scope_key', 'producer_key', 'correlation_id'):
            for blank in ("' '", "E'\\t\\n'"):
                values = [blank if c == column else c for c in columns]
                self.rejected('INSERT INTO evidence.correlation_receipts SELECT ' + ','.join(values) +
                              ' FROM evidence.correlation_receipts')
        self.rejected(confirm + 'UPDATE evidence.correlation_groups SET confirmed_context_id=NULL,updated_at=now()',
                      constraint='correlation_groups_confirmation_ck')
        self.accepted(confirm + self.next_correlation_snapshot() +
                      f"UPDATE evidence.correlation_groups SET confirmed_context_id='{TWO}',updated_at=now()")
        self.rejected(confirm + self.next_correlation_snapshot() +
                      f"UPDATE evidence.correlation_groups SET confirmed_context_id='{TWO}',updated_at=now();" + confirm,
                      constraint='correlation_groups_confirmation_ck')
        foreign_group = f"""INSERT INTO evidence.correlation_groups(id,scope_key,execution_id,incident_id,created_at,updated_at)
VALUES ('{TWO}','other-scope','{ONE}','{ONE}',now(),now());"""
        self.rejected(foreign_group + f"UPDATE evidence.correlation_groups SET confirmed_context_id='{ONE}' WHERE id='{TWO}'",
                      constraint='correlation_groups_confirmation_ck')

    def test_valid_origin_and_verification(self):
        self.accepted(f"INSERT INTO ops.pipeline_executions SELECT '{TWO}', pipeline_id, 'other-run', run_attempt, branch, commit_sha, external_status, external_conclusion, failed, started_at, completed_at, correlation_id, created_at FROM ops.pipeline_executions; INSERT INTO ops.incident_runs SELECT '{TWO}', incident_id, '{TWO}', 'VERIFICATION', correlation_id, created_at FROM ops.incident_runs")
        self.accepted('UPDATE ops.pipeline_executions SET failed=TRUE')

    def test_origin_required_failed_and_same_pipeline(self):
        self.rejected('DELETE FROM ops.incident_runs')
        self.rejected('UPDATE ops.pipeline_executions SET failed=FALSE')
        self.rejected(f"INSERT INTO ops.pipelines SELECT '{TWO}', repository_id, 'other', workflow_name, workflow_file, environment, criticality, monitoring_status, responsible_team_ref, responsible_team_name_snapshot, created_at FROM ops.pipelines; UPDATE ops.incidents SET pipeline_id='{TWO}'")

    def test_append_only(self):
        for statement in ('UPDATE diagnosis.diagnoses SET version=2', 'DELETE FROM diagnosis.diagnoses', 'TRUNCATE diagnosis.diagnoses CASCADE', 'TRUNCATE ops.incident_runs'):
            with self.subTest(statement=statement):
                self.rejected(statement)

    def test_checks_and_unique_constraints(self):
        self.rejected('UPDATE ops.pipeline_executions SET run_attempt=0')
        self.rejected('UPDATE knowledge.knowledge_chunks SET chunk_index=-1')
        self.rejected("UPDATE evidence.evidence_items SET size_bytes=-1")
        self.rejected("UPDATE diagnosis.human_reviews SET decision='PENDING'", '22P02')
        self.rejected("UPDATE knowledge.knowledge_documents SET provenance=' '")
        self.rejected("UPDATE diagnosis.human_reviews SET decision='CORRECTED', actual_cause=NULL")
        self.rejected(f"INSERT INTO diagnosis.diagnoses SELECT '{TWO}', incident_id, version, status, probable_cause, explanation, limitations, confidence, diagnosis_ready_at, correlation_id, created_at FROM diagnosis.diagnoses", '23505')
        self.rejected(f"INSERT INTO diagnosis.diagnoses SELECT '{TWO}', incident_id, 2, 'DIAGNOSIS_READY', NULL, explanation, limitations, confidence, NULL, correlation_id, created_at FROM diagnosis.diagnoses")

    def test_logical_refs_are_not_physical_foreign_keys(self):
        self.accepted(f"UPDATE evidence.evidence_items SET incident_id='{TWO}'")
        self.rejected(f"UPDATE knowledge.knowledge_chunks SET document_id='{TWO}'", '23503')

    def test_open_vector_and_review_correction(self):
        self.accepted("UPDATE knowledge.knowledge_chunks SET embedding='[1,2,3]'")
        self.accepted("UPDATE diagnosis.human_reviews SET decision='CORRECTED', actual_cause='synthetic correction'")


if __name__ == '__main__':
    unittest.main(verbosity=2)
