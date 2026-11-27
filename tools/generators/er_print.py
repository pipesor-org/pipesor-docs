#!/usr/bin/env python3
"""Print-legible ER figures, one per bounded context (decision 6 of 27/11/2026).

The single ER (out/er.svg, D2) prints its text at about 1 pt on A4. These figures split it by
schema, or by a declared group of one schema, keep the columns that out/er.svg shows, mark the
implementation state from model/implementation_status.yml and are laid out by Graphviz so that
no text falls below MIN_POINTS once inserted on an A4 page. References to tables drawn in
another figure stay as text on the referencing column. SSOT: model/domain.yml.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
import subprocess
import sys

from graphviz import Digraph

try:
    from . import document_figures as df
    from . import implementation_status
    from .domain_model import ROOT, load_domain
    from .to_er_d2 import STATE_STYLE, attribute_state, visible_columns
except ImportError:
    import document_figures as df
    import implementation_status
    from domain_model import ROOT, load_domain
    from to_er_d2 import STATE_STYLE, attribute_state, visible_columns

OUT = ROOT / "out" / "doc"
BUILD = ROOT / "build" / "doc"
FONT = 14
# (figure id, title, schemas, explicit tables or None for every table of those schemas)
GROUPS = (
    ("er_ops_catalog", "ER — ops (1/2: catalog, executions and access grants)", ("ops",),
     ("repositories", "pipelines", "pipeline_executions", "execution_stages", "execution_event_receipts",
      "pipeline_access_grants")),
    ("er_ops_incidents", "ER — ops (2/2: incidents and the incident queue read model)", ("ops",),
     ("incidents", "incident_runs", "incident_diagnoses")),
    ("er_evidence_audit", "ER — evidence (Log/Event and Correlation) and audit", ("evidence", "audit"), None),
    ("er_diagnosis_intake", "ER — diagnosis (1/3: correlated context intake and diagnosis job queue)", ("diagnosis",),
     ("correlated_context_receipts", "diagnosis_jobs")),
    ("er_diagnosis", "ER — diagnosis (2/3: diagnoses, human reviews and summary outbox)", ("diagnosis",),
     ("diagnoses", "human_reviews", "incident_summary_outbox")),
    ("er_diagnosis_modeled", "ER — diagnosis (3/3: tables modeled but not created by any migration)", ("diagnosis",),
     ("recommendations", "diagnosis_evidence_links", "diagnosis_source_links")),
    ("er_knowledge", "ER — knowledge (RAG Knowledge Retrieval)", ("knowledge",), None),
    ("er_ingestion_connection", "ER — ingestion (1/2: GitHub connection, sign-in and consent)", ("ingestion",),
     ("github_connections", "github_connection_generations", "github_authorization_attempts",
      "github_credential_operations", "github_login_attempts", "consent_records")),
    ("er_ingestion_capture", "ER — ingestion (2/2: admission, capture and publication)", ("ingestion",),
     ("repository_admissions", "capture_workflow_scopes", "capture_receipts", "capture_delivery_aliases",
      "capture_observations", "publication_outputs")),
)
LEGEND = ("Solid arrow: intra-schema FK (N:1) · Dashed arrow: logical reference by ID, no physical FK · "
          "→ schema.table: reference to a table drawn in another figure · +N columns: see the data dictionary · "
          "Red dashed border: modeled, not implemented · Amber border: partially implemented "
          "(model/implementation_status.yml)")


def groups(model):
    """Resolve each figure's tables and check that every table appears exactly once."""
    resolved = []
    for gid, title, schemas, tables in GROUPS:
        members = [e for e in model["entities"] if e["schema"] in schemas and (tables is None or e["table"] in tables)]
        if tables is not None and len(members) != len(tables):
            raise ValueError(f"{gid}: unknown table in group")
        resolved.append((gid, title, members))
    drawn = [e["id"] for _, _, members in resolved for e in members]
    if sorted(drawn) != sorted(e["id"] for e in model["entities"]) or len(drawn) != len(set(drawn)):
        raise ValueError("ER print groups must cover every table exactly once")
    return resolved


def references(model, entity):
    """Column -> (target 'schema.table', kind) for single-column FKs and logical references."""
    found = {}
    prefix = f"{entity['schema']}.{entity['table']}."
    for r in model["relationships"]:
        if r["from"].startswith(prefix):
            found[r["from"][len(prefix):]] = (r["to"].rsplit(".", 1)[0], r["kind"])
    for fk in entity.get("foreign_keys", []):
        found.setdefault(fk["columns"][0], (fk["references"]["table"], "fk"))
    return found


