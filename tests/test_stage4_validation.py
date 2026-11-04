"""Mutate copies of the approved baseline; never rewrite normative models."""
from copy import deepcopy
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from architecture_policy import validate_policy
from domain_validation import validate_domain
from verify_artifacts import compare


class PolicyRegressionTests(unittest.TestCase):
    def setUp(self):
        self.arch = yaml.safe_load((ROOT / 'model/architecture.yml').read_text())
        self.domain = yaml.safe_load((ROOT / 'model/domain.yml').read_text())

    def test_current_policy_passes(self):
        self.assertEqual(validate_policy(self.arch), [])
        self.assertEqual(validate_domain(self.domain, self.arch), [])

    def test_github_auth_and_workflow_publication(self):
        for auth in (self.arch['deployment']['github_authentication'],
                     next(e for e in self.arch['elements'] if e['id'] == 'github')['authentication']):
            original = auth['access']
            auth['access'] = 'write'
            self.assertTrue(validate_policy(self.arch))
            auth['access'] = original
        output = next(o for o in self.arch['outputs'] if o.get('publication_target') == 'github_actions')
        output['published_by'] = 'recommendation_service'
        self.assertTrue(any('workflow-owned' in e for e in validate_policy(self.arch)))

    def test_all_alternate_ingestion_paths_are_rejected_even_with_safe_route(self):
        for middle in ('azure_service_bus', 'new_relay', 'api_management'):
            arch = deepcopy(self.arch)
            arch['relationships'] += [
                {'id': 'unsafe1', 'from': 'observability_sources', 'to': middle},
                {'id': 'unsafe2', 'from': middle, 'to': 'nlp_log_processor'}]
            self.assertTrue(any('bypasses ingestion' in e for e in validate_policy(arch)))

    def test_missing_privacy_and_raw_llm_contract_rejected(self):
        for ident, field, value in (
            ('ingestion_normalization_service', 'capabilities', []),
            ('pretrained_llm_diagnostic_service', 'input_contract', ['raw_logs']),
            ('rag_retrieval', 'provenance_required', False),
            ('rag_retrieval', 'knowledge_scope', ['evaluation']),
        ):
            arch = deepcopy(self.arch)
            next(e for e in arch['elements'] if e['id'] == ident)[field] = value
            self.assertTrue(validate_policy(arch), (ident, field))

    def test_each_approved_check_and_unique_cannot_disappear_or_be_weakened(self):
        for index, entity in enumerate(self.domain['entities']):
            for field in ('checks', 'unique_constraints'):
                for number in range(len(entity.get(field, []))):
                    for weaken in (False, True):
                        domain = deepcopy(self.domain)
                        constraints = domain['entities'][index][field]
                        if not weaken:
                            constraints.pop(number)
                        elif field == 'checks':
                            constraints[number]['expression'] = 'TRUE'
                        else:
                            constraints[number]['columns'] = ['id']
                        with self.subTest(table=entity['table'], field=field, number=number, weaken=weaken):
                            self.assertTrue(validate_domain(domain, self.arch))

    def test_duplicate_questions_and_relationships_rejected(self):
        for field in ('open_questions', 'relationships'):
            domain = deepcopy(self.domain)
            entry = deepcopy(domain[field][0])
            if field == 'relationships':
                entry['id'] = 'different_id_same_reference'
            domain[field].append(entry)
            self.assertTrue(validate_domain(domain, self.arch))

    def test_check_names_can_change_without_changing_policy(self):
        for entity in self.domain['entities']:
            for check in entity.get('checks', []):
                check['name'] += '_renamed'
        self.assertEqual(validate_domain(self.domain, self.arch), [])


class EnvironmentChecksTests(unittest.TestCase):
    def test_missing_tools_return_failure_and_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            env = {**os.environ, 'PYTHON': '/missing/python', 'TMPDIR': directory}
            run = subprocess.run(['bash', str(ROOT / 'tools/check_env.sh')], env=env,
                                 capture_output=True, text=True, timeout=30)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn('Environment checks failed', run.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_artifact_comparison_rejects_missing_and_changed_files(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / 'a', Path(directory) / 'b'
            a.mkdir(); b.mkdir()
            (a / 'x').write_text('source')
            self.assertEqual(compare(a, b, {'x'}), ['x'])
            (b / 'x').write_text('stale')
            self.assertEqual(compare(a, b, {'x'}), ['x'])
            (b / 'x').write_text('source')
            self.assertEqual(compare(a, b, {'x'}), [])


if __name__ == '__main__':
    unittest.main()
