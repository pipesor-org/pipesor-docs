"""Current DD-003/005/006/007/009/013/023/024/026 constraints, not a SQL parser.

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
    'github_login_attempts': [('state_digest',)],
}
# DD-026: one-time handoff digests and admitted-repository membership of workflow scopes.
REQUIRED_PARTIAL_UNIQUES = {
    'github_login_attempts': [(('handoff_digest',), 'handoff_digest IS NOT NULL')],
}
REQUIRED_COMPOSITE_FKS = {
    'capture_workflow_scopes': [(['tenant_id', 'repository_id'], 'ingestion.repository_admissions',
                                 ['tenant_id', 'repository_id'])],
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
    'evidence.correlated_contexts.scope_pipeline_id': ('logical_ref', 'ops.pipelines.id'),
    'diagnosis.correlated_context_receipts.context_id': ('logical_ref', 'evidence.correlated_contexts.id'),
    'diagnosis.correlated_context_receipts.pipeline_id': ('logical_ref', 'ops.pipelines.id'),
    'diagnosis.correlated_context_receipts.incident_id': ('logical_ref', 'ops.incidents.id'),
    'diagnosis.correlated_context_receipts.execution_id': ('logical_ref', 'ops.pipeline_executions.id'),
    'diagnosis.correlated_context_receipts.evidence_ids': ('logical_ref', 'evidence.evidence_items.id'),
    'diagnosis.diagnoses.incident_id': ('logical_ref', 'ops.incidents.id'),
    'diagnosis.recommendations.diagnosis_id': ('fk', 'diagnosis.diagnoses.id'),
    'diagnosis.diagnosis_evidence_links.diagnosis_id': ('fk', 'diagnosis.diagnoses.id'),
    'diagnosis.diagnosis_evidence_links.evidence_id': ('logical_ref', 'evidence.evidence_items.id'),
    'diagnosis.diagnosis_source_links.diagnosis_id': ('fk', 'diagnosis.diagnoses.id'),
    'diagnosis.diagnosis_source_links.knowledge_chunk_id': ('logical_ref', 'knowledge.knowledge_chunks.id'),
    'diagnosis.human_reviews.diagnostic_id': ('fk', 'diagnosis.diagnoses.id'),
    'knowledge.knowledge_documents.reviewed_incident_id': ('logical_ref', 'ops.incidents.id'),
    'knowledge.knowledge_chunks.document_id': ('fk', 'knowledge.knowledge_documents.id'),
    'ops.execution_event_receipts.execution_id': ('logical_ref', 'ops.pipeline_executions.id'),
    'ops.incident_diagnoses.incident_id': ('fk', 'ops.incidents.id'),
    'ops.incident_diagnoses.execution_id': ('fk', 'ops.pipeline_executions.id'),
    'ops.incident_diagnoses.diagnosis_id': ('logical_ref', 'diagnosis.diagnoses.id'),
    'diagnosis.diagnosis_jobs.context_id': ('fk', 'diagnosis.correlated_context_receipts.context_id'),
    'diagnosis.incident_summary_outbox.incident_id': ('logical_ref', 'ops.incidents.id'),
    'diagnosis.incident_summary_outbox.execution_id': ('logical_ref', 'ops.pipeline_executions.id'),
    'ingestion.github_login_attempts.connection_id': ('logical_ref', 'ingestion.github_connections.id'),
    'ingestion.github_login_attempts.generation_id': ('logical_ref', 'ingestion.github_connection_generations.id'),
    'ingestion.capture_workflow_scopes.pipeline_id': ('logical_ref', 'ops.pipelines.id'),
}
REQUIRED_CHECKS = {
    'pipeline_executions': ['run_attempt > 0'],
    'evidence_items': [
        'size_bytes IS NULL OR size_bytes >= 0',
        "((scope_tenant_id IS NULL AND scope_github_installation_id IS NULL AND scope_revision IS NULL) "
        "OR (scope_tenant_id IS NOT NULL AND scope_tenant_id <> '00000000-0000-0000-0000-000000000000'::uuid "
        "AND scope_github_installation_id IS NOT NULL AND scope_github_installation_id ~ '^[1-9][0-9]*$' "
        "AND scope_revision IS NOT NULL AND scope_revision ~ '^[A-Za-z0-9._:-]{1,128}$'))",
    ],
    'diagnoses': ['version > 0', "status <> 'DIAGNOSIS_READY' OR (probable_cause IS NOT NULL AND btrim(probable_cause) <> '' AND diagnosis_ready_at IS NOT NULL)"],
    'human_reviews': ["decision <> 'CORRECTED' OR (actual_cause IS NOT NULL AND btrim(actual_cause) <> '')"],
    'knowledge_documents': ["btrim(provenance) <> ''", "corpus_kind <> 'reviewed_incidents' OR reviewed_incident_id IS NOT NULL"],
    'knowledge_chunks': ['chunk_index >= 0', "btrim(provenance) <> ''"],
    'correlated_context_receipts': [
        'operation_id = context_id',
        "request_fingerprint ~ '^v1:sha256:[0-9a-f]{64}$'",
        "github_installation_id ~ '^[1-9][0-9]{0,31}$'",
        "github_repository_id ~ '^[1-9][0-9]{0,31}$'",
        "scope_revision ~ '^[A-Za-z0-9._:-]{1,128}$'",
        'cardinality(evidence_ids) > 0',
        "btrim(summary) <> ''",
        "correlation_id ~ '^[A-Za-z0-9._:-]{1,128}$'",
    ],
    # DD-026: implemented MVP tables, expressions as in their owners' migrations.
    'execution_event_receipts': [
        "message_digest ~ '^[0-9a-f]{64}$'",
        "content_digest ~ '^[0-9a-f]{64}$'",
        'source_submicro_nanos BETWEEN 0 AND 999',
        "disposition IN ('APPLIED','DUPLICATE','IGNORED_STALE','IGNORED_PAUSED')",
    ],
    'incident_diagnoses': [
        'diagnosis_version > 0',
        "status IN ('PENDING','CONFIRMED','CORRECTED','REJECTED')",
        "review_revision >= 0 AND (status = 'PENDING') = (review_revision = 0) AND (reviewed_at IS NULL) = (review_revision = 0)",
        'probable_cause IS NULL OR char_length(probable_cause) BETWEEN 1 AND 1000',
    ],
    'diagnosis_jobs': [
        "state IN ('PENDING','DONE','FAILED')",
        'attempts >= 0',
        "last_failure IS NULL OR last_failure ~ '^[a-z][a-z0-9_]{0,63}$'",
        "state = 'PENDING' OR lease_until IS NULL",
    ],
    'incident_summary_outbox': [
        'generation > 0',
        'attempts >= 0',
        "last_failure IS NULL OR last_failure ~ '^[a-z][a-z0-9_]{0,63}$'",
    ],
    'github_login_attempts': [
        "phase IN ('READY','CLAIMED','HANDOFF_READY','COMPLETED','FAILED')",
        "pkce_secret_object_ref = 'pkce:' || id::text",
        "btrim(pkce_secret_version_ref) <> '' AND lower(btrim(pkce_secret_version_ref)) <> 'latest'",
        "return_path ~ '^/'",
        "btrim(correlation_id) <> ''",
        'expires_at > created_at',
        'updated_at >= created_at',
        "(phase IN ('HANDOFF_READY','COMPLETED')) = (handoff_digest IS NOT NULL) AND (handoff_digest IS NULL OR "
        "(handoff_expires_at IS NOT NULL AND connection_id IS NOT NULL AND generation_id IS NOT NULL AND "
        "github_user_id ~ '^[1-9][0-9]*$' AND btrim(github_login) <> ''))",
    ],
    'repository_admissions': [
        "app_id ~ '^[1-9][0-9]*$' AND account_id ~ '^[1-9][0-9]*$' AND installation_id ~ '^[1-9][0-9]*$' "
        "AND repository_id ~ '^[1-9][0-9]*$'",
        "btrim(admitted_by) <> ''",
        "source IN ('operator','repository_administrator')",
        "(revoked_at IS NULL) = (revoked_by IS NULL) AND (revoked_by IS NULL OR btrim(revoked_by) <> '')",
    ],
    'capture_workflow_scopes': [
        "status IN ('ACTIVE','PAUSED')",
        "app_id ~ '^[1-9][0-9]*$' AND account_id ~ '^[1-9][0-9]*$' AND installation_id ~ '^[1-9][0-9]*$' "
        "AND repository_id ~ '^[1-9][0-9]*$' AND workflow_id ~ '^[1-9][0-9]*$'",
        "cardinality(allowed_actions) > 0 AND allowed_actions <@ ARRAY['requested','in_progress','completed']::text[]",
        "replay_window > interval '0'",
        "revision > 0 AND scope_revision ~ '^[A-Za-z0-9._:-]{1,128}$'",
    ],
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
        partial = {(tuple(c.get('columns', [])), normalize(c.get('where', '')))
                   for c in entity.get('partial_unique_constraints', [])}
        for columns, where in REQUIRED_PARTIAL_UNIQUES.get(name, []):
            if (columns, normalize(where)) not in partial:
                errors.append(f'{name}: missing approved partial uniqueness {columns}')
        foreign_keys = [(f.get('columns'), f.get('references', {}).get('table'), f.get('references', {}).get('columns'))
                        for f in entity.get('foreign_keys', [])]
        for required in REQUIRED_COMPOSITE_FKS.get(name, []):
            if tuple(required) not in [tuple(f) for f in foreign_keys]:
                errors.append(f'{name}: missing approved composite FK {required[0]}')
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
