"""DD-020 source/export contracts; these checks do not simulate provider authorization."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools/generators'))
from domain_validation import validate_domain
from to_dbml import generate_dbml
from to_dictionary import generate_dictionary
from to_er_d2 import generate_er
from to_sql import generate_extras, validate_export


class ConnectorGenerationTests(unittest.TestCase):
    def setUp(self):
        self.model=yaml.safe_load((ROOT/'model/domain.yml').read_text())
        self.architecture=yaml.safe_load((ROOT/'model/architecture.yml').read_text())

    def entity(self,name):
        return next(e for e in self.model['entities'] if e['table']==name)

    def test_connector_owned_metadata_excludes_reverse_uniqueness_and_secret_values(self):
        self.assertEqual(validate_domain(self.model,self.architecture),[])
        tables=[e for e in self.model['entities'] if e['schema']=='ingestion' and e['table'].startswith('github_')]
        self.assertEqual(len(tables),4)
        self.assertTrue(all(e['owner_container']=='ingestion_normalization_service' for e in tables))
        self.entity('github_connection_generations')['unique_constraints'].append({'name':'unapproved_reverse_uq','columns':['github_user_id']})
        self.assertTrue(any('reverse uniqueness' in e for e in validate_domain(self.model,self.architecture)))

    def test_composite_membership_and_unfinished_refresh_cannot_disappear(self):
        for field in ['foreign_keys','partial_unique_constraints']:
            with self.subTest(field=field):
                entity=self.entity('github_credential_operations'); old=entity[field];entity[field]=[]
                self.assertTrue(any('missing approved' in e for e in validate_domain(self.model,self.architecture)))
                entity[field]=old

    def test_composite_fk_rejects_cross_schema_wrong_type_and_missing_target_key(self):
        for mutation in ['schema','type','key']:
            with self.subTest(mutation=mutation):
                model=deepcopy(self.model);conn=next(e for e in model['entities'] if e['table']=='github_connections')
                if mutation=='schema':conn['foreign_keys'][0]['references']['table']='ops.repositories'
                elif mutation=='type':next(c for c in conn['attributes'] if c['name']=='active_generation_id')['type']='text'
                else:next(e for e in model['entities'] if e['table']=='github_connection_generations')['unique_constraints']=[]
                self.assertTrue(validate_domain(model,self.architecture))

    def test_exports_preserve_membership_partial_deferred_and_exact_version_rules(self):
        dbml=generate_dbml(self.model);extras=generate_extras(self.model)
        dictionary=generate_dictionary(self.model);er=generate_er(self.model)
        self.assertIn('(connection_id, tenant_id, entra_object_id)',dbml)
        self.assertIn('ALTER CONSTRAINT github_attempts_identity_fk DEFERRABLE INITIALLY DEFERRED',extras)
        self.assertIn("WHERE kind = 'REFRESH' AND phase <> 'COMPLETED'",extras)
        self.assertIn('CREATE CONSTRAINT TRIGGER github_connections_active_consistency',extras)
        self.assertIn('github_active_consistency_ck',extras)
        self.assertIn('FOR UPDATE',extras)
        self.assertIn('Unicidad parcial',dictionary)
        self.assertIn('FK compuesta',dictionary)
        self.assertIn('composite FK deferred: connection_id, tenant_id, entra_object_id',er)
        self.assertIn('partial UQ; see dictionary',er)
        self.assertIn('github_credential_operations_exact_versions_ck',dbml)
        self.assertIn("lower(btrim(candidate_secret_version_ref)) <> 'latest'",dbml)

    def test_export_cannot_silently_omit_composite_fk(self):
        lines=[]
        for e in self.model['entities']:
            lines.append(f'CREATE TABLE "{e["schema"]}"."{e["table"]}" (id uuid);')
            pk = [a['name'] for a in e['attributes'] if a['pk']]
            if len(pk) > 1:
                lines.append('PRIMARY KEY (' + ', '.join(f'"{c}"' for c in pk) + ')')
            lines.extend(f'CONSTRAINT "{c["name"]}" CHECK (true)' for c in e.get('checks',[]))
            lines.extend(f'CREATE UNIQUE INDEX "{u["name"]}"' for u in e.get('unique_constraints',[]))
            lines.extend(f'ADD CONSTRAINT "{f["name"]}" FOREIGN KEY' for f in e.get('foreign_keys',[]))
        sql='\n'.join(lines);validate_export(sql,self.model)
        with self.assertRaisesRegex(ValueError,'omitted composite FK'):
            validate_export(sql.replace('ADD CONSTRAINT "github_attempts_identity_fk" FOREIGN KEY','ADD CONSTRAINT "lost" FOREIGN KEY'),self.model)
