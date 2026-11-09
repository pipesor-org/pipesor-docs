"""DD-020 source/export constraints. Runtime provider workflows remain adapter-owned."""
TABLES = ('github_connections','github_connection_generations','github_authorization_attempts','github_credential_operations')

REQUIRED_CHECKS = {'github_connections': ['revision >= 0', 'updated_at >= created_at'],
 'github_connection_generations': ["state IN ('PREPARING','ACTIVE','BLOCKED','INVALIDATED')",
                                   'revision >= 0',
                                   "(activated_at IS NULL AND state IN ('PREPARING','INVALIDATED')) OR "
                                   '(activated_at IS NOT NULL AND github_user_id IS NOT NULL AND '
                                   'active_secret_version_ref IS NOT NULL AND access_expires_at IS NOT NULL '
                                   'AND refresh_expires_at IS NOT NULL)',
                                   "btrim(secret_object_ref) <> ''",
                                   "github_user_id IS NULL OR btrim(github_user_id) <> ''",
                                   'active_secret_version_ref IS NULL OR (btrim(active_secret_version_ref) '
                                   "<> '' AND lower(btrim(active_secret_version_ref)) <> 'latest')",
                                   'updated_at >= created_at',
                                   "secret_object_ref = 'generation:' || id::text"],
 'github_authorization_attempts': ["phase IN ('PREPARING','READY','CLAIMED','COMPLETED','FAILED','EXPIRED')",
                                   "pkce_cleanup_state IN ('HELD','PENDING','COMPLETED','BLOCKED')",
                                   'pkce_cleanup_result IS NULL OR pkce_cleanup_result IN '
                                   "('CONFIRMED','UNAVAILABLE','SCOPE_UNAPPROVED','NOT_APPLICABLE')",
                                   'expected_connection_revision >= 0',
                                   "phase NOT IN ('READY','CLAIMED','COMPLETED') OR pkce_secret_version_ref "
                                   'IS NOT NULL',
                                   "phase NOT IN ('CLAIMED','COMPLETED') OR consumed_at IS NOT NULL",
                                   "phase NOT IN ('PREPARING','READY') OR consumed_at IS NULL",
                                   "phase NOT IN ('COMPLETED','FAILED','EXPIRED') OR pkce_cleanup_state <> "
                                   "'HELD'",
                                   "pkce_cleanup_state <> 'COMPLETED' OR (pkce_cleanup_result IS NOT NULL "
                                   "AND pkce_cleanup_result IN ('CONFIRMED','NOT_APPLICABLE'))",
                                   "btrim(pkce_secret_object_ref) <> ''",
                                   "pkce_secret_version_ref IS NULL OR (btrim(pkce_secret_version_ref) <> '' "
                                   "AND lower(btrim(pkce_secret_version_ref)) <> 'latest')",
                                   "btrim(approved_return_ref) <> ''",
                                   "btrim(correlation_id) <> ''",
                                   'expires_at > created_at',
                                   'updated_at >= created_at',
                                   "pkce_cleanup_state <> 'COMPLETED' OR phase IN "
                                   "('COMPLETED','FAILED','EXPIRED')",
                                   "pkce_secret_object_ref = 'pkce:' || id::text"],
 'github_credential_operations': ["kind IN ('REFRESH','CLEANUP')",
                                  "(kind = 'REFRESH' AND phase IN "
                                  "('PENDING','CLAIMED','REQUEST_MAY_BE_IN_FLIGHT','VERSION_SAVED','COMPLETED','BLOCKED')) "
                                  "OR (kind = 'CLEANUP' AND phase IN "
                                  "('PENDING','CLAIMED','COMPLETED','BLOCKED'))",
                                  'fence >= 0 AND expected_connection_revision >= 0 AND '
                                  'expected_generation_revision >= 0',
                                  "(phase = 'PENDING' AND owner_id IS NULL AND started_at IS NULL AND "
                                  "deadline_at IS NULL) OR (phase <> 'PENDING' AND owner_id IS NOT NULL AND "
                                  'started_at IS NOT NULL AND deadline_at IS NOT NULL AND deadline_at >= '
                                  'started_at)',
                                  "(phase = 'COMPLETED') = (completed_at IS NOT NULL)",
                                  "(kind = 'REFRESH' AND cleanup_scope IS NULL AND "
                                  'cleanup_target_version_ref IS NULL AND upstream_result IS NULL AND '
                                  "vault_result IS NULL) OR (kind = 'CLEANUP' AND "
                                  'candidate_secret_version_ref IS NULL AND cleanup_scope IS NOT NULL AND '
                                  "cleanup_scope IN ('EXACT_VERSION','INVALIDATED_GENERATION') AND "
                                  'upstream_result IS NOT NULL AND upstream_result IN '
                                  "('PENDING','CONFIRMED','UNAVAILABLE','SCOPE_UNAPPROVED','NOT_APPLICABLE') "
                                  'AND vault_result IS NOT NULL AND vault_result IN '
                                  "('PENDING','CONFIRMED','UNAVAILABLE','SCOPE_UNAPPROVED','NOT_APPLICABLE'))",
                                  "kind <> 'CLEANUP' OR ((cleanup_scope = 'EXACT_VERSION' AND "
                                  'cleanup_target_version_ref IS NOT NULL) OR (cleanup_scope = '
                                  "'INVALIDATED_GENERATION' AND cleanup_target_version_ref IS NULL))",
                                  '(candidate_secret_version_ref IS NULL OR '
                                  "(btrim(candidate_secret_version_ref) <> '' AND "
                                  "lower(btrim(candidate_secret_version_ref)) <> 'latest')) AND "
                                  '(cleanup_target_version_ref IS NULL OR (btrim(cleanup_target_version_ref) '
                                  "<> '' AND lower(btrim(cleanup_target_version_ref)) <> 'latest'))",
                                  "kind <> 'REFRESH' OR phase NOT IN ('VERSION_SAVED','COMPLETED') OR "
                                  'candidate_secret_version_ref IS NOT NULL',
                                  "kind <> 'CLEANUP' OR phase <> 'COMPLETED' OR (upstream_result IN "
                                  "('CONFIRMED','NOT_APPLICABLE') AND vault_result IN "
                                  "('CONFIRMED','NOT_APPLICABLE'))",
                                  'updated_at >= created_at']}
