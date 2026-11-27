#!/usr/bin/env python3
"""Render the single persistent-domain ER using D2 + ELK."""

import os
import subprocess

from domain_model import ROOT, find_tool, load_domain, main_guard, quote, write_generated
import implementation_status

# Implementation state from model/implementation_status.yml (colour and text, readable in monochrome).
STATE_STYLE = {"not_implemented": ("#B91C1C", "modeled, not implemented"),
               "partial": ("#B45309", "partially implemented"),
               "divergent": ("#6D28D9", "implemented differently")}


def attribute_state(overlay, entity, column):
    return implementation_status.state(overlay, "domain", "attributes", f"{entity['id']}.{column['name']}")


def visible_columns(entity, overlay=None):
    unique_columns = {c for u in entity.get("unique_constraints", []) for c in u["columns"]}
    composite_columns = {c for fk in entity.get("foreign_keys", []) for c in fk["columns"]}
    return [c for c in entity["attributes"] if c["er_visible"] or c["pk"] or c.get("fk")
            or attribute_state(overlay or {}, entity, c) in STATE_STYLE
            or c.get("logical_ref") or c["unique"] or c.get("enum")
            or c["name"] == "correlation_id" or c["name"] in unique_columns or c["name"] in composite_columns]


def generate_er(model, overlay=None):
    overlay = overlay if overlay is not None else implementation_status.load()
    # load_domain performs the shared checks before any generated file is written.
    if len(model["entities"]) > 40:
        raise ValueError("ER exceeds 40 tables")
    keys = {f"{e['schema']}.{e['table']}" for e in model["entities"]}
    for e in model["entities"]:
        if not any(c["pk"] for c in e["attributes"]):
            raise ValueError(f"{e['table']}: table has no PK")
    for r in model["relationships"]:
        if r["from"].rsplit(".", 1)[0] not in keys or r["to"].rsplit(".", 1)[0] not in keys:
            raise ValueError(f"{r['id']}: relationship points to nonexistent table")
    title = f"Persistent Model — One PostgreSQL Instance / {len(model['entities'])} Tables"
    lines = ["# GENERATED — DO NOT EDIT. SSOT: model/domain.yml", "direction: down",
             f"title: {quote(title)} {{",
             "  shape: text", "  style.font-size: 26", "  near: top-center", "}", ""]
    colors = ["#DDEBF7", "#E2F0D9", "#FFF2CC", "#E4DDF5", "#E7E6E6"]
    for i, schema in enumerate(model["schemas"]):
        color = colors[i % len(colors)]
        lines.extend([f"{schema['id']}: {quote(schema['id'])} {{", "  direction: right",
                      f"  style.fill: {quote(color)}"])
        for e in model["entities"]:
            if e["schema"] != schema["id"]:
                continue
            state = implementation_status.state(overlay, "domain", "entities", e["id"])
            label = e["table"] + (f" [{STATE_STYLE[state][1]}]" if state in STATE_STYLE else "")
            lines.extend([f"  {e['table']}: {quote(label)} {{", "    shape: sql_table",
                          "    style.font-size: 15"])
            if e["scope_basis"] == "ia_only":
                lines.append("    style.stroke-dash: 2")
            if state in STATE_STYLE:
                lines.extend([f"    style.stroke: {quote(STATE_STYLE[state][0])}", "    style.stroke-width: 4"])
                if state == "not_implemented":
                    lines.append("    style.stroke-dash: 6")
            unique_columns = {c for u in e.get("unique_constraints", []) for c in u["columns"]}
            composite_columns = {c for fk in e.get("foreign_keys", []) for c in fk["columns"]}
            partial_columns = {c for index in e.get("partial_unique_constraints", []) for c in index["columns"]}
            cols = visible_columns(e, overlay)
            for c in cols:
                constraints = []
                if c["pk"]: constraints.append("primary_key")
                if c.get("fk"): constraints.append("foreign_key")
                elif c["name"] in composite_columns: constraints.append("composite FK")
                if c["name"] in partial_columns: constraints.append("partial UQ; see dictionary")
                if c.get("logical_ref"): constraints.append("logical ID")
                if c["unique"]: constraints.append("unique")
                elif c["name"] in unique_columns: constraints.append("composite UQ")
                typ = c.get("enum", c["type"])
                if attribute_state(overlay, e, c) in STATE_STYLE:
                    typ += " · " + STATE_STYLE[attribute_state(overlay, e, c)][1]
                row = f"    {c['name']}: {quote(typ)}"
                if constraints:
                    row += " {constraint: [" + "; ".join(quote(c) for c in constraints) + "]}"
                lines.append(row)
            hidden = len(e["attributes"]) - len(cols)
            if hidden:
                lines.append(f"    {quote('+' + str(hidden) + ' columns')}: \"see dictionary\"")
            lines.append("  }")
        lines.extend(["}", ""])
    for r in model["relationships"]:
        logical = r["kind"] == "logical_ref"
        label = "logical ref." if logical else "N:1"
        lines.append(f"{r['from']} -> {r['to']}: {quote(label)} {{")
        lines.extend(["  style.stroke-dash: 5" if logical else "  style.stroke-dash: 0",
                      '  style.stroke: "#586174"', "}"])
    for entity in model['entities']:
        for fk in entity.get('foreign_keys', []):
            left = f"{entity['schema']}.{entity['table']}.{fk['columns'][0]}"
            right = f"{fk['references']['table']}.{fk['references']['columns'][0]}"
            kind = "composite FK deferred: " if fk.get('initially_deferred') else "composite FK: "
            label = kind + ', '.join(fk['columns']) + ' → ' + ', '.join(fk['references']['columns'])
            lines.append(f'{left} -> {right}: {quote(label)}')
    lines.extend(["", 'legend: "Legend\\nSolid line: intra-schema FK (N:1)\\nDashed line: logical reference by ID, no physical FK\\nDotted border: pipeline_access_grants (IA-only / inferred)\\nComposite UQ: member of a composite unique key\\n+N columns: see data dictionary\\nNo cross-context ORM navigation' + state_legend(model, overlay) + '" {',
                  "  shape: text", "  style.font-size: 16", "  near: bottom-center", "}"])
    return "\n".join(lines)


