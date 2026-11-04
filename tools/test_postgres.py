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
        result = cls.sql('BEGIN;\n' + '\n'.join(inserts) + '\nCOMMIT;')
        if result.returncode:
            raise RuntimeError(result.stderr)
        print(cls.sql("SELECT version(); SELECT extversion FROM pg_extension WHERE extname='vector';").stdout)

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
        self.rejected("UPDATE evidence.evidence_items SET storage_container='synthetic', blob_object_key=NULL")
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
