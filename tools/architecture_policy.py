"""Executable guards for current INV-001/002/003/010 and ADR-005/014/016.

These checks validate the declared graph, not runtime sanitization. Changes to
accepted policy must update these guards and their tests explicitly.
"""


def validate_policy(doc):
    errors = []
    elements = {e['id']: e for e in doc.get('elements', [])}
    relations = doc.get('relationships', [])
    invariants = {i['id'] for i in doc.get('architectural_invariants', [])}
    # Generic fixtures without this project's invariants remain usable.
    if doc.get('architecture', {}).get('id') == 'ey_aiops_ci_cd_diagnosis':
        if {'api_management', 'object_evidence_store'} & elements.keys():
            errors.append('ADR-019 excludes APIM and workload Blob from the MVP')
        ingress = doc.get('deployment', {}).get('identity_and_api_perimeter', {})
        if ingress.get('api_ingress') != 'Azure Container Apps native ingress' or ingress.get('dedicated_gateway') is not False:
            errors.append('ADR-019 requires native ACA ingress without a dedicated gateway')
        mvp = doc.get('deployment', {}).get('mvp_preparation', {})
        if mvp.get('active_environment') != 'dev' or mvp.get('deployment_authorized') is not False:
            errors.append('ADR-019 permits only dev preparation, not deployment')
        foundation = elements.get('pretrained_llm_diagnostic_service', {}).get('foundation', {})
        if (foundation.get('technology') != 'Microsoft Foundry'
                or foundation.get('authentication') != 'Entra_only'
                or foundation.get('model_deployments_selected') is not False):
            errors.append('ADR-019 requires the Entra-only Foundry foundation without model selection')
        required = {'INV-001', 'INV-002', 'INV-003', 'INV-010'}
        if not required <= invariants:
            errors.append('Missing current privacy/read-only/RAG invariants')
        invariants |= required
    if 'INV-003' in invariants:
        expected = {'mechanism': 'GitHub App', 'access': 'read_only',
                    'credential_type': 'installation_token'}
        for location, auth in (
            ('github.authentication', elements.get('github', {}).get('authentication', {})),
            ('deployment.github_authentication', doc.get('deployment', {}).get('github_authentication', {})),
        ):
            if any(auth.get(k) != v for k, v in expected.items()):
                errors.append(f'{location}: ADR-005 requires GitHub App/read_only/installation_token')
        for location, auth in (
            ('github.authentication', elements.get('github', {}).get('authentication', {})),
            ('deployment.github_authentication', doc.get('deployment', {}).get('github_authentication', {})),
        ):
            if (auth.get('user_credential_type') != 'user_access_token'
                    or auth.get('user_connection_owner') != 'ingestion_normalization_service'):
                errors.append(f'{location}: ADR-020 requires user tokens owned by Ingestion')
        for r in relations:
            endpoints = {r.get('from'), r.get('to')}
            if endpoints & {'github', 'github_actions'}:
                internal = endpoints - {'github', 'github_actions'}
                if internal and r.get('access') != 'read_only':
                    errors.append(f"{r.get('id')}: GitHub integration must declare read_only")
                if r.get('access') not in (None, 'read_only'):
                    errors.append(f"{r.get('id')}: GitHub write access is prohibited")
        for output in doc.get('outputs', []):
            if output.get('publication_target') in {'github', 'github_actions'}:
                if (output.get('published_by') != 'github_actions'
                        or output.get('publication_mode') != 'workflow_pull_then_native_upload'):
                    errors.append(f"{output.get('id')}: ADR-016 requires workflow-owned artifact publication")
    if 'INV-001' in invariants:
        gateway = 'ingestion_normalization_service'
        required = {'masking', 'anonymization', 'secret_filtering', 'data_minimization',
                    'validation', 'normalization'}
        if not required <= set(elements.get(gateway, {}).get('capabilities', [])):
            errors.append('INV-001: ingestion must retain validation/normalization/privacy capabilities')
        controls = {c['id']: c for c in doc.get('cross_cutting_controls', [])}
        if not {'masking_before_ai', 'anonymization_before_ai', 'minimization_before_ai',
                'secret_filtering_before_ai'} <= set(controls.get('CTRL-002', {}).get('rules', [])):
            errors.append('CTRL-002: privacy before AI controls are required')
        # Check all alternate paths: existence of one safe route is insufficient.
        adjacency = {}
        for r in relations:
            query = (r.get('id') in {'rel_github_actions_diagnostic', 'rel_github_actions_diagnostic_api'}
                     and r.get('from') == 'github_actions'
                     and r.get('to') in {'recommendation_service', 'diagnostic_api_component'}
                     and r.get('access') == 'read_only')
            if not query and r.get('from') != gateway and r.get('to') != gateway:
                adjacency.setdefault(r.get('from'), set()).add(r.get('to'))
        pending = ['github', 'github_actions', 'observability_sources']
        visited = set()
        protected = {'nlp_log_processor', 'rag_retrieval', 'pretrained_llm_diagnostic_service'}
        while pending:
            node = pending.pop()
            if node in visited:
                continue
            visited.add(node)
            if node in protected:
                errors.append(f'INV-001: evidence path bypasses ingestion/privacy boundary to {node}')
            pending.extend(adjacency.get(node, set()) - visited)
    if 'INV-002' in invariants:
        contract = elements.get('pretrained_llm_diagnostic_service', {}).get('input_contract', [])
        if set(contract) != {'sanitized_prioritized_evidence', 'correlated_context', 'rag_retrieved_knowledge'}:
            errors.append('INV-002: LLM requires sanitized evidence/context/RAG input contract')
    if 'INV-010' in invariants:
        rag = elements.get('rag_retrieval', {})
        if set(rag.get('knowledge_scope', [])) != {'reviewed_incidents', 'authorized_technical_documentation', 'authorized_response_procedures'} or rag.get('provenance_required') is not True:
            errors.append('INV-010: authorized RAG corpus and provenance are required')
    return errors
