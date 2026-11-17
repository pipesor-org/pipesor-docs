#!/usr/bin/env python3
"""Export generated DBML using installed dbml2sql; add unexpressible constraints."""

import os
import re
import subprocess

from domain_model import ROOT, find_tool, load_domain, main_guard, write_generated
from to_dbml import generate_dbml
from connector_constraints import generate_lifecycle_sql
from capture_constraints import generate_capture_sql
from correlation_constraints import generate_correlation_sql


ORIGIN_CONSTRAINTS = """
-- DD-002: at most one ORIGIN, including concurrent writes.
CREATE UNIQUE INDEX incident_runs_one_origin_uq
ON ops.incident_runs (incident_id) WHERE role = 'ORIGIN';

-- DD-002: exactly one failed ORIGIN, consistent with the incident pipeline.
-- No extra workflow policy is imposed on VERIFICATION runs.
-- Deferred so incident + ORIGIN can be inserted in the same transaction.
CREATE FUNCTION ops.assert_incident_runs(p_incident uuid) RETURNS void
LANGUAGE plpgsql SET search_path = pg_catalog, ops AS $$
DECLARE
    p_pipeline uuid;
BEGIN
    SELECT pipeline_id INTO p_pipeline FROM ops.incidents
      WHERE id = p_incident FOR UPDATE;
    IF NOT FOUND THEN RETURN; END IF;
    IF (SELECT count(*) FROM ops.incident_runs
        WHERE incident_id = p_incident AND role = 'ORIGIN') <> 1 THEN
        RAISE EXCEPTION 'Incident % requires exactly one ORIGIN', p_incident
          USING ERRCODE = '23514';
    END IF;
    IF EXISTS (
        SELECT 1 FROM ops.incident_runs ir
        JOIN ops.pipeline_executions pe ON pe.id = ir.execution_id
        WHERE ir.incident_id = p_incident AND ir.role = 'ORIGIN' AND
          (pe.pipeline_id <> p_pipeline OR pe.failed IS NOT TRUE)
    ) THEN
        RAISE EXCEPTION 'Incident % requires a failed ORIGIN consistent with its pipeline', p_incident
          USING ERRCODE = '23514';
    END IF;
END;
$$;

CREATE FUNCTION ops.check_incident_runs() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, ops AS $$
DECLARE
    linked_incident uuid;
BEGIN
    IF TG_TABLE_NAME = 'incidents' THEN
        PERFORM ops.assert_incident_runs(NEW.id);
    ELSIF TG_TABLE_NAME = 'incident_runs' THEN
        IF TG_OP <> 'INSERT' THEN
            PERFORM ops.assert_incident_runs(OLD.incident_id);
        END IF;
        IF TG_OP <> 'DELETE' THEN
            PERFORM ops.assert_incident_runs(NEW.incident_id);
        END IF;
    ELSE
        FOR linked_incident IN SELECT incident_id FROM ops.incident_runs
            WHERE execution_id = NEW.id ORDER BY incident_id LOOP
            PERFORM ops.assert_incident_runs(linked_incident);
        END LOOP;
    END IF;
    RETURN NULL;
END;
$$;

CREATE CONSTRAINT TRIGGER incidents_origin_required
AFTER INSERT OR UPDATE ON ops.incidents DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION ops.check_incident_runs();

CREATE CONSTRAINT TRIGGER incident_runs_origin_required
AFTER INSERT OR UPDATE OR DELETE ON ops.incident_runs DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION ops.check_incident_runs();

CREATE CONSTRAINT TRIGGER execution_origin_stays_failed
AFTER UPDATE ON ops.pipeline_executions DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION ops.check_incident_runs();

-- TRUNCATE bypasses row/constraint triggers; reject it to preserve the invariant.
CREATE FUNCTION ops.reject_incident_runs_truncate() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'Use transactional DELETE for incident run records'
      USING ERRCODE = '23514';
END;
$$;
CREATE TRIGGER incident_runs_no_truncate BEFORE TRUNCATE ON ops.incident_runs
FOR EACH STATEMENT EXECUTE FUNCTION ops.reject_incident_runs_truncate();
"""