def state_legend(model, overlay):
    if not overlay:
        return ""
    states = [implementation_status.state(overlay, "domain", "entities", e["id"]) for e in model["entities"]]
    built = sum(1 for s in states if s != "not_implemented")
    return ("\\nImplementation state (model/implementation_status.yml, " + str(overlay.get("evidence_cutoff", "")) +
            f"): {built} of {len(states)} tables implemented by migrations" +
            "\\nRed dashed border: modeled, not implemented · Amber border: partially implemented" +
            "\\n'· modeled, not implemented' after a type: column absent from the migrations")


def main():
    model = load_domain()
    write_generated("build/er.d2", generate_er(model))
    tool = find_tool("d2")
    env = dict(os.environ)
    if env.get("DEBUG") not in {None, "0", "1", "false", "true"}:
        env.pop("DEBUG")
    result = subprocess.run([str(tool), "--layout=elk", str(ROOT / "build/er.d2"),
                             str(ROOT / "out/er.svg")], cwd=ROOT,
                            capture_output=True, text=True, check=False, env=env)
    if result.returncode:
        raise RuntimeError("D2 failed: " + (result.stderr or result.stdout))
    if not (ROOT / "out/er.svg").is_file() or not (ROOT / "out/er.svg").stat().st_size:
        raise RuntimeError("D2 produced no/nonempty ER SVG")
    print("[domain] generated out/er.svg (D2 + ELK)")
    if result.stderr.strip():
        print(result.stderr.strip())


if __name__ == "__main__":
    raise SystemExit(main_guard(main))