def table_label(model, entity, overlay, here):
    state = implementation_status.state(overlay, "domain", "entities", entity["id"])
    colour = STATE_STYLE[state][0] if state in STATE_STYLE else "#1E293B"
    header = escape(entity["table"]) + (f'<BR/><FONT COLOR="{colour}">[{STATE_STYLE[state][1]}]</FONT>'
                                        if state in STATE_STYLE else "")
    rows = [f'<TR><TD COLSPAN="2" BGCOLOR="#E2E8F0"><B>{header}</B></TD></TR>']
    refs = references(model, entity)
    columns = visible_columns(entity, overlay)
    for c in columns:
        flags = []
        if c["pk"]:
            flags.append("PK")
        target = refs.get(c["name"])
        if target:
            arrow = "FK" if target[1] == "fk" else "ref."
            flags.append(arrow if target[0] in here else f"{arrow} → {target[0]}")
        if c["unique"]:
            flags.append("UQ")
        kind = c.get("enum", c["type"])
        col_state = attribute_state(overlay, entity, c)
        name = escape(c["name"])
        if col_state in STATE_STYLE:
            name = f'<FONT COLOR="{STATE_STYLE[col_state][0]}">{name} ({STATE_STYLE[col_state][1]})</FONT>'
        detail = escape(kind + (" · " + ", ".join(flags) if flags else ""))
        rows.append(f'<TR><TD ALIGN="LEFT" PORT="{escape(c["name"])}">{name}</TD>'
                    f'<TD ALIGN="LEFT"><FONT COLOR="#475569">{detail}</FONT></TD></TR>')
    hidden = len(entity["attributes"]) - len(columns)
    if hidden:
        rows.append(f'<TR><TD COLSPAN="2" ALIGN="LEFT"><FONT COLOR="#475569">+{hidden} columns</FONT></TD></TR>')
    return ('<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">' + "".join(rows) + "</TABLE>>"), state


def generate_dot(model, gid, title, members, overlay, rankdir):
    here = {f"{e['schema']}.{e['table']}" for e in members}
    graph = Digraph(gid, comment="GENERATED — sources: model/domain.yml + model/implementation_status.yml")
    graph.attr(rankdir=rankdir, bgcolor="white", pad="0.15", nodesep="0.35", ranksep="0.45", fontname="DejaVu Sans",
               fontsize=str(FONT), labelloc="b", labeljust="l",
               label="<" + df.lines(LEGEND, 90 if rankdir == "LR" else 60) + ">")
    graph.attr("node", shape="plain", fontname="DejaVu Sans", fontsize=str(FONT))
    graph.attr("edge", fontname="DejaVu Sans", fontsize=str(FONT), color="#475569", arrowsize="0.7")
    for e in members:
        label, state = table_label(model, e, overlay, here)
        colour = STATE_STYLE[state][0] if state in STATE_STYLE else "#64748B"
        style = "dashed" if state == "not_implemented" else "solid"
        graph.node(f"{e['schema']}.{e['table']}", f"<<TABLE BORDER=\"2\" COLOR=\"{colour}\" STYLE=\"{'dashed' if style == 'dashed' else 'rounded'}\" "
                   f"CELLBORDER=\"0\" CELLSPACING=\"0\"><TR><TD>{label[1:-1]}</TD></TR></TABLE>>")
    for e in members:
        for column, (target, kind) in references(model, e).items():
            if target in here and target != f"{e['schema']}.{e['table']}":
                graph.edge(f"{e['schema']}.{e['table']}", target, style="solid" if kind == "fk" else "dashed")
    return graph.source


def render(model, overlay, gid, title, members):
    BUILD.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    source, svg = BUILD / f"{gid}.dot", OUT / f"{gid}.svg"
    results = []
    for page in df.PAGES:
        for rankdir in ("TB", "LR"):
            source.write_text(generate_dot(model, gid, title, members, overlay, rankdir), encoding="utf-8")
            subprocess.run(["dot", "-Tsvg", str(source), "-o", str(svg)], check=True, cwd=ROOT)
            results.append(((page, rankdir), *df.printed_sizes(svg, page)))
    passing = [r for r in results if r[4] >= df.MIN_POINTS]
    if not passing:
        tried = "; ".join(f"{'/'.join(layout)}: {smallest:.1f} pt" for layout, *_, smallest in results)
        raise ValueError(f"{gid}: no layout reaches {df.MIN_POINTS} pt ({tried})")
    (page, rankdir), scale, width_cm, height_cm, smallest = max(passing, key=lambda r: (round(r[4], 1), -r[2] * r[3]))
    source.write_text(generate_dot(model, gid, title, members, overlay, rankdir), encoding="utf-8")
    subprocess.run(["dot", "-Tsvg", str(source), "-o", str(svg)], check=True, cwd=ROOT)
    df.set_svg_print_size(svg, width_cm, height_cm)
    png = svg.with_suffix(".png")
    subprocess.run(["dot", "-Tpng", f"-Gdpi={df.PNG_DPI * scale:.2f}", str(source), "-o", str(png)], check=True, cwd=ROOT)
    df.set_png_dpi(png, df.PNG_DPI)
    return {"id": gid, "title": title, "page": page, "legend": "en la figura", "width_cm": width_cm,
            "height_cm": height_cm, "min_pt": smallest}


def render_documents():
    model = load_domain()
    overlay = implementation_status.load()
    return [render(model, overlay, gid, title, members) for gid, title, members in groups(model)]


def main():
    if "--validate-only" in sys.argv:
        groups(load_domain())
        print("ER PRINT VALIDATION PASSED")
        return 0
    for row in render_documents():
        print(f"generated: out/doc/{row['id']}.svg ({row['page']}, {row['width_cm']:.1f}x{row['height_cm']:.1f} cm, "
              f"min {row['min_pt']:.1f} pt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