REQUIRED_UNIQUES = {'github_connections': [['tenant_id', 'entra_object_id'], ['id', 'tenant_id', 'entra_object_id']],
 'github_connection_generations': [['connection_id', 'id'], ['secret_object_ref']],
 'github_authorization_attempts': [['target_generation_id'], ['state_digest'], ['pkce_secret_object_ref']],
 'github_credential_operations': []}

def validate_connector(domain):
    errors = []
    tables = {e['table']: e for e in domain['entities'] if e['schema'] == 'ingestion' and e['table'] in TABLES}
    if set(tables) != set(TABLES):
        errors.append('ingestion requires exactly four DD-020 metadata tables')
    for name, table in tables.items():
        if table['owner_container'] != 'ingestion_normalization_service':
            errors.append('ingestion metadata owner must be ingestion_normalization_service')
        if 'connector_lifecycle' not in table.get('domain_constraints', []):
            errors.append(f'{name}: missing connector_lifecycle constraints')
        actual = {' '.join(c['expression'].split()) for c in table.get('checks', [])}
        if any((' '.join(c.split()) not in actual for c in REQUIRED_CHECKS.get(name, []))):
            errors.append(f'{name}: missing approved CHECK')
        actual = {frozenset(c['columns']) for c in table.get('unique_constraints', [])}
        if any((frozenset(c) not in actual for c in REQUIRED_UNIQUES.get(name, []))):
            errors.append(f'{name}: missing approved uniqueness')
        if any((c['name'] in {'access_token', 'refresh_token', 'code_verifier', 'authorization_code', 'credential_payload'} or c['type'] == 'jsonb' for c in table['attributes'])):
            errors.append('ingestion metadata cannot store credentials or generic JSON')
        if any((c['name'] == 'github_user_id' and c.get('unique') for c in table['attributes'])) or any((u['columns'] == ['github_user_id'] for u in table.get('unique_constraints', []))):
            errors.append('GitHub user reverse uniqueness is not approved')
    if not any((c['name'] == 'connection_id' and c.get('fk') == 'ingestion.github_connections.id' for c in tables.get('github_connection_generations', {}).get('attributes', []))):
        errors.append('github generations require FK to their connection')
    for name, cols, where in [('github_connection_generations', ['connection_id'], "state = 'ACTIVE'"), ('github_credential_operations', ['generation_id'], "kind = 'REFRESH' AND phase <> 'COMPLETED'")]:
        if not any((c.get('columns') == cols and c.get('where') == where for c in tables.get(name, {}).get('partial_unique_constraints', []))):
            errors.append(f'{name}: missing approved partial uniqueness')
    for name, cols, target, refs in MEMBERSHIPS:
        if not any((f.get('columns') == cols and f.get('references') == {'table': 'ingestion.' + target, 'columns': refs} and (f.get('deferrable') is True) and (f.get('initially_deferred') is True) for f in tables.get(name, {}).get('foreign_keys', []))):
            errors.append(f'{name}: missing approved deferred composite membership')
    return errors

