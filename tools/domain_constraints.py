"""Current DD-003/005/006/007/009/013 constraints, not a SQL parser.

An authorized domain evolution updates these contracts and regression tests.
Constraint names are presentation details; compare expressions and column sets.
"""
import re

REQUIRED_UNIQUES = {
    'pipelines': [('repository_id', 'github_workflow_id')],
    'pipeline_executions': [('pipeline_id', 'github_run_id', 'run_attempt')],
    'execution_stages': [('execution_id', 'stage')],
    'incident_runs': [('incident_id', 'execution_id')],
    'pipeline_access_grants': [('pipeline_id', 'principal_ref', 'capability')],
    'diagnoses': [('incident_id', 'version')],
    'diagnosis_evidence_links': [('diagnosis_id', 'evidence_id')],
    'diagnosis_source_links': [('diagnosis_id', 'knowledge_chunk_id')],
    'knowledge_chunks': [('document_id', 'chunk_index')],
}
REQUIRED_CHECKS = {
    'pipeline_executions': ['run_attempt > 0'],
    'evidence_items': ['size_bytes IS NULL OR size_bytes >= 0', '(storage_container IS NULL) = (blob_object_key IS NULL)'],
    'diagnoses': ['version > 0', "status <> 'DIAGNOSIS_READY' OR (probable_cause IS NOT NULL AND btrim(probable_cause) <> '' AND diagnosis_ready_at IS NOT NULL)"],
    'human_reviews': ["decision <> 'CORRECTED' OR (actual_cause IS NOT NULL AND btrim(actual_cause) <> '')"],
    'knowledge_documents': ["btrim(provenance) <> ''", "corpus_kind <> 'reviewed_incidents' OR reviewed_incident_id IS NOT NULL"],
    'knowledge_chunks': ['chunk_index >= 0', "btrim(provenance) <> ''"],
}


def normalize(expression):
    # Do not fold literals: 'corrected' is not the enum 'CORRECTED'.
    return re.sub(r'\s+', ' ', expression).strip()


def validate_constraints(domain):
    errors = []
    for entity in domain['entities']:
        name = entity.get('table')
        uniques = entity.get('unique_constraints', [])
        actual = {frozenset(c.get('columns', [])) for c in uniques}
        for required in REQUIRED_UNIQUES.get(name, []):
            if frozenset(required) not in actual:
                errors.append(f'{name}: missing approved uniqueness {required}')
        checks = entity.get('checks', [])
        actual_checks = {normalize(c.get('expression', '')) for c in checks}
        for required in REQUIRED_CHECKS.get(name, []):
            if normalize(required) not in actual_checks:
                errors.append(f'{name}: missing approved CHECK {required}')
        constraint_names = set()
        for c in [*uniques, *checks]:
            cid = c.get('name', '')
            if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', cid) or cid in constraint_names:
                errors.append(f'{name}: invalid/duplicate constraint name {cid!r}')
            constraint_names.add(cid)
        for c in uniques:
            columns = c.get('columns', [])
            if len(set(columns)) != len(columns):
                errors.append(f'{name}: duplicate unique constraint columns')
        for c in checks:
            if not c.get('expression', '').strip():
                errors.append(f'{name}: empty CHECK expression')
    questions = domain['open_questions']
    if len({q.get('id') for q in questions}) != len(questions):
        errors.append('Duplicate open question ID')
    if len({q.get('topic') for q in questions}) != len(questions):
        errors.append('Duplicate open question topic')
    return errors
