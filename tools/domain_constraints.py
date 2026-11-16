"""Current DD-003/005/006/007/009/013 constraints, not a SQL parser.

An authorized domain evolution updates these contracts and regression tests.
Constraint names are presentation details; compare expressions and column sets.
"""
import re

REQUIRED_UNIQUES = {
    'correlation_groups': [('scope_key', 'execution_id', 'incident_id'), ('id', 'incident_id', 'execution_id')],
    'correlated_contexts': [('group_id', 'id')],
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
REQUIRED_REFERENCES = {
    'evidence.correlation_groups.execution_id': ('logical_ref', 'ops.pipeline_executions.id'),
    'evidence.correlation_groups.incident_id': ('logical_ref', 'ops.incidents.id'),
    'evidence.correlation_receipts.evidence_id': ('logical_ref', 'evidence.evidence_items.id'),
    'evidence.correlation_receipts.context_id': ('fk', 'evidence.correlated_contexts.id'),
    'ops.pipelines.repository_id': ('fk', 'ops.repositories.id'),
    'ops.pipeline_executions.pipeline_id': ('fk', 'ops.pipelines.id'),
    'ops.execution_stages.execution_id': ('fk', 'ops.pipeline_executions.id'),
    'ops.incidents.pipeline_id': ('fk', 'ops.pipelines.id'),
    'ops.incident_runs.incident_id': ('fk', 'ops.incidents.id'),
    'ops.incident_runs.execution_id': ('fk', 'ops.pipeline_executions.id'),
    'ops.pipeline_access_grants.pipeline_id': ('fk', 'ops.pipelines.id'),
    'evidence.evidence_items.incident_id': ('logical_ref', 'ops.incidents.id'),
    'evidence.evidence_items.execution_id': ('logical_ref', 'ops.pipeline_executions.id'),
    'evidence.correlated_contexts.incident_id': ('logical_ref', 'ops.incidents.id'),
    'evidence.correlated_contexts.execution_id': ('logical_ref', 'ops.pipeline_executions.id'),
    'evidence.correlated_contexts.evidence_ids': ('logical_ref', 'evidence.evidence_items.id'),
    'diagnosis.diagnoses.incident_id': ('logical_ref', 'ops.incidents.id'),
    'diagnosis.recommendations.diagnosis_id': ('fk', 'diagnosis.diagnoses.id'),
    'diagnosis.diagnosis_evidence_links.diagnosis_id': ('fk', 'diagnosis.diagnoses.id'),
    'diagnosis.diagnosis_evidence_links.evidence_id': ('logical_ref', 'evidence.evidence_items.id'),
    'diagnosis.diagnosis_source_links.diagnosis_id': ('fk', 'diagnosis.diagnoses.id'),
    'diagnosis.diagnosis_source_links.knowledge_chunk_id': ('logical_ref', 'knowledge.knowledge_chunks.id'),
    'diagnosis.human_reviews.diagnostic_id': ('fk', 'diagnosis.diagnoses.id'),
    'knowledge.knowledge_documents.reviewed_incident_id': ('logical_ref', 'ops.incidents.id'),
    'knowledge.knowledge_chunks.document_id': ('fk', 'knowledge.knowledge_documents.id'),
}
REQUIRED_CHECKS = {
    'pipeline_executions': ['run_attempt > 0'],
    'evidence_items': ['size_bytes IS NULL OR size_bytes >= 0'],
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
        if name == 'evidence_items' and any(c.get('name') in {'storage_container', 'blob_object_key'} for c in entity.get('attributes', [])):
            errors.append('ADR-019 excludes workload Blob locator columns')
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
    columns = {f"{e['schema']}.{e['table']}.{c['name']}": c
               for e in domain['entities'] for c in e.get('attributes', [])}
    for column, (kind, target) in REQUIRED_REFERENCES.items():
        if columns.get(column, {}).get(kind) != target:
            errors.append(f'{column}: required {kind} to {target}')
    for table, names in {
        'ops.pipeline_executions': ['run_attempt'],
        'diagnosis.diagnoses': ['version', 'status', 'incident_id'],
        'diagnosis.human_reviews': ['decision'],
        'knowledge.knowledge_documents': ['provenance', 'corpus_kind'],
        'knowledge.knowledge_chunks': ['chunk_index', 'document_id', 'provenance'],
    }.items():
        for name in names:
            if columns.get(f'{table}.{name}', {}).get('nullable') is not False:
                errors.append(f'{table}.{name}: approved constraint requires NOT NULL')
    if columns.get('ops.repositories.github_repository_id', {}).get('unique') is not True:
        errors.append('ops.repositories.github_repository_id: approved identity requires UNIQUE')
    confidence = columns.get('diagnosis.diagnoses.confidence', {})
    if confidence.get('type') != 'jsonb' or confidence.get('nullable') is not True:
        errors.append('confidence must remain nullable JSONB while DQ-002 is open')
    questions = domain['open_questions']
    if len({q.get('id') for q in questions}) != len(questions):
        errors.append('Duplicate open question ID')
    if len({q.get('topic') for q in questions}) != len(questions):
        errors.append('Duplicate open question topic')
    return errors