APPEND_ONLY = """
-- DD-003: each status/content change creates a new immutable version.
-- Retention maintenance needs a future, explicitly controlled procedure; no purge job.
CREATE FUNCTION diagnosis.reject_diagnoses_mutation() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'diagnoses is append-only; insert a new version'
      USING ERRCODE = '23514';
END;
$$;
CREATE TRIGGER diagnoses_append_only
BEFORE UPDATE OR DELETE OR TRUNCATE ON diagnosis.diagnoses
FOR EACH STATEMENT EXECUTE FUNCTION diagnosis.reject_diagnoses_mutation();
"""


RECEIPT_SIGNALS = r'''
-- DD-024: only the typed protected signal array belongs to the durable receipt.
CREATE FUNCTION diagnosis.valid_correlated_signals(signals jsonb, evidence_ids uuid[]) RETURNS boolean
LANGUAGE plpgsql IMMUTABLE SET search_path = pg_catalog AS $$
DECLARE item jsonb; member uuid; seen uuid[] := ARRAY[]::uuid[];
BEGIN
    IF signals IS NULL OR evidence_ids IS NULL OR jsonb_typeof(signals) <> 'array' THEN
        RETURN false;
    END IF;
    IF array_ndims(evidence_ids) IS DISTINCT FROM 1 OR array_lower(evidence_ids,1) IS DISTINCT FROM 1
       OR cardinality(evidence_ids) = 0 OR jsonb_array_length(signals) <> cardinality(evidence_ids) THEN
        RETURN false;
    END IF;
    FOR item IN SELECT value FROM jsonb_array_elements(signals) LOOP
        IF jsonb_typeof(item) <> 'object' THEN RETURN false; END IF;
        IF (SELECT count(*) FROM jsonb_object_keys(item)) <> 6
           OR NOT item ?& ARRAY['evidence_id','origin_context_id','correlation_id','stage','summary','content']
           OR EXISTS (SELECT 1 FROM jsonb_each(item) field WHERE jsonb_typeof(field.value) <> 'string') THEN
            RETURN false;
        END IF;
        member := (item->>'evidence_id')::uuid;
        PERFORM (item->>'origin_context_id')::uuid;
        IF member = ANY(seen) OR NOT member = ANY(evidence_ids)
           OR (item->>'correlation_id') !~ '^[A-Za-z0-9._:-]{1,128}$'
           OR (item->>'stage') NOT IN ('BUILD','TESTING','QUALITY_GATE','DEPLOYMENT','CONTAINER','INFRASTRUCTURE')
           OR (item->>'summary') !~ '[^[:space:]]' OR (item->>'content') !~ '[^[:space:]]' THEN
            RETURN false;
        END IF;
        seen := array_append(seen, member);
    END LOOP;
    RETURN (SELECT count(DISTINCT id) FROM unnest(evidence_ids) id) = cardinality(evidence_ids)
           AND NOT EXISTS (SELECT 1 FROM unnest(evidence_ids) id WHERE id IS NULL);
EXCEPTION WHEN invalid_text_representation THEN
    RETURN false;
END; $$;
ALTER TABLE diagnosis.correlated_context_receipts
ADD CONSTRAINT correlated_context_receipts_signals_membership_ck
CHECK (diagnosis.valid_correlated_signals(signals, evidence_ids));

CREATE FUNCTION diagnosis.reject_correlated_receipt_mutation() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$ BEGIN
    RAISE EXCEPTION 'Correlation context receipt is append-only'
      USING ERRCODE = '23514';
END; $$;
CREATE TRIGGER correlated_context_receipts_append_only
BEFORE UPDATE OR DELETE OR TRUNCATE ON diagnosis.correlated_context_receipts
FOR EACH STATEMENT EXECUTE FUNCTION diagnosis.reject_correlated_receipt_mutation();
'''


