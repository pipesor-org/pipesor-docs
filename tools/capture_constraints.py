"""DD-021 durable capture ledger constraints; no runtime or network authorization."""
TABLES = ('capture_receipts', 'capture_delivery_aliases', 'capture_observations', 'publication_outputs')


# Frozen expressions reject weakening of the locally adopted physical contract.
REQUIRED_CHECKS = {'capture_receipts': ["btrim(capture_domain) <> ''",
                      "btrim(source) <> ''",
                      "btrim(body_digest) <> ''",
                      "body_digest ~ '^[0-9a-f]{64}$'",
                      "btrim(app_id) <> ''",
                      "app_id ~ '^[1-9][0-9]*$'",
                      "btrim(account_id) <> ''",
                      "account_id ~ '^[1-9][0-9]*$'",
                      "btrim(installation_id) <> ''",
                      "installation_id ~ '^[1-9][0-9]*$'",
                      "btrim(repository_id) <> ''",
                      "repository_id ~ '^[1-9][0-9]*$'",
                      "btrim(workflow_id) <> ''",
                      "workflow_id ~ '^[1-9][0-9]*$'",
                      "btrim(run_id) <> ''",
                      "run_id ~ '^[1-9][0-9]*$'",
                      'run_attempt > 0',
                      "btrim(scope_revision) <> ''",
                      "btrim(correlation_id) <> ''",
                      "btrim(phase) <> ''",
                      'revision >= 0',
                      'claim_fence >= 0',
                      'updated_at >= created_at',
                      '(claim_owner IS NULL) = (lease_until IS NULL)',
                      "(phase = 'BLOCKED') = (blocked_reason IS NOT NULL) AND (blocked_reason IS NULL OR "
                      "btrim(blocked_reason) <> '')",
                      "phase IN ('ACCEPTED','PREPARED','PUBLISHED','BLOCKED')",
                      'snapshot_message_id <> evidence_message_id',
                      "(phase NOT IN ('PREPARED','PUBLISHED') OR (observation_id IS NOT NULL AND prepared_at IS "
                      "NOT NULL AND replay_until IS NOT NULL)) AND (phase <> 'ACCEPTED' OR (observation_id IS "
                      'NULL AND prepared_at IS NULL AND published_at IS NULL))',
                      "(phase = 'PUBLISHED') = (published_at IS NOT NULL)",
                      '(prepared_at IS NULL OR prepared_at >= created_at) AND (published_at IS NULL OR '
                      'published_at >= prepared_at) AND replay_until > created_at',
                      "claim_owner IS NULL OR phase = 'ACCEPTED'"],
 'capture_delivery_aliases': ["btrim(capture_domain) <> ''", "btrim(source) <> ''", "btrim(delivery_id) <> ''"],
 'capture_observations': ["btrim(capture_domain) <> ''",
                          "btrim(source) <> ''",
                          "observation_key ~ '^[0-9a-f]{64}$'",
                          "btrim(protected_content_digest) <> ''",
                          "protected_content_digest ~ '^[0-9a-f]{64}$'",
                          "btrim(repository_id) <> ''",
                          "repository_id ~ '^[1-9][0-9]*$'",
                          "btrim(workflow_id) <> ''",
                          "workflow_id ~ '^[1-9][0-9]*$'",
                          "btrim(run_id) <> ''",
                          "run_id ~ '^[1-9][0-9]*$'",
                          'run_attempt > 0',
                          "btrim(normalizer_version) <> ''",
                          "btrim(protection_policy_version) <> ''",
                          "btrim(correlation_id) <> ''",
                          'required_output_count IN (1,2)',
                          'observed_at_submicro BETWEEN 0 AND 999',
                          'source_updated_at_submicro BETWEEN 0 AND 999'],
 'publication_outputs': ["btrim(event_type) <> ''",
                         "btrim(payload_digest) <> ''",
                         "payload_digest ~ '^[0-9a-f]{64}$'",
                         "btrim(phase) <> ''",
                         'revision >= 0',
                         'claim_fence >= 0',
                         'attempt_count >= 0',
                         'updated_at >= created_at',
                         '(claim_owner IS NULL) = (lease_until IS NULL)',
                         "(phase = 'BLOCKED') = (blocked_reason IS NOT NULL) AND (blocked_reason IS NULL OR "
                         "btrim(blocked_reason) <> '')",
                         "(event_type = 'execution.snapshot' AND schema_major = 1 AND fragment_locator IS NULL) "
                         "OR (event_type = 'protected_workflow_evidence' AND schema_major = 2 AND "
                         "fragment_locator IS NOT NULL AND btrim(fragment_locator) <> '')",
                         "phase IN ('PENDING','CLAIMED','CONFIRMED','BLOCKED')",
                         "(phase = 'CLAIMED') = (claim_owner IS NOT NULL)",
                         "(phase = 'CONFIRMED') = (confirmed_at IS NOT NULL)",
                         '(payload IS NOT NULL AND payload_removed_at IS NULL) OR (payload IS NULL AND phase = '
                         "'CONFIRMED' AND payload_removed_at IS NOT NULL AND payload_recover_until IS NOT NULL "
                         'AND payload_removed_at >= payload_recover_until)',
                         '(confirmed_at IS NULL OR confirmed_at >= created_at) AND (payload_removed_at IS NULL OR '
                         'payload_removed_at >= confirmed_at) AND (payload_recover_until IS NULL OR '
                         'payload_recover_until > created_at)',
                         "phase <> 'CLAIMED' OR (last_attempt_at IS NOT NULL AND lease_until > last_attempt_at "
                         'AND attempt_count > 0)']}


