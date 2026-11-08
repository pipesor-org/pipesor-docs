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
            ready = subprocess.run(['docker', 'exec', cls.container, 'pg_isready', '-U', 'postgres'], capture_output=True)
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
            if entity['schema'] == 'ingestion':
                continue  # DD-020 needs coherent lifecycle metadata, not generic scalar values.
            cols, values = [], []
            for c in entity['attributes']:
                if c['nullable'] and c['name'] != 'reviewed_incident_id':
                    continue
                cols.append(c['name'])
                if c.get('enum'):
                    value = "'" + enums[c['enum']] + "'"
                else:
                    value = {'uuid': f"'{ONE}'", 'uuid[]': f"ARRAY['{ONE}'::uuid]", 'text': "'synthetic'",
                             'integer': '1', 'bigint': '1', 'boolean': 'TRUE', 'timestamptz': 'now()',
                             'jsonb': "'{}'::jsonb"}[c['type']]
                values.append(value)
            inserts.append(f"INSERT INTO {entity['schema']}.{entity['table']} ({','.join(cols)}) VALUES ({','.join(values)});")
        inserts.append(cls.connector_fixture())
        result = cls.sql('BEGIN;\n' + '\n'.join(inserts) + '\nCOMMIT;')
        if result.returncode:
            raise RuntimeError(result.stderr)
        print(cls.sql("SELECT version(); SELECT extversion FROM pg_extension WHERE extname='vector';").stdout)

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

    def rejected(self, statement, code='23514'):
        # Each psql session rolls its failed transaction back on disconnect.
        result = self.sql('BEGIN; ' + statement + '; SET CONSTRAINTS ALL IMMEDIATE; ROLLBACK;')
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(code, result.stderr)

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