def generate_extras(model):
    constraints = {c for e in model["entities"] for c in e.get("domain_constraints", [])}
    supported = {"at_most_one_origin", "exactly_one_failed_origin", "origin_pipeline_consistency", "append_only", "connector_lifecycle", "capture_lifecycle", "correlation_lifecycle"}
    if constraints - supported:
        raise ValueError(f"Unsupported domain constraints: {sorted(constraints - supported)}")
    parts = ["-- GENERATED — DO NOT EDIT. SSOT: model/domain.yml; DD-002 / DD-003."]
    origin = supported - {"append_only", "connector_lifecycle", "capture_lifecycle", "correlation_lifecycle"}
    if constraints & origin:
        if not origin <= constraints:
            raise ValueError("ORIGIN constraints must be declared together")
        parts.append(ORIGIN_CONSTRAINTS)
    if "append_only" in constraints:
        parts.append(APPEND_ONLY)
    if any(e["schema"] == "diagnosis" and e["table"] == "correlated_context_receipts" for e in model["entities"]):
        parts.append(RECEIPT_SIGNALS)
    for entity in model['entities']:
        table = f"{entity['schema']}.{entity['table']}"
        for index in entity.get('partial_unique_constraints', []):
            parts.append(f"CREATE UNIQUE INDEX {index['name']} ON {table} ({', '.join(index['columns'])}) WHERE {index['where']};")
        for fk in entity.get('foreign_keys', []):
            if fk.get('deferrable'):
                mode = 'DEFERRED' if fk.get('initially_deferred') else 'IMMEDIATE'
                parts.append(f"ALTER TABLE {table} ALTER CONSTRAINT {fk['name']} DEFERRABLE INITIALLY {mode};")
    if 'connector_lifecycle' in constraints:
        parts.append(generate_lifecycle_sql())
    if "capture_lifecycle" in constraints:
        parts.append(generate_capture_sql())
    if "correlation_lifecycle" in constraints:
        parts.append(generate_correlation_sql())
    return "\n".join(parts)


def validate_export(sql, model):
    """Reject empty/partial successful CLI output before replacing artifacts.

    This is an exporter contract, not a PostgreSQL syntax/security validator.
    Actual DDL behavior is exercised by make test-postgres.
    """
    tables = set(re.findall(r'CREATE TABLE "(\w+)"\."(\w+)"', sql))
    expected = {(e['schema'], e['table']) for e in model['entities']}
    if tables != expected:
        raise ValueError('dbml2sql returned incomplete/unexpected CREATE TABLE output')
    for entity in model['entities']:
        pk = [a['name'] for a in entity['attributes'] if a['pk']]
        if len(pk) > 1:
            columns = ', '.join(f'"{name}"' for name in pk)
            if f'PRIMARY KEY ({columns})' not in sql:
                raise ValueError(f'dbml2sql omitted composite primary key {entity["table"]}')
        for fk in entity.get('foreign_keys', []):
            if f'ADD CONSTRAINT "{fk["name"]}" FOREIGN KEY' not in sql:
                raise ValueError(f'dbml2sql omitted composite FK {fk["name"]}')
        for check in entity.get('checks', []):
            if f'CONSTRAINT "{check["name"]}" CHECK' not in sql:
                raise ValueError(f'dbml2sql omitted CHECK {check["name"]}')
        for constraint in entity.get('unique_constraints', []):
            if f'CREATE UNIQUE INDEX "{constraint["name"]}"' not in sql:
                raise ValueError(f'dbml2sql omitted unique index {constraint["name"]}')


def main():
    model = load_domain()
    dbml = ROOT / "model/db.dbml"
    if not dbml.exists() or dbml.read_text(encoding="utf-8") != generate_dbml(model).rstrip() + "\n":
        raise ValueError("DBML is stale; run make dbml before make sql")
    tool = find_tool("dbml2sql")
    env = {**os.environ, "PATH": str(tool.parent) + os.pathsep + os.environ.get("PATH", "")}
    result = subprocess.run([str(tool), str(dbml), "--postgres"], cwd=ROOT,
                            capture_output=True, text=True, env=env, check=False)
    if result.returncode:
        raise RuntimeError("dbml2sql failed: " + (result.stderr or result.stdout))
    validate_export(result.stdout, model)
    sql = re.sub(r'^CREATE SCHEMA(?: IF NOT EXISTS)? "?[A-Za-z_][A-Za-z0-9_]*"?;\s*',
                 '', result.stdout, flags=re.M)
    preamble = ["-- GENERATED — DO NOT EDIT. model/domain.yml → model/db.dbml → dbml2sql.",
                *[f"CREATE SCHEMA IF NOT EXISTS {s['id']};" for s in model["schemas"]],
                "CREATE EXTENSION IF NOT EXISTS vector;", ""]
    write_generated("build/schema.sql", "\n".join(preamble) + sql)
    write_generated("build/extras.sql", generate_extras(model))
    print(f"[domain] SQL exporter: {tool}")


if __name__ == "__main__":
    raise SystemExit(main_guard(main))