def validate_capture(domain):
    errors = []
    tables = {e['table']: e for e in domain['entities'] if e['schema'] == 'ingestion'}
    if set(tables) != set(TABLES) | {'github_connections', 'github_connection_generations',
                                    'github_authorization_attempts', 'github_credential_operations',
                                    'github_login_attempts', 'repository_admissions', 'capture_workflow_scopes'}:
        errors.append('ingestion requires only the four DD-020, four DD-021 and three DD-026 tables')
    for name in TABLES:
        entity = tables.get(name, {})
        if entity.get('owner_container') != 'ingestion_normalization_service':
            errors.append(f'{name}: capture owner must remain ingestion_normalization_service')
        if 'capture_lifecycle' not in entity.get('domain_constraints', []):
            errors.append(f'{name}: missing capture_lifecycle constraints')
        actual_checks = {' '.join(c['expression'].split()) for c in entity.get('checks', [])}
        if any(' '.join(c.split()) not in actual_checks for c in REQUIRED_CHECKS[name]):
            errors.append(f'{name}: missing approved capture CHECK')
        attributes = {c['name']: c for c in entity.get('attributes', [])}
        if any(n in attributes for n in ('raw_body', 'raw_log', 'signature', 'access_token', 'refresh_token')):
            errors.append(f'{name}: capture cannot retain raw inputs or credentials')
        if name in ('capture_delivery_aliases', 'capture_observations') and 'updated_at' in attributes:
            errors.append(f'{name}: append-only rows cannot have updated_at')
        if name == 'capture_receipts':
            if attributes.get('replay_until', {}).get('type') != 'timestamptz' or attributes['replay_until'].get('nullable'):
                errors.append('capture_receipts: acceptance requires an explicit replay horizon')
            for n in ('snapshot_message_id', 'evidence_message_id'):
                if attributes.get(n, {}).get('type') != 'uuid' or attributes[n].get('nullable') or not attributes[n].get('unique'):
                    errors.append(f'{name}: reserved message UUIDs must be mandatory and unique')
        if name == 'capture_observations':
            for n in ('observed_at_submicro', 'source_updated_at_submicro'):
                if attributes.get(n, {}).get('type') != 'integer' or attributes[n].get('nullable'):
                    errors.append(f'{name}: source instants require lossless submicro companions')
        required = {
            'capture_receipts': [['capture_domain', 'source', 'body_digest'], ['capture_domain', 'source', 'id']],
            'capture_delivery_aliases': [['capture_domain', 'source', 'delivery_id']],
            'capture_observations': [['capture_domain', 'source', 'observation_key'], ['capture_domain', 'source', 'id']],
            'publication_outputs': [],
        }[name]
        if any(cols not in [u['columns'] for u in entity.get('unique_constraints', [])] for cols in required):
            errors.append(f'{name}: missing approved capture uniqueness')
    for name, columns, target, refs in MEMBERSHIPS:
        if not any(f.get('columns') == columns and f.get('references') == {'table': 'ingestion.' + target, 'columns': refs}
                   and f.get('deferrable') is True and f.get('initially_deferred') is True
                   for f in tables.get(name, {}).get('foreign_keys', [])):
            errors.append(f'{name}: missing approved capture membership')
    outputs = tables.get('publication_outputs', {})
    for columns, where in [(['observation_id'], "event_type = 'execution.snapshot'"),
                           (['observation_id', 'fragment_locator'], "event_type = 'protected_workflow_evidence'")]:
        if not any(u.get('columns') == columns and u.get('where') == where for u in outputs.get('partial_unique_constraints', [])):
            errors.append('publication_outputs: missing approved output uniqueness')
    return errors