MEMBERSHIPS = [('github_connections',
  ['id', 'active_generation_id'],
  'github_connection_generations',
  ['connection_id', 'id']),
 ('github_authorization_attempts',
  ['connection_id', 'tenant_id', 'entra_object_id'],
  'github_connections',
  ['id', 'tenant_id', 'entra_object_id']),
 ('github_authorization_attempts',
  ['connection_id', 'expected_generation_id'],
  'github_connection_generations',
  ['connection_id', 'id']),
 ('github_authorization_attempts',
  ['connection_id', 'target_generation_id'],
  'github_connection_generations',
  ['connection_id', 'id']),
 ('github_credential_operations',
  ['connection_id', 'generation_id'],
  'github_connection_generations',
  ['connection_id', 'id'])]

SQL = r'''
-- DD-020: transactional metadata only; no remote token/PKCE material.
CREATE FUNCTION ingestion.assert_github_connection(p_connection uuid) RETURNS void
LANGUAGE plpgsql SET search_path = pg_catalog, ingestion AS $$
DECLARE current_generation uuid;
BEGIN
    SELECT active_generation_id INTO current_generation FROM ingestion.github_connections
      WHERE id = p_connection FOR UPDATE;
    IF NOT FOUND THEN RETURN; END IF;
    IF EXISTS (SELECT 1 FROM ingestion.github_connection_generations
               WHERE connection_id = p_connection AND state = 'ACTIVE'
                 AND id IS DISTINCT FROM current_generation)
       OR (current_generation IS NOT NULL AND NOT EXISTS (
           SELECT 1 FROM ingestion.github_connection_generations
           WHERE connection_id = p_connection AND id = current_generation AND state = 'ACTIVE')) THEN
        RAISE EXCEPTION 'Connector active generation mismatch' USING ERRCODE = '23514', CONSTRAINT = 'github_active_consistency_ck';
    END IF;
END;
$$;
CREATE FUNCTION ingestion.check_github_connection() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, ingestion AS $$
BEGIN
    IF TG_TABLE_NAME = 'github_connections' THEN
        IF TG_OP <> 'DELETE' THEN PERFORM ingestion.assert_github_connection(NEW.id); END IF;
    ELSE
        IF TG_OP <> 'INSERT' THEN PERFORM ingestion.assert_github_connection(OLD.connection_id); END IF;
        IF TG_OP <> 'DELETE' THEN PERFORM ingestion.assert_github_connection(NEW.connection_id); END IF;
    END IF;
    RETURN NULL;
END;
$$;
CREATE CONSTRAINT TRIGGER github_connections_active_consistency
AFTER INSERT OR UPDATE OR DELETE ON ingestion.github_connections
DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION ingestion.check_github_connection();
CREATE CONSTRAINT TRIGGER github_generations_active_consistency
AFTER INSERT OR UPDATE OR DELETE ON ingestion.github_connection_generations
DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION ingestion.check_github_connection();

CREATE FUNCTION ingestion.guard_github_metadata() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, ingestion AS $$
BEGIN
    IF NEW.id IS DISTINCT FROM OLD.id OR NEW.created_at IS DISTINCT FROM OLD.created_at THEN
        RAISE EXCEPTION 'Connector identity and creation time are immutable' USING ERRCODE = '23514', CONSTRAINT = TG_TABLE_NAME || '_guard_ck';
    END IF;
    IF TG_TABLE_NAME = 'github_connections' THEN
        IF ROW(NEW.tenant_id, NEW.entra_object_id) IS DISTINCT FROM ROW(OLD.tenant_id, OLD.entra_object_id)
           OR (NEW IS DISTINCT FROM OLD AND NEW.revision <= OLD.revision) THEN
            RAISE EXCEPTION 'Connector identity or revision violation' USING ERRCODE = '23514', CONSTRAINT = TG_TABLE_NAME || '_guard_ck';
        END IF;
    ELSIF TG_TABLE_NAME = 'github_connection_generations' THEN
        IF ROW(NEW.connection_id, NEW.secret_object_ref) IS DISTINCT FROM ROW(OLD.connection_id, OLD.secret_object_ref)
           OR (OLD.github_user_id IS NOT NULL AND NEW.github_user_id IS DISTINCT FROM OLD.github_user_id)
           OR (OLD.activated_at IS NOT NULL AND NEW.activated_at IS DISTINCT FROM OLD.activated_at)
           OR (OLD.state = 'INVALIDATED' AND NEW.state <> 'INVALIDATED')
           OR (NEW IS DISTINCT FROM OLD AND NEW.revision <= OLD.revision) THEN
            RAISE EXCEPTION 'Connector generation identity or revision violation' USING ERRCODE = '23514', CONSTRAINT = TG_TABLE_NAME || '_guard_ck';
        END IF;
    ELSIF TG_TABLE_NAME = 'github_authorization_attempts' THEN
        IF ROW(NEW.connection_id, NEW.tenant_id, NEW.entra_object_id, NEW.expected_connection_revision,
               NEW.expected_generation_id, NEW.target_generation_id, NEW.state_digest, NEW.expires_at,
               NEW.pkce_secret_object_ref, NEW.approved_return_ref, NEW.correlation_id)
           IS DISTINCT FROM ROW(OLD.connection_id, OLD.tenant_id, OLD.entra_object_id, OLD.expected_connection_revision,
               OLD.expected_generation_id, OLD.target_generation_id, OLD.state_digest, OLD.expires_at,
               OLD.pkce_secret_object_ref, OLD.approved_return_ref, OLD.correlation_id)
           OR (OLD.consumed_at IS NOT NULL AND NEW.consumed_at IS DISTINCT FROM OLD.consumed_at)
           OR (OLD.pkce_secret_version_ref IS NOT NULL AND NEW.pkce_secret_version_ref IS DISTINCT FROM OLD.pkce_secret_version_ref)
           OR NOT (NEW.phase = OLD.phase
               OR (OLD.phase = 'PREPARING' AND NEW.phase IN ('READY','FAILED','EXPIRED'))
               OR (OLD.phase = 'READY' AND NEW.phase IN ('CLAIMED','FAILED','EXPIRED'))
               OR (OLD.phase = 'CLAIMED' AND NEW.phase IN ('COMPLETED','FAILED','EXPIRED'))) THEN
            RAISE EXCEPTION 'Connector authorization attempt is immutable or consumed' USING ERRCODE = '23514', CONSTRAINT = TG_TABLE_NAME || '_guard_ck';
        END IF;
    ELSE
        IF ROW(NEW.connection_id, NEW.generation_id, NEW.kind, NEW.cleanup_scope, NEW.cleanup_target_version_ref,
               NEW.expected_connection_revision, NEW.expected_generation_revision)
           IS DISTINCT FROM ROW(OLD.connection_id, OLD.generation_id, OLD.kind, OLD.cleanup_scope, OLD.cleanup_target_version_ref,
               OLD.expected_connection_revision, OLD.expected_generation_revision)
           OR NEW.fence < OLD.fence
           OR (NEW.owner_id IS DISTINCT FROM OLD.owner_id AND NEW.fence <= OLD.fence)
           OR (OLD.candidate_secret_version_ref IS NOT NULL AND NEW.candidate_secret_version_ref IS DISTINCT FROM OLD.candidate_secret_version_ref)
           OR NOT (NEW.phase = OLD.phase
               OR (OLD.kind = 'REFRESH' AND (
                   (OLD.phase = 'PENDING' AND NEW.phase IN ('CLAIMED','BLOCKED'))
                   OR (OLD.phase = 'CLAIMED' AND NEW.phase IN ('PENDING','REQUEST_MAY_BE_IN_FLIGHT','BLOCKED'))
                   OR (OLD.phase = 'REQUEST_MAY_BE_IN_FLIGHT' AND NEW.phase IN ('VERSION_SAVED','BLOCKED'))
                   OR (OLD.phase = 'VERSION_SAVED' AND NEW.phase IN ('COMPLETED','BLOCKED'))
                   OR (OLD.phase = 'BLOCKED' AND NEW.phase = 'VERSION_SAVED')))
               OR (OLD.kind = 'CLEANUP' AND (
                   (OLD.phase = 'PENDING' AND NEW.phase IN ('CLAIMED','BLOCKED'))
                   OR (OLD.phase = 'CLAIMED' AND NEW.phase IN ('PENDING','COMPLETED','BLOCKED'))
                   OR (OLD.phase = 'BLOCKED' AND NEW.phase IN ('PENDING','CLAIMED'))))) THEN
            RAISE EXCEPTION 'Connector operation target, fence or remote phase violation' USING ERRCODE = '23514', CONSTRAINT = TG_TABLE_NAME || '_guard_ck';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;
CREATE FUNCTION ingestion.reject_github_metadata_truncate() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN
    RAISE EXCEPTION 'Connector cleanup requires transactional guarded operations' USING ERRCODE = '23514', CONSTRAINT = TG_TABLE_NAME || '_no_truncate_ck';
END; $$;

CREATE TRIGGER github_connections_guard BEFORE UPDATE ON ingestion.github_connections FOR EACH ROW EXECUTE FUNCTION ingestion.guard_github_metadata();
CREATE TRIGGER github_connections_no_truncate BEFORE TRUNCATE ON ingestion.github_connections FOR EACH STATEMENT EXECUTE FUNCTION ingestion.reject_github_metadata_truncate();
CREATE TRIGGER github_connection_generations_guard BEFORE UPDATE ON ingestion.github_connection_generations FOR EACH ROW EXECUTE FUNCTION ingestion.guard_github_metadata();
CREATE TRIGGER github_connection_generations_no_truncate BEFORE TRUNCATE ON ingestion.github_connection_generations FOR EACH STATEMENT EXECUTE FUNCTION ingestion.reject_github_metadata_truncate();
CREATE TRIGGER github_authorization_attempts_guard BEFORE UPDATE ON ingestion.github_authorization_attempts FOR EACH ROW EXECUTE FUNCTION ingestion.guard_github_metadata();
CREATE TRIGGER github_authorization_attempts_no_truncate BEFORE TRUNCATE ON ingestion.github_authorization_attempts FOR EACH STATEMENT EXECUTE FUNCTION ingestion.reject_github_metadata_truncate();
CREATE TRIGGER github_credential_operations_guard BEFORE UPDATE ON ingestion.github_credential_operations FOR EACH ROW EXECUTE FUNCTION ingestion.guard_github_metadata();
CREATE TRIGGER github_credential_operations_no_truncate BEFORE TRUNCATE ON ingestion.github_credential_operations FOR EACH STATEMENT EXECUTE FUNCTION ingestion.reject_github_metadata_truncate();
'''

def generate_lifecycle_sql():
    return SQL
