#!/usr/bin/env python3
"""Load and validate model/implementation_status.yml, the implementation overlay.

The overlay records, for facts already modeled in architecture.yml and domain.yml, whether the
code implements them and where (evidence references). Generators read it only to mark diagrams.
"""

from __future__ import annotations

from pathlib import Path

try:
    from . import evidence
except ImportError:
    import evidence

ROOT = evidence.ROOT
OVERLAY = evidence.OVERLAY
STATUSES = evidence.STATUSES
SECTIONS = {("architecture", "elements"), ("architecture", "relationships"),
            ("domain", "entities"), ("domain", "attributes"), ("domain", "constraints")}
# Severity order used when one drawn edge stands for several modeled relationships.
ORDER = {"implemented": 0, "external": 0, "partial": 1, "divergent": 2, "not_implemented": 3}


def load(path=OVERLAY):
    path = Path(path)
    return evidence.load_overlay(path) if path.exists() else {}


def _entries(overlay, top, section):
    return ((overlay.get(top) or {}).get(section) or {})


def state(overlay, top, section, key):
    entry = _entries(overlay, top, section).get(key)
    return entry.get("status") if isinstance(entry, dict) else None


def element_state(overlay, eid):
    return state(overlay, "architecture", "elements", eid)


def relationship_state(overlay, rid):
    return state(overlay, "architecture", "relationships", rid)


def combined(states):
    """Worst-case state of several relationships drawn as one edge; mixed states read as partial."""
    known = [s for s in states if s]
    if not known:
        return None
    worst = max(known, key=lambda s: ORDER[s])
    if worst in {"not_implemented", "divergent"} and any(ORDER[s] == 0 for s in known):
        return "partial"
    return worst


def _domain_keys(domain):
    entities = {e["id"]: e for e in domain.get("entities", [])}
    attributes = {f"{e['id']}.{a['name']}" for e in entities.values() for a in e.get("attributes", [])}
    constraints = set()
    for e in entities.values():
        for c in e.get("constraints", []) or []:
            if isinstance(c, dict) and c.get("name"):
                constraints.add(c["name"])
    return set(entities), attributes, constraints


def validate(overlay, architecture, domain=None):
    errors = []
    if not overlay:
        return errors
    repos = overlay.get("repositories") or {}
    errors.extend(evidence.validate_repositories(repos))
    for top in ("architecture", "domain"):
        for section in (overlay.get(top) or {}):
            if (top, section) not in SECTIONS:
                errors.append(f"{top}.{section}: unknown overlay section")
    elements = {e["id"] for e in architecture.get("elements", [])}
    relationships = {r["id"] for r in architecture.get("relationships", [])}
    known = {("architecture", "elements"): elements, ("architecture", "relationships"): relationships}
    if domain is not None:
        entities, attributes, constraints = _domain_keys(domain)
        known.update({("domain", "entities"): entities, ("domain", "attributes"): attributes})
        # Named constraints from migrations need not exist in domain.yml (divergences are recorded here).
    for (top, section), ids in known.items():
        for key, entry in _entries(overlay, top, section).items():
            where = f"{top}.{section}.{key}"
            if key not in ids:
                errors.append(f"{where}: unknown model ID")
            errors.extend(_entry_errors(entry, repos, where))
    for key, entry in _entries(overlay, "domain", "constraints").items():
        errors.extend(_entry_errors(entry, repos, f"domain.constraints.{key}"))
    # Every architecture fact drawn in a view must carry an explicit state.
    for section, ids in (("elements", elements), ("relationships", relationships)):
        missing = sorted(ids - set(_entries(overlay, "architecture", section)))
        if missing:
            errors.append(f"architecture.{section}: missing implementation state for {', '.join(missing)}")
    if domain is not None:
        missing = sorted(known[("domain", "entities")] - set(_entries(overlay, "domain", "entities")))
        if missing:
            errors.append(f"domain.entities: missing implementation state for {', '.join(missing)}")
    return errors


def _entry_errors(entry, repos, where):
    if not isinstance(entry, dict):
        return [f"{where}: expected a mapping"]
    errors = []
    status = entry.get("status")
    if status not in STATUSES:
        errors.append(f"{where}: status must be one of {', '.join(STATUSES)}")
    if status in {"not_implemented", "external"}:
        if not str(entry.get("reason", "")).strip():
            errors.append(f"{where}: {status} requires a reason")
        if entry.get("evidence"):
            errors.extend(evidence.validate_refs(entry["evidence"], repos, where))
    else:
        errors.extend(evidence.validate_refs(entry.get("evidence"), repos, where))
    if status in {"partial", "divergent"} and not str(entry.get("note", "")).strip():
        errors.append(f"{where}: {status} requires a note")
    for field in ("decisions",):
        if field in entry and (not isinstance(entry[field], list) or not all(isinstance(v, str) and v for v in entry[field])):
            errors.append(f"{where}: {field} must be a list of identifiers")
    return errors