MEMBERSHIPS = [
    ('capture_receipts', ['capture_domain','source','observation_id'], 'capture_observations', ['capture_domain','source','id']),
    ('capture_delivery_aliases', ['capture_domain','source','receipt_id'], 'capture_receipts', ['capture_domain','source','id']),
    ('capture_observations', ['capture_domain','source','origin_receipt_id'], 'capture_receipts', ['capture_domain','source','id']),
    ('publication_outputs', ['observation_id'], 'capture_observations', ['id']),
]

SQL = r'''
-- DD-021: identities, context, final bytes and the complete publication plan are immutable.
CREATE FUNCTION ingestion.assert_capture_observation(p_observation uuid) RETURNS void
LANGUAGE plpgsql SET search_path = pg_catalog, ingestion AS $$
DECLARE o ingestion.capture_observations; r ingestion.capture_receipts;
BEGIN
    SELECT * INTO o FROM ingestion.capture_observations WHERE id = p_observation FOR UPDATE;
    IF NOT FOUND THEN RETURN; END IF;
    SELECT * INTO r FROM ingestion.capture_receipts WHERE id = o.origin_receipt_id;
    IF NOT FOUND OR r.observation_id IS DISTINCT FROM o.id OR r.prepared_at IS NULL
       OR ROW(o.capture_domain,o.source,o.repository_id,o.workflow_id,o.run_id,o.run_attempt,o.correlation_id)
       IS DISTINCT FROM ROW(r.capture_domain,r.source,r.repository_id,r.workflow_id,r.run_id,r.run_attempt,r.correlation_id) THEN
        RAISE EXCEPTION 'Capture observation origin mismatch' USING ERRCODE = '23514', CONSTRAINT = 'capture_origin_ck';
    END IF;
    IF EXISTS (SELECT 1 FROM ingestion.capture_receipts linked WHERE linked.observation_id = o.id AND
       ROW(linked.capture_domain,linked.source,linked.tenant_id,linked.app_id,linked.account_id,linked.installation_id,
           linked.repository_id,linked.workflow_id,linked.run_id,linked.run_attempt)
       IS DISTINCT FROM ROW(r.capture_domain,r.source,r.tenant_id,r.app_id,r.account_id,r.installation_id,
           r.repository_id,r.workflow_id,r.run_id,r.run_attempt)) THEN
        RAISE EXCEPTION 'Capture receipt context mismatch' USING ERRCODE = '23514', CONSTRAINT = 'capture_context_ck';
    END IF;
    IF (SELECT count(*) FROM ingestion.publication_outputs WHERE observation_id = o.id) <> o.required_output_count
       OR (SELECT count(*) FROM ingestion.publication_outputs WHERE observation_id = o.id AND event_type = 'execution.snapshot') <> 1
       OR NOT EXISTS (SELECT 1 FROM ingestion.publication_outputs WHERE observation_id = o.id
                      AND event_type = 'execution.snapshot' AND id = r.snapshot_message_id)
       OR (o.required_output_count > 1 AND NOT EXISTS (
           SELECT 1 FROM ingestion.publication_outputs WHERE observation_id = o.id
           AND event_type = 'protected_workflow_evidence' AND id = r.evidence_message_id)) THEN
        RAISE EXCEPTION 'Capture publication plan incomplete or message identity mismatch'
          USING ERRCODE = '23514', CONSTRAINT = 'capture_plan_ck';
    END IF;
    IF EXISTS (SELECT 1 FROM ingestion.capture_receipts WHERE observation_id = o.id AND phase = 'PUBLISHED')
       AND EXISTS (SELECT 1 FROM ingestion.publication_outputs WHERE observation_id = o.id AND phase <> 'CONFIRMED') THEN
        RAISE EXCEPTION 'Capture publication is not confirmed' USING ERRCODE = '23514', CONSTRAINT = 'capture_publication_ck';
    END IF;
END;
$$;
CREATE FUNCTION ingestion.check_capture_plan() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, ingestion AS $$
BEGIN
    IF TG_TABLE_NAME = 'capture_observations' THEN
        PERFORM ingestion.assert_capture_observation(NEW.id);
    ELSIF NEW.observation_id IS NOT NULL THEN
        PERFORM ingestion.assert_capture_observation(NEW.observation_id);
    END IF;
    RETURN NULL;
END;
$$;
CREATE CONSTRAINT TRIGGER capture_receipts_plan AFTER INSERT OR UPDATE ON ingestion.capture_receipts
DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION ingestion.check_capture_plan();
CREATE CONSTRAINT TRIGGER capture_observations_plan AFTER INSERT ON ingestion.capture_observations
DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION ingestion.check_capture_plan();
CREATE CONSTRAINT TRIGGER publication_outputs_plan AFTER INSERT OR UPDATE ON ingestion.publication_outputs
DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION ingestion.check_capture_plan();

CREATE FUNCTION ingestion.guard_capture_immutable() RETURNS trigger
LANGUAGE plpgsql AS $$ BEGIN
    RAISE EXCEPTION 'Capture ledger mutation requires an approved retention operation'
      USING ERRCODE = '23514', CONSTRAINT = TG_TABLE_NAME || '_immutable_ck';
END; $$;

CREATE FUNCTION ingestion.guard_capture_receipt() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, ingestion AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.phase <> 'ACCEPTED' OR NEW.revision <> 0 OR NEW.claim_fence <> 0
           OR NEW.claim_owner IS NOT NULL OR NEW.updated_at <> NEW.created_at THEN
            RAISE EXCEPTION 'Capture receipt requires initial accepted state' USING ERRCODE = '23514';
        END IF;
        RETURN NEW;
    END IF;
    IF OLD.observation_id IS NULL AND NEW.observation_id IS NOT NULL AND NEW.phase <> 'PREPARED' THEN
        RAISE EXCEPTION 'Capture observation association requires preparation'
          USING ERRCODE = '23514', CONSTRAINT = 'capture_receipts_association_ck';
    END IF;
    IF NEW.replay_until IS DISTINCT FROM OLD.replay_until THEN
        RAISE EXCEPTION 'Capture replay horizon is immutable after acceptance'
          USING ERRCODE = '23514', CONSTRAINT = 'capture_receipts_replay_horizon_ck';
    END IF;
    IF ROW(NEW.id,NEW.capture_domain,NEW.tenant_id,NEW.source,NEW.body_digest,NEW.app_id,NEW.account_id,NEW.installation_id,
           NEW.repository_id,NEW.workflow_id,NEW.run_id,NEW.run_attempt,NEW.scope_revision,NEW.correlation_id,
           NEW.snapshot_message_id,NEW.evidence_message_id,NEW.created_at)
       IS DISTINCT FROM ROW(OLD.id,OLD.capture_domain,OLD.tenant_id,OLD.source,OLD.body_digest,OLD.app_id,OLD.account_id,OLD.installation_id,
           OLD.repository_id,OLD.workflow_id,OLD.run_id,OLD.run_attempt,OLD.scope_revision,OLD.correlation_id,
           OLD.snapshot_message_id,OLD.evidence_message_id,OLD.created_at)
       OR (OLD.blocked_reason IS NOT NULL AND NEW.blocked_reason IS DISTINCT FROM OLD.blocked_reason)
       OR NEW.revision <> OLD.revision + 1 OR NEW.updated_at < OLD.updated_at
       OR NEW.claim_fence < OLD.claim_fence
       OR (NEW.claim_owner IS NOT NULL AND (NEW.claim_owner IS DISTINCT FROM OLD.claim_owner OR NEW.lease_until IS DISTINCT FROM OLD.lease_until)
           AND NEW.claim_fence <> OLD.claim_fence + 1)
       OR (NEW.claim_owner IS NULL AND NEW.claim_fence <> OLD.claim_fence)
       OR (NEW.claim_owner IS NOT NULL AND (NEW.lease_until <= NEW.updated_at
           OR (NEW.claim_fence > OLD.claim_fence AND OLD.claim_owner IS NOT NULL AND OLD.lease_until > NEW.updated_at)))
       OR (OLD.observation_id IS NOT NULL AND NEW.observation_id IS DISTINCT FROM OLD.observation_id)
       OR (OLD.prepared_at IS NOT NULL AND ROW(NEW.prepared_at,NEW.replay_until) IS DISTINCT FROM ROW(OLD.prepared_at,OLD.replay_until))
       OR (OLD.published_at IS NOT NULL AND NEW.published_at IS DISTINCT FROM OLD.published_at)
       OR NOT (NEW.phase = OLD.phase OR (OLD.phase = 'ACCEPTED' AND NEW.phase IN ('PREPARED','BLOCKED'))
            OR (OLD.phase = 'PREPARED' AND NEW.phase IN ('PUBLISHED','BLOCKED')))
       OR (OLD.phase = 'ACCEPTED' AND NEW.phase = 'PREPARED' AND
           (OLD.claim_owner IS NULL OR OLD.lease_until <= NEW.updated_at OR NEW.claim_owner IS NOT NULL)) THEN
        RAISE EXCEPTION 'Capture receipt identity, revision, claim or phase violation'
          USING ERRCODE = '23514', CONSTRAINT = 'capture_receipts_guard_ck';
    END IF;
    RETURN NEW;
END;
$$;
CREATE FUNCTION ingestion.guard_publication_output() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, ingestion AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.phase <> 'PENDING' OR NEW.revision <> 0 OR NEW.claim_fence <> 0 OR NEW.attempt_count <> 0
           OR NEW.payload IS NULL OR NEW.payload_removed_at IS NOT NULL OR NEW.claim_owner IS NOT NULL
           OR NEW.last_attempt_at IS NOT NULL OR NEW.updated_at <> NEW.created_at THEN
            RAISE EXCEPTION 'Publication output requires initial pending bytes' USING ERRCODE = '23514';
        END IF;
        RETURN NEW;
    END IF;
    IF ROW(NEW.id,NEW.observation_id,NEW.event_type,NEW.schema_major,NEW.fragment_locator,NEW.payload_digest,
           NEW.payload_recover_until,NEW.created_at)
       IS DISTINCT FROM ROW(OLD.id,OLD.observation_id,OLD.event_type,OLD.schema_major,OLD.fragment_locator,OLD.payload_digest,
           OLD.payload_recover_until,OLD.created_at)
       OR (OLD.blocked_reason IS NOT NULL AND NEW.blocked_reason IS DISTINCT FROM OLD.blocked_reason)
       OR NEW.revision <> OLD.revision + 1 OR NEW.updated_at < OLD.updated_at
       OR NEW.claim_fence < OLD.claim_fence OR NEW.attempt_count < OLD.attempt_count
       OR (OLD.confirmed_at IS NOT NULL AND NEW.confirmed_at IS DISTINCT FROM OLD.confirmed_at)
       OR (OLD.payload IS NULL AND NEW.payload IS DISTINCT FROM OLD.payload)
       OR (NEW.payload IS NOT NULL AND NEW.payload IS DISTINCT FROM OLD.payload)
       OR (OLD.payload_removed_at IS NOT NULL AND NEW.payload_removed_at IS DISTINCT FROM OLD.payload_removed_at)
       OR (OLD.payload IS NOT NULL AND NEW.payload IS NULL AND
           (OLD.phase <> 'CONFIRMED' OR OLD.payload_recover_until IS NULL
            OR NEW.updated_at < OLD.payload_recover_until OR NEW.payload_removed_at IS DISTINCT FROM NEW.updated_at))
       OR NOT (NEW.phase = OLD.phase OR (OLD.phase = 'PENDING' AND NEW.phase IN ('CLAIMED','BLOCKED'))
            OR (OLD.phase = 'CLAIMED' AND NEW.phase IN ('PENDING','CONFIRMED','BLOCKED')))
       OR (NEW.phase = 'CLAIMED' AND
           (NEW.claim_fence <> OLD.claim_fence + 1 OR NEW.attempt_count <> OLD.attempt_count + 1
            OR NEW.last_attempt_at IS DISTINCT FROM NEW.updated_at
            OR (OLD.phase = 'CLAIMED' AND OLD.lease_until > NEW.updated_at)))
       OR (NEW.phase <> 'CLAIMED' AND
           (NEW.claim_fence <> OLD.claim_fence OR NEW.attempt_count <> OLD.attempt_count
            OR NEW.last_attempt_at IS DISTINCT FROM OLD.last_attempt_at))
       OR (OLD.phase = 'CLAIMED' AND NEW.phase <> 'CLAIMED' AND OLD.lease_until <= NEW.updated_at) THEN
        RAISE EXCEPTION 'Publication output identity, bytes, revision, claim or phase violation'
          USING ERRCODE = '23514', CONSTRAINT = 'publication_outputs_guard_ck';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER capture_receipts_guard BEFORE INSERT OR UPDATE ON ingestion.capture_receipts
FOR EACH ROW EXECUTE FUNCTION ingestion.guard_capture_receipt();
CREATE TRIGGER publication_outputs_guard BEFORE INSERT OR UPDATE ON ingestion.publication_outputs
FOR EACH ROW EXECUTE FUNCTION ingestion.guard_publication_output();
'''


def generate_capture_sql():
    parts = [SQL]
    for table in TABLES:
        operations = 'UPDATE OR DELETE OR TRUNCATE' if table in ('capture_delivery_aliases', 'capture_observations') else 'DELETE OR TRUNCATE'
        parts.append(f'CREATE TRIGGER {table}_immutable BEFORE {operations} ON ingestion.{table} '
                     'FOR EACH STATEMENT EXECUTE FUNCTION ingestion.guard_capture_immutable();')
    return '\n'.join(parts)
