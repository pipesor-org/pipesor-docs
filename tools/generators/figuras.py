#!/usr/bin/env python3
"""Document figures for the thesis and the Capstone (out/figuras/), APA 7 and Word.

Source: model/document_figures.yml, which selects and labels in Spanish facts already modeled in
architecture.yml, design.yml, domain.yml, sequence_presentation.yml and deployment_presentation.yml.
Implementation states come from model/implementation_status.yml or design.yml, never from the
figure model. Each figure is one PNG (300 ppp) that fits one A4 page at 9 pt or more, without
title, notes, legend or technical references inside the image; the README of each folder carries
the APA title, note, call paragraph, alternative text and simplifications.

``--validate-only`` checks the model; the default run renders, writes the READMEs and the contact
sheet and checks every output (sizes, 300 ppp, text size, README entries, clean intermediates).
Intermediate DOT, PlantUML and SVG files stay in build/figuras/ (ignored by Git).
"""

from __future__ import annotations

import argparse
import os
from html import escape
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET
import zlib

import yaml

try:
    from . import c4, evidence, implementation_status
except ImportError:
    import c4
    import evidence
    import implementation_status

ROOT = evidence.ROOT
MODEL = ROOT / "model" / "document_figures.yml"
OUT = ROOT / "out" / "figuras"
BUILD = ROOT / "build" / "figuras"
JAR = ROOT / "tools" / "plantuml.jar"
PAGES = {"portrait": (15.9, 19.0), "landscape": (24.6, 13.0)}
MIN_POINTS = 9.0
PNG_DPI = 300
FONT = 10
CM_PER_POINT = 2.54 / 72
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SPLIT = re.compile(r"(?:-p\d+|-parte|-\d+|_\d+)$")
FORBIDDEN = (re.compile(r"repo:"), re.compile(r"rel_"), re.compile(r"Generated", re.I),
             re.compile(r"(?<![#\w])[0-9a-f]{7,40}(?!\w)"))
KINDS = ("c4_context", "c4_container", "c4_component", "classes", "data", "sequence", "deployment")
DOMAIN_STEREOTYPES = {"Aggregate", "Entity", "ValueObject", "Enum", "Record"}

# Three states at most, by colour and line style.
IMPLEMENTED, PARTIAL, PROPOSED = "implementado", "parcial", "propuesto"
STATE = {"implemented": IMPLEMENTED, "external": IMPLEMENTED, "partial": PARTIAL, "divergent": PARTIAL,
         "not_implemented": PROPOSED, "deployed": IMPLEMENTED, "proposed": PROPOSED, "tbd": PROPOSED}
STYLE = {IMPLEMENTED: ("#334155", "solid"), PARTIAL: ("#B45309", "dashed"), PROPOSED: ("#B91C1C", "dotted")}
NOTE_WORDS = {PARTIAL: "ámbar", PROPOSED: "roj"}
FILL = {"system": "#DBEAFE", "internal": "#EFF6FF", "external": "#F1F5F9", "datastore": "#ECFDF5",
        "person": "#E2E8F0", "class": "#FFFBEB", "table": "#FFFFFF"}
ORDER = {IMPLEMENTED: 0, PARTIAL: 1, PROPOSED: 2}


def worst(states):
    states = [s for s in states if s]
    if not states:
        return IMPLEMENTED
    top = max(states, key=lambda s: ORDER[s])
    # A drawn edge that joins implemented and unimplemented relationships is partial.
    return PARTIAL if top == PROPOSED and any(s != PROPOSED for s in states) else top


def words(text):
    return len(str(text).split())


def wrap(text, width):
    return "<BR/>".join(escape(line) for line in textwrap.wrap(str(text), width, break_long_words=False)) or ""


def load(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def models():
    m = {"figures": load(MODEL)}
    for key, name in (("architecture", "architecture.yml"), ("design", "design.yml"), ("domain", "domain.yml"),
                      ("sequences", "sequence_presentation.yml"), ("deployment", "deployment_presentation.yml")):
        m[key] = load(ROOT / "model" / name)
    m["overlay"] = implementation_status.load()
    return m


# ----------------------------------------------------------------------------------------------------
# Validation and selection: each kind returns a spec (nodes, edges, groups) with derived states.

class Invalid(ValueError):
    pass


def check(condition, message):
    if not condition:
        raise Invalid(message)


def common(figure, folders):
    fid = figure.get("id", "?")
    check(NAME.fullmatch(fid) and not SPLIT.search(fid), f"{fid}: file name must be kebab-case without part numbers")
    check(figure.get("folder") in folders, f"{fid}: unknown folder")
    check(figure.get("kind") in KINDS, f"{fid}: unknown kind")
    check(figure.get("orientation") in PAGES, f"{fid}: orientation must be portrait or landscape")
    destination = figure.get("destination") or {}
    documents = destination.get("documents") or []
    check(documents and set(documents) <= {"Memoria", "Capstone"}, f"{fid}: destination documents")
    check(str(destination.get("section", "")).strip(), f"{fid}: destination section")
    if figure["orientation"] == "landscape":
        check(documents == ["Capstone"], f"{fid}: landscape is only for Capstone-only figures")
    title = str(figure.get("title", ""))
    check(title and title[0].isupper() and not title.endswith("."), f"{fid}: APA title in sentence case, no period")
    note = str(figure.get("note", ""))
    check(note.startswith("*Nota.* Elaboración propia a partir de"), f"{fid}: note must start with «*Nota.* Elaboración propia a partir de»")
    check(words(note) <= 60, f"{fid}: note has {words(note)} words (max 60)")
    check("pipesor-docs (Anexo C)" in note, f"{fid}: note must point to pipesor-docs (Anexo C)")
    check(not re.search(r"https?://|sharepoint|onedrive", note, re.I), f"{fid}: no URLs in the note")
    call = str(figure.get("call", ""))
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", call.strip()) if s]
    check(2 <= len(sentences) <= 4, f"{fid}: call paragraph needs 2 to 4 sentences")
    check(re.search(r"\b[Ll]a Figura N\b", call), f"{fid}: call paragraph must mention «la Figura N»")
    alt = str(figure.get("alt", ""))
    check(alt and len(alt) <= 125, f"{fid}: alternative text must have 1 to 125 characters ({len(alt)})")
    check(figure.get("simplifications"), f"{fid}: list the simplifications")


def label_check(fid, text, limit, what):
    check(text and words(text) <= limit, f"{fid}: {what} «{text}» exceeds {limit} words")


def lift(architecture):
    """Model endpoint → drawn endpoint: pgvector is the PostgreSQL instance; components lift to parents."""
    elements = {e["id"]: e for e in architecture["elements"]}

    def endpoint(eid, drawn):
        if eid in drawn:
            return eid
        if eid == "pgvector_knowledge_store" and "postgresql_operational_store" in drawn:
            return "postgresql_operational_store"
        parent = elements.get(eid, {}).get("parent")
        return parent if parent in drawn else eid
    return endpoint


def rel_state(m, rid):
    return STATE[implementation_status.relationship_state(m["overlay"], rid) or "implemented"]


def element_state(m, eid):
    return STATE[implementation_status.element_state(m["overlay"], eid) or "implemented"]


def element_kind(element):
    if element["kind"] == "actor":
        return "person"
    if element["kind"] == "datastore":
        return "datastore"
    return "external" if element["kind"] == "external_system" else "internal"


def spec_c4_context(figure, m):
    fid, architecture = figure["id"], m["architecture"]
    projection = next(p for p in c4.prepare(architecture)[0] if p.view["id"] == figure["view"])
    system = architecture["architecture"]["id"]
    expected = {e["id"] for e in projection.outside} | {system}
    check(set(figure["nodes"]) == expected, f"{fid}: nodes must be the context view's actors, systems and the system")
    groups = {(r["from"].replace("aiops", system), r["to"].replace("aiops", system)): r for r in projection.relationships}
    drawn = {(e["from"], e["to"]) for e in figure["edges"]}
    check(drawn == set(groups), f"{fid}: edges must match the aggregated context relationships exactly")
    elements = {e["id"]: e for e in architecture["elements"]}
    nodes = []
    for eid, item in figure["nodes"].items():
        label_check(fid, item.get("text"), 10, "description")
        kind = "system" if eid == system else element_kind(elements[eid])
        nodes.append({"id": eid, "name": item["name"], "text": item.get("text", ""), "kind": kind,
                      "state": IMPLEMENTED if eid == system else element_state(m, eid)})
    edges = []
    for e in figure["edges"]:
        label_check(fid, e["label"], 6, "relationship label")
        ids = groups[(e["from"], e["to"])].get("ids", [])
        edges.append({"from": e["from"], "to": e["to"], "label": e["label"], "state": worst(rel_state(m, r) for r in ids)})
    return {"nodes": nodes, "edges": edges, "clusters": []}


def spec_c4_graph(figure, m, *, component):
    fid, architecture = figure["id"], m["architecture"]
    elements = {e["id"]: e for e in architecture["elements"]}
    relationships = {r["id"]: r for r in architecture["relationships"]}
    drawn = set(figure["nodes"])
    endpoint = lift(architecture)
    if component:
        projection = next(p for p in c4.prepare(architecture)[0] if p.view["id"] == figure["view"])
        allowed = {e["id"] for e in projection.inside + projection.outside}
        check(drawn <= allowed, f"{fid}: nodes must belong to view {figure['view']}")
        inside = [e for e in figure["nodes"] if elements[e]["kind"] == "component"]
        check(1 <= len(inside) <= 8, f"{fid}: 1 to 8 components")
        allowed_rels = {r["id"] for r in projection.relationships}
    nodes, clusters = [], []
    group_members = {}
    for eid, item in figure["nodes"].items():
        check(eid in elements, f"{fid}: unknown element {eid}")
        element = elements[eid]
        if element["kind"] in {"container", "datastore", "component"} and (component is False or element["kind"] == "component"):
            label_check(fid, item.get("text"), 10, "description")
            check("\n" not in str(item.get("tech", "")), f"{fid}: technology in one line")
        kind = "internal" if element["kind"] == "component" else element_kind(element)
        if component and element["kind"] == "container":
            kind = "external"  # neighbours of a component view lie outside its container
        if element["kind"] == "datastore":
            kind = "datastore"
        nodes.append({"id": eid, "name": item["name"], "tech": item.get("tech", ""), "text": item.get("text", ""),
                      "kind": kind, "state": element_state(m, eid),
                      "cluster": "boundary" if (component and element["kind"] == "component") or
                      (not component and element["kind"] != "actor" and element["kind"] != "external_system") else None,
                      "group": item.get("group")})
        if item.get("group"):
            group_members.setdefault(item["group"], set()).add(eid)
    edges = []
    for e in figure["edges"]:
        rels = e["relationships"]
        label_check(fid, e["label"], 6, "relationship label")
        for rid in rels:
            check(rid in relationships, f"{fid}: unknown relationship {rid}")
            if component:
                check(rid in allowed_rels, f"{fid}: {rid} is not drawn in view {figure['view']}")
        state = worst(rel_state(m, rid) for rid in rels)
        if e.get("from_group"):
            members = group_members.get(e["from_group"], set())
            for rid in rels:
                r = relationships[rid]
                check(endpoint(r["from"], drawn) in members and endpoint(r["to"], drawn) == e["to"],
                      f"{fid}: {rid} does not go from group {e['from_group']} to {e['to']}")
            edges.append({"from_group": e["from_group"], "to": e["to"], "label": e["label"], "state": state})
            continue
        ends = {(endpoint(relationships[rid]["from"], drawn), endpoint(relationships[rid]["to"], drawn)) for rid in rels}
        check(len(ends) == 1, f"{fid}: relationships of one edge must share their endpoints")
        src, dst = ends.pop()
        check(src in drawn and dst in drawn, f"{fid}: edge {src} → {dst} uses an undrawn node")
        edges.append({"from": src, "to": dst, "label": e["label"], "state": state})
    if not component:
        clusters = [("boundary", figure.get("boundary", "Sistema"))]
        if group_members:
            clusters.append(("services", figure.get("services_group", "")))
    else:
        clusters = [("boundary", figure["container_name"])]
    return {"nodes": nodes, "edges": edges, "clusters": clusters}


def class_state(item):
    impl = item.get("implementation") or {}
    status = impl.get("status") or ("implemented" if item.get("status") == "implemented" else "not_implemented")
    return STATE[status]


def spec_classes(figure, m):
    fid, design = figure["id"], m["design"]
    classes = {c["id"]: c for c in design["classes"]}
    chosen = figure["classes"]
    check(1 <= len(chosen) <= 8, f"{fid}: 1 to 8 classes")
    nodes = []
    for cid, item in chosen.items():
        check(cid in classes, f"{fid}: unknown class {cid}")
        cls = classes[cid]
        check(cls["stereotype"] in DOMAIN_STEREOTYPES, f"{fid}: {cid} is a {cls['stereotype']}; only domain types")
        container = cls.get("container", design["design_rules"].get("container"))
        check(container in (figure["container"], None) or cls.get("status") == "proposed",
              f"{fid}: {cid} belongs to {container}")
        attributes = {a["name"]: a for a in cls.get("attributes", [])}
        methods = {mt["name"]: mt for mt in cls.get("methods", [])}
        names = item.get("attributes", []) or []
        check(len(names) <= 6 and set(names) <= set(attributes), f"{fid}: {cid} attributes (max 6, existing)")
        calls = item.get("methods", []) or []
        check(len(calls) <= 3 and set(calls) <= set(methods), f"{fid}: {cid} methods (max 3, existing)")
        values = cls.get("values", [])
        nodes.append({"id": cid, "name": cls["name"].split(".")[-1], "stereotype": cls["stereotype"],
                      "attributes": [f"{n}: {attributes[n]['type']}" for n in names],
                      "methods": [f"{n}()" for n in calls],
                      "values": values[:6] + (["…"] if len(values) > 6 else []),
                      "state": class_state(cls), "kind": "class"})
    labels = figure.get("relationship_labels", {})
    edges, used = [], set()
    for rel in design["relationships"]:
        if rel["from"] in chosen and rel["to"] in chosen:
            key = f"{rel['from']}>{rel['to']}"
            check(key in labels, f"{fid}: Spanish label missing for {key}")
            used.add(key)
            edges.append({"from": rel["from"], "to": rel["to"], "label": labels[key], "type": rel["type"],
                          "ownership": rel.get("ownership"), "multiplicity": rel.get("multiplicity")})
    check(set(labels) == used, f"{fid}: labels for undrawn relationships: {sorted(set(labels) - used)}")
    return {"nodes": nodes, "edges": edges, "clusters": []}


def spec_data(figure, m):
    fid, domain, overlay = figure["id"], m["domain"], m["overlay"]
    limit = int(figure.get("max_columns", 8))
    check(1 <= limit <= 8, f"{fid}: max_columns between 1 and 8")
    schemas = figure["schemas"]
    tables = [e for e in domain["entities"] if e["schema"] in schemas]
    check(tables, f"{fid}: no tables")
    if figure.get("table_order"):
        # Presentation only: the order that fills the grid rows.
        check(sorted(figure["table_order"]) == sorted(e["table"] for e in tables), f"{fid}: table_order must list every table once")
        tables.sort(key=lambda e: figure["table_order"].index(e["table"]))
    here = {f"{e['schema']}.{e['table']}" for e in tables}
    refs = {}
    for r in domain["relationships"]:
        table, column = r["from"].rsplit(".", 1)
        refs.setdefault(table, {})[column] = (r["to"].rsplit(".", 1)[0], r["kind"])
    nodes, edges = [], []
    for e in tables:
        key = f"{e['schema']}.{e['table']}"
        mine = dict(refs.get(key, {}))
        for fk in e.get("foreign_keys", []):
            for column in fk["columns"]:
                mine.setdefault(column, (fk["references"]["table"], "fk"))
        state_of = lambda name: STATE[implementation_status.state(overlay, "domain", "attributes", f"{e['id']}.{name}") or "implemented"]
        keys = [a for a in e["attributes"] if a["pk"] or a["name"] in mine]
        rest = [a for a in e["attributes"] if a not in keys]
        rest.sort(key=lambda a: (state_of(a["name"]) == IMPLEMENTED, not a.get("er_visible"), not a.get("unique")))
        shown = keys + rest[:max(0, limit - len(keys))]
        rows = []
        for a in shown:
            flags = ["PK"] if a["pk"] else []
            target = mine.get(a["name"])
            if target:
                flags.append("FK" if target[1] == "fk" else "ref.")
            rows.append({"name": a["name"], "type": a.get("enum", a["type"]), "flags": " · ".join(flags),
                         "state": state_of(a["name"])})
        hidden = len(e["attributes"]) - len(shown)
        # The schema is in the APA title; multi-schema figures keep it in the table name.
        nodes.append({"id": key, "name": e["table"] if len(schemas) == 1 else key, "rows": rows, "hidden": hidden, "kind": "table",
                      "state": STATE[implementation_status.state(overlay, "domain", "entities", e["id"]) or "implemented"]})
        for target in dict.fromkeys(t for t, kind in mine.values() if kind == "fk" and t in here and t != key):
            edges.append({"from": key, "to": target, "label": "", "state": IMPLEMENTED})
    return {"nodes": nodes, "edges": edges, "clusters": []}


def walk(steps, found, depth=0):
    for step in steps:
        if "message" in step:
            found["messages"].append(step["message"])
        if "fragment" in step:
            found["fragments"] += 1
            for branch in step["fragment"]["branches"]:
                walk(branch["steps"], found, depth + 1)
    return found


def spec_sequence(figure, m):
    fid, architecture = figure["id"], m["architecture"]
    check(figure["sequence"] in {s["id"] for s in m["sequences"]["sequences"]}, f"{fid}: unknown technical sequence")
    elements = {e["id"]: e for e in architecture["elements"]}
    relationships = {r["id"]: r for r in architecture["relationships"]}
    participants = {p["id"]: p for p in figure["participants"]}
    check(len(participants) <= 7, f"{fid}: at most 7 lifelines")
    for p in participants.values():
        check(p["element"] in elements, f"{fid}: unknown element {p['element']}")
        check(elements[p["element"]]["kind"] != "component", f"{fid}: lifelines group by container, not component")
    found = walk(figure["steps"], {"messages": [], "fragments": 0})
    check(len(found["messages"]) <= 15, f"{fid}: {len(found['messages'])} messages (max 15)")
    check(found["fragments"] <= 2, f"{fid}: at most 2 alt/opt/loop fragments")
    endpoint = lift(architecture)
    repos = m["overlay"].get("repositories", {})
    for message in found["messages"]:
        label_check(fid, message["text"], 8, "message")
        check(message["from"] in participants and message["to"] in participants, f"{fid}: unknown participant")
        mine = {participants[message["from"]]["element"], participants[message["to"]]["element"]}
        if message.get("relationships"):
            # A message through an intermediary that has no lifeline: a chain of modeled relationships.
            chain = [relationships.get(rid) for rid in message["relationships"]]
            check(all(chain) and len(chain) >= 2, f"{fid}: «{message['text']}» needs two or more known relationships")
            check(all(a["to"] == b["from"] for a, b in zip(chain, chain[1:])), f"{fid}: «{message['text']}» chain is broken")
            check(endpoint(chain[0]["from"], mine) == participants[message["from"]]["element"]
                  and endpoint(chain[-1]["to"], mine) == participants[message["to"]]["element"],
                  f"{fid}: «{message['text']}» chain does not join its participants")
            message["_state"] = worst(rel_state(m, rid) for rid in message["relationships"])
        elif message.get("relationship"):
            r = relationships.get(message["relationship"])
            check(r, f"{fid}: unknown relationship {message['relationship']}")
            ends = {endpoint(r["from"], mine), endpoint(r["to"], mine)}
            check(mine <= ends if len(mine) == 1 else ends == mine,
                  f"{fid}: «{message['text']}» does not match {message['relationship']}")
            message["_state"] = rel_state(m, message["relationship"])
        else:
            check(message.get("state") in STATE and not evidence.validate_refs(message.get("evidence"), repos, fid),
                  f"{fid}: «{message['text']}» needs a relationship or state and evidence")
            message["_state"] = STATE[message["state"]]
    for fragment_kind in re.findall(r"kind:\s*(\w+)", yaml.safe_dump(figure["steps"])):
        check(fragment_kind in {"alt", "opt", "loop"}, f"{fid}: fragment kind {fragment_kind}")
    return {"participants": participants, "steps": figure["steps"], "elements": elements,
            "states": [msg["_state"] for msg in found["messages"]]}


def spec_deployment(figure, m):
    fid = figure["id"]
    source = next((f for f in m["deployment"]["figures"] if f["id"] == figure["figure"]), None)
    check(source, f"{fid}: unknown deployment figure")
    by_id = {n["id"]: n for n in source["nodes"]}
    groups = figure.get("groups", {})
    nodes, merged_into = [], {}
    for nid, item in figure["nodes"].items():
        check(nid in by_id, f"{fid}: unknown deployment node {nid}")
        check(item.get("group") in (None, *groups), f"{fid}: unknown group for {nid}")
        if item.get("text"):
            label_check(fid, item["text"], 10, "description")
        for other in item.get("merge", []):
            check(other in by_id, f"{fid}: unknown merged node {other}")
            merged_into[other] = nid
        src = by_id[nid]
        kind = "datastore" if src.get("element") in {"postgresql_operational_store", "azure_key_vault"} else (
            "external" if not src.get("group") and src.get("element") not in {None} and nid.startswith("n_") else "internal")
        state = worst([STATE[src["state"]], *(STATE[by_id[o]["state"]] for o in item.get("merge", []))])
        nodes.append({"id": nid, "name": item["name"], "text": item.get("text", ""), "kind": kind,
                      "state": state, "group": item.get("group"), "source_group": src.get("group")})
    source_edges = {}
    for e in source.get("edges", []):
        source_edges.setdefault((merged_into.get(e["from"], e["from"]), merged_into.get(e["to"], e["to"])), e)
    edges = []
    states = {n["id"]: n["state"] for n in nodes}
    for e in figure["edges"]:
        label_check(fid, e["label"], 6, "relationship label")
        src, dst = e.get("from") or e.get("from_group"), e.get("to") or e.get("to_group")
        for end, group in ((src, e.get("from_group")), (dst, e.get("to_group"))):
            check(end in (groups if group else states), f"{fid}: unknown edge end {end}")
        known = source_edges.get((src, dst))
        state = STATE[known["state"]] if known else worst([states.get(src), states.get(dst)])
        edges.append({**e, "state": state})
    return {"nodes": nodes, "edges": edges, "groups": groups, "source": source}


SPECS = {"c4_context": spec_c4_context, "c4_container": lambda f, m: spec_c4_graph(f, m, component=False),
         "c4_component": lambda f, m: spec_c4_graph(f, m, component=True), "classes": spec_classes,
         "data": spec_data, "sequence": spec_sequence, "deployment": spec_deployment}


def figure_states(kind, spec):
    if kind == "sequence":
        return set(spec["states"])
    states = {n["state"] for n in spec["nodes"]} | {e.get("state", IMPLEMENTED) for e in spec["edges"]}
    if kind == "data":
        states |= {row["state"] for n in spec["nodes"] for row in n["rows"]}
    return states


def validate(m):
    doc = m["figures"]
    folders = doc.get("folders") or {}
    errors, specs, seen = [], {}, set()
    for figure in doc.get("figures", []):
        fid = figure.get("id", "?")
        try:
            check(fid not in seen, f"{fid}: duplicate figure")
            seen.add(fid)
            common(figure, folders)
            spec = SPECS[figure["kind"]](figure, m)
            states = figure_states(figure["kind"], spec)
            for state, word in NOTE_WORDS.items():
                mentioned = word in figure["note"].lower()
                check(mentioned == (state in states),
                      f"{fid}: the note {'mentions' if mentioned else 'omits'} the «{state}» style "
                      f"({'absent from' if mentioned else 'present in'} the figure)")
            specs[fid] = spec
        except (Invalid, KeyError, TypeError, StopIteration) as error:
            errors.append(str(error) if isinstance(error, Invalid) else f"{fid}: {type(error).__name__}: {error}")
    orders = [f.get("order") for f in doc.get("figures", [])]
    if sorted(orders) != list(range(1, len(orders) + 1)):
        errors.append("figure order must run 1..N without gaps")
    return errors, specs


# ----------------------------------------------------------------------------------------------------
# Rendering.

def node_html(node):
    colour, style = STYLE[node["state"]]
    rows = [f'<TR><TD><B>{wrap(node["name"], 20)}</B></TD></TR>']
    if node.get("tech"):
        rows.append(f'<TR><TD><FONT COLOR="#334155">[{escape(node["tech"])}]</FONT></TD></TR>')
    if node.get("text"):
        rows.append(f'<TR><TD><FONT COLOR="#1F2937">{wrap(node["text"], 22)}</FONT></TD></TR>')
    return "<<TABLE BORDER=\"0\" CELLBORDER=\"0\" CELLSPACING=\"1\" CELLPADDING=\"1\">" + "".join(rows) + "</TABLE>>"


def class_html(node):
    colour, style = STYLE[node["state"]]
    border_style = {"solid": "ROUNDED", "dashed": "DASHED", "dotted": "DOTTED"}[style]
    head = f'<TR><TD BGCOLOR="{FILL["class"]}"><FONT COLOR="#334155">«{escape(node["stereotype"])}»</FONT><BR/><B>{escape(node["name"])}</B></TD></TR>'
    body = node["values"] if node["stereotype"] == "Enum" else node["attributes"]
    rows = [head]
    if body:
        rows.append('<TR><TD ALIGN="LEFT" BALIGN="LEFT">' + "<BR/>".join(escape(x) for x in body) + "</TD></TR>")
    if node["methods"]:
        rows.append('<TR><TD ALIGN="LEFT" BALIGN="LEFT">' + "<BR/>".join(escape(x) for x in node["methods"]) + "</TD></TR>")
    return (f'<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4" COLOR="{colour}" '
            f'STYLE="{border_style}" BGCOLOR="white">' + "".join(rows) + "</TABLE>>")


def table_html(node):
    colour, style = STYLE[node["state"]]
    border_style = {"solid": "ROUNDED", "dashed": "DASHED", "dotted": "DOTTED"}[style]
    rows = [f'<TR><TD COLSPAN="2" BGCOLOR="#E2E8F0"><B>{escape(node["name"])}</B></TD></TR>']
    for row in node["rows"]:
        name = escape(row["name"])
        if row["state"] != IMPLEMENTED:
            name = f'<FONT COLOR="{STYLE[row["state"]][0]}">{name}</FONT>'
        # Types stay in the data dictionary; the figure keeps names and key roles.
        detail = escape(row["flags"])
        detail = f'<FONT COLOR="#475569">{detail}</FONT>' if detail else " "
        rows.append(f'<TR><TD ALIGN="LEFT">{name}</TD><TD ALIGN="LEFT">{detail}</TD></TR>')
    if node["hidden"]:
        rows.append(f'<TR><TD COLSPAN="2" ALIGN="LEFT"><FONT COLOR="#475569">+{node["hidden"]} columnas</FONT></TD></TR>')
    return (f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1" COLOR="{colour}" '
            f'STYLE="{border_style}" BGCOLOR="white">' + "".join(rows) + "</TABLE>>")


def dot_node(node, alias):
    colour, style = STYLE[node["state"]]
    kind = node["kind"]
    if kind == "class":
        return f'{alias} [shape=plain label={class_html(node)}]'
    if kind == "table":
        return f'{alias} [shape=plain label={table_html(node)}]'
    shape = {"datastore": "cylinder", "person": "box"}.get(kind, "box")
    styles = ["filled"] + ([] if kind == "datastore" else ["rounded"]) + ([] if style == "solid" else [style])
    width = "0.6"
    return (f'{alias} [shape={shape} style="{",".join(styles)}" fillcolor="{FILL.get(kind, FILL["internal"])}" '
            f'color="{colour}" penwidth={2.0 if style != "solid" else 1.2} width={width} label={node_html(node)}]')


def dot_edge(edge, src, dst, extra=""):
    colour, style = STYLE[edge.get("state", IMPLEMENTED)]
    label = f' label=<{wrap(edge["label"], 16)}>' if edge.get("label") else ""
    return (f'{src} -> {dst} [color="{colour}" fontcolor="#1F2937" style={style} '
            f'penwidth={1.8 if style != "solid" else 1.1}{label}{extra}]')


def generate_dot(figure, spec, rankdir, pack=None, grid=None):
    kind = figure["kind"]
    alias = {n["id"]: f"n{index}" for index, n in enumerate(spec["nodes"])}
    packing = f' pack=true packmode="{pack}"' if pack else ""
    lines = ["digraph figura {", f'  graph [rankdir={rankdir} fontname="DejaVu Sans" fontsize={FONT} bgcolor="white" '
             f'pad=0.05 nodesep={0.1 if kind == "data" else 0.18} ranksep=0.3 compound=true newrank=true splines=true{packing}]',
             f'  node [fontname="DejaVu Sans" fontsize={FONT} margin="0.05,0.03"]',
             f'  edge [fontname="DejaVu Sans" fontsize={FONT} arrowsize=0.7]']
    if kind in {"c4_container", "c4_component"}:
        boundary = dict(spec["clusters"]).get("boundary")
        inside = [n for n in spec["nodes"] if n.get("cluster") == "boundary"]
        services = [n for n in inside if n.get("group") == "services"]
        # boundary «none»: colour alone separates the prototype (blue) from external elements (grey).
        lines.append(f'  subgraph cluster_boundary {{ label=<{escape(boundary)}> labeljust=l '
                     'style="dashed,rounded" color="#2563EB" fontcolor="#1E3A8A"' if boundary != "none" else "  {")
        if services:
            lines.append(f'    subgraph cluster_services {{ label=<{escape(dict(spec["clusters"])["services"])}> labeljust=l '
                         'style="rounded" color="#94A3B8" fontcolor="#334155"')
            lines += ["      " + dot_node(n, alias[n["id"]]) for n in services]
            lines.append("    }")
        lines += ["    " + dot_node(n, alias[n["id"]]) for n in inside if n not in services]
        lines.append("  }")
        lines += ["  " + dot_node(n, alias[n["id"]]) for n in spec["nodes"] if n not in inside]
    elif kind == "deployment":
        groups = spec["groups"]
        tree = {"azure": None, "environment": "azure", "external": "environment", "internal": "environment",
                "service": None, "iac": None, "environments": None}

        def members(group):
            return [n for n in spec["nodes"] if n.get("group") == group or (
                group == "azure" and not n.get("group") and n.get("source_group"))]

        def emit(group, depth):
            if group not in groups:
                return
            pad = "  " * depth
            lines.append(f'{pad}subgraph cluster_{group} {{ label=<{escape(groups[group])}> labeljust=l '
                         'style="dashed,rounded" color="#64748B" fontcolor="#1F2937"')
            for child in [g for g, parent in tree.items() if parent == group]:
                emit(child, depth + 1)
            lines.extend(pad + "  " + dot_node(n, alias[n["id"]]) for n in members(group))
            lines.append(pad + "}")
        # A group whose parent group is not drawn becomes a top-level frame.
        for group in [g for g, parent in tree.items() if parent is None or parent not in groups]:
            emit(group, 1)
        placed = {n["id"] for g in groups for n in members(g)}
        lines += ["  " + dot_node(n, alias[n["id"]]) for n in spec["nodes"] if n["id"] not in placed]
    else:
        lines += ["  " + dot_node(n, alias[n["id"]]) for n in spec["nodes"]]
    if grid:
        # Tables in rows of `grid`: invisible edges order the rows; foreign keys do not constrain ranks.
        ids = [alias[n["id"]] for n in spec["nodes"]]
        rows = [ids[i:i + grid] for i in range(0, len(ids), grid)]
        lines += ["  { rank=same; " + "; ".join(row) + " }" for row in rows]
        lines += [f"  {a} -> {b} [style=invis]" for upper, lower in zip(rows, rows[1:]) for a, b in zip(upper, lower)]
    for group in figure.get("same_rank", []):
        check(all(n in alias for n in group), f"{figure['id']}: same_rank uses an undrawn node")
        lines.append("  { rank=same; " + "; ".join(alias[n] for n in group) + " }")
    for upper, lower in figure.get("stack", []):
        # Presentation only: an invisible edge places `upper` above `lower`.
        check(upper in alias and lower in alias, f"{figure['id']}: stack uses an undrawn node")
        lines.append(f"  {alias[upper]} -> {alias[lower]} [style=invis]")
    for e in spec["edges"]:
        if kind == "classes":
            colour = STYLE[IMPLEMENTED][0]
            if e["type"] == "realizes":
                attrs = 'style=dashed arrowhead=onormal'
            elif e.get("ownership") == "composition":
                attrs = 'dir=both arrowtail=diamond arrowhead=none'
            else:
                attrs = 'arrowhead=vee'
            text = e["label"] + (f" ({e['multiplicity']})" if e.get("multiplicity") else "")
            lines.append(f'  {alias[e["from"]]} -> {alias[e["to"]]} [color="{colour}" {attrs} label=<{wrap(text, 14)}>]')
            continue
        if kind == "data":
            lines.append(f'  {alias[e["from"]]} -> {alias[e["to"]]} [color="#475569" arrowhead=vee'
                         f'{" constraint=false" if grid else ""}]')
            continue
        extra = ""
        src = alias.get(e.get("from"))
        dst = alias.get(e.get("to"))
        if e.get("from_group"):
            group = e["from_group"]
            member = next(n for n in spec["nodes"] if n.get("group") == group)
            src, extra = alias[member["id"]], f" ltail=cluster_{group}"
        if e.get("to_group"):
            group = e["to_group"]
            member = next(n for n in spec["nodes"] if n.get("group") == group or n.get("group") in
                          {"external", "internal"} and group == "environment")
            dst, extra = alias[member["id"]], extra + f" lhead=cluster_{group}"
        lines.append("  " + dot_edge(e, src, dst, extra))
    lines.append("}")
    declared = set(re.findall(r"^\s*(n\d+) \[", "\n".join(lines), re.M))
    used = set(re.findall(r"\b(n\d+) -> (n\d+)", "\n".join(lines)) and
               [a for pair in re.findall(r"\b(n\d+) -> (n\d+)", "\n".join(lines)) for a in pair])
    check(set(alias.values()) <= declared and used <= declared,
          f"{figure['id']}: undeclared nodes {sorted((set(alias.values()) | used) - declared)}")
    return "\n".join(lines) + "\n"


def participant_line(p, element):
    kind = element_kind(element)
    keyword = {"person": "actor", "datastore": "database"}.get(kind, "participant")
    return f'{keyword} "{p["name"]}" as {p["id"]} {FILL["internal"] if kind == "internal" else FILL["external"] if kind != "datastore" else FILL["datastore"]}'


def puml_steps(steps, lines):
    for step in steps:
        if "message" in step:
            msg = step["message"]
            colour, style = STYLE[msg["_state"]]
            # Replies are already dashed: partial messages are amber and bold, proposed ones dotted red.
            style = {"dashed": "bold"}.get(style, style)
            arrow_style = f"[{colour}" + ("" if style == "solid" else f",{style}") + "]"
            kind = msg.get("style", "sync")
            head = ">>" if kind == "async" else ">"
            body = "--" if kind == "reply" else "-"
            arrow = f"{body[0]}{arrow_style}{body[1:]}{head}" if body == "--" else f"-{arrow_style}{head}"
            lines.append(f'{msg["from"]} {arrow} {msg["to"]} : {msg["text"]}')
        if "fragment" in step:
            fragment = step["fragment"]
            for index, branch in enumerate(fragment["branches"]):
                lines.append(f'{fragment["kind"] if index == 0 else "else"} {branch["guard"]}')
                puml_steps(branch["steps"], lines)
            lines.append("end")


def generate_puml(figure, spec):
    lines = ["@startuml", "skinparam defaultFontName DejaVu Sans", f"skinparam defaultFontSize {FONT}",
             "skinparam shadowing false", f"skinparam maxMessageSize {figure.get('max_message_width', 95)}", "skinparam sequenceMessageAlign center",
             "skinparam sequenceArrowThickness 1.2",
             "skinparam sequenceLifeLineBorderColor #94A3B8", "skinparam sequenceGroupBorderColor #64748B",
             "skinparam ParticipantBorderColor #475569", "skinparam ActorBorderColor #475569",
             "skinparam DatabaseBorderColor #059669", "hide footbox",
             "<style>", "participant { Padding 2", "Margin 2 }", "actor { Padding 2 }", "database { Padding 2 }", "</style>"]
    for p in figure["participants"]:
        lines.append(participant_line(p, spec["elements"][p["element"]]))
    puml_steps(spec["steps"], lines)
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def clean_svg(path):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<\?plantuml[^>]*\?>", "", text)
    path.write_text(text, encoding="utf-8")


def measure(svg, orientation):
    root = ET.parse(svg).getroot()
    _, _, width, height = (float(v) for v in root.get("viewBox").split())
    sizes = [float(el.get("font-size")) for el in root.iter()
             if el.tag.endswith("text") and el.get("font-size") and "".join(el.itertext()).strip()]
    page_w, page_h = PAGES[orientation]
    scale = min(page_w / (width * CM_PER_POINT), page_h / (height * CM_PER_POINT), 1.0)
    return scale, width * CM_PER_POINT * scale, height * CM_PER_POINT * scale, min(sizes) * scale, width


def set_png_dpi(png, dpi=PNG_DPI):
    data = png.read_bytes()
    signature, rest = data[:8], data[8:]
    chunks, offset = [], 0
    while offset < len(rest):
        length, kind = struct.unpack(">I4s", rest[offset:offset + 8])
        chunks.append((kind, rest[offset + 8:offset + 8 + length]))
        offset += 12 + length
    ppm = round(dpi / 0.0254)
    payload = struct.pack(">IIB", ppm, ppm, 1)
    chunks = [c for c in chunks if c[0] != b"pHYs"]
    chunks.insert(1, (b"pHYs", payload))
    out = signature + b"".join(struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
                               for kind, body in chunks)
    png.write_bytes(out)


def png_info(png):
    data = png.read_bytes()
    width, height = struct.unpack(">II", data[16:24])
    offset, dpi = 8, None
    while offset < len(data):
        length, kind = struct.unpack(">I4s", data[offset:offset + 8])
        if kind == b"pHYs":
            ppm_x, ppm_y, unit = struct.unpack(">IIB", data[offset + 8:offset + 17])
            dpi = round(ppm_x * 0.0254) if unit == 1 else None
        offset += 12 + length
    return width, height, dpi


def run(command, cwd=ROOT):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{' '.join(map(str, command[:3]))} failed: {result.stderr or result.stdout}")


def render(figure, spec, out=OUT, build=BUILD):
    folder_out, folder_build = Path(out) / figure["folder"], Path(build) / figure["folder"]
    folder_out.mkdir(parents=True, exist_ok=True)
    folder_build.mkdir(parents=True, exist_ok=True)
    fid, orientation = figure["id"], figure["orientation"]
    png = folder_out / f"{fid}.png"
    if figure["kind"] == "sequence":
        source = folder_build / f"{fid}.puml"
        source.write_text(generate_puml(figure, spec), encoding="utf-8")
        run(["java", "-Djava.awt.headless=true", "-jar", str(JAR), "-charset", "UTF-8", "-tsvg", "-nometadata", "-failfast2", str(source)])
        svg = source.with_suffix(".svg")
        clean_svg(svg)
        scale, width_cm, height_cm, smallest, view_width = measure(svg, orientation)
        factor = (width_cm / 2.54 * PNG_DPI) / view_width
        raster = folder_build / "png"
        raster.mkdir(exist_ok=True)
        scaled = raster / f"{fid}.puml"
        scaled.write_text(source.read_text(encoding="utf-8").replace("@startuml", f"@startuml\nscale {factor:.4f}", 1), encoding="utf-8")
        run(["java", "-Djava.awt.headless=true", "-jar", str(JAR), "-charset", "UTF-8", "-tpng", "-nometadata", str(scaled)])
        shutil.move(str(raster / f"{fid}.png"), png)
        choice = "TB"
    else:
        results = []
        # Disconnected classes or tables can be packed in columns; clustered views keep dot's layout.
        packs = (None, "array_c1", "array_2", "array_c2") if figure["kind"] in {"classes", "data"} else (None,)
        grids = (None, 2, 3, 4) if figure["kind"] == "data" else (None,)
        for rankdir, pack, grid in [(r, p, g) for r in figure.get("rankdir", ["TB", "LR"]) for p in packs for g in grids
                                    if not (p and g) and not (g and r == "LR")]:
            if True:
                tag = f"{rankdir}{'-' + pack if pack else ''}{f'-grid{grid}' if grid else ''}"
                source = folder_build / f"{fid}.{tag}.dot"
                source.write_text(generate_dot(figure, spec, rankdir, pack, grid), encoding="utf-8")
                svg = source.with_suffix(".svg")
                run(["dot", "-Tsvg", str(source), "-o", str(svg)])
                clean_svg(svg)
                results.append((measure(svg, orientation), tag, source, svg))
        (scale, width_cm, height_cm, smallest, _), choice, source, svg = max(
            results, key=lambda r: (round(r[0][3], 1), -r[0][1] * r[0][2]))
        final = folder_build / f"{fid}.dot"
        shutil.copyfile(source, final)
        shutil.copyfile(svg, final.with_suffix(".svg"))
        for _, _, src, s in results:
            src.unlink(missing_ok=True)
            s.unlink(missing_ok=True)
        run(["dot", "-Tpng", f"-Gdpi={PNG_DPI * scale:.3f}", str(final), "-o", str(png)])
    set_png_dpi(png)
    return {"id": fid, "png": png, "orientation": orientation, "width_cm": width_cm, "height_cm": height_cm,
            "min_pt": smallest, "layout": choice}


# ----------------------------------------------------------------------------------------------------
# READMEs, contact sheet and output checks.

ORIENTATION_ES = {"portrait": "vertical", "landscape": "apaisada"}


def es(value):
    """One decimal with a decimal comma, as Spanish text expects."""
    return f"{value:.1f}".replace(".", ",")


def readme_folder(doc, folder, figures, rows):
    lines = [f"# {doc['folders'][folder]}", "",
             "Figuras documentales generadas desde `model/document_figures.yml`; no editar a mano. Cada PNG está a "
             "300 ppp y se inserta al ancho indicado, sin reescalar. En Word: «Figura N» en negrita, el título en "
             "cursiva en la línea siguiente, la imagen y la nota debajo. El número lo asigna el documento.", ""]
    for figure in figures:
        row = rows[figure["id"]]
        dest = figure["destination"]
        lines += [f"## {figure['title']}", "",
                  f"- **Archivo:** [`{figure['id']}.png`]({figure['id']}.png)",
                  f"- **Orientación:** {ORIENTATION_ES[figure['orientation']]} · **ancho de inserción:** "
                  f"{es(row['width_cm'])} cm (alto {es(row['height_cm'])} cm) · texto mínimo {es(row['min_pt'])} pt",
                  f"- **Destino:** {' y '.join(dest['documents'])} · {dest['section']}",
                  f"- **Título APA:** *{figure['title']}*", "",
                  f"**Nota APA.** {figure['note'].replace('*Nota.* ', '', 1)}", "",
                  "*Texto para la nota en Word:* " + figure["note"], "",
                  f"**Párrafo de llamada.** {figure['call']}", "",
                  f"**Texto alternativo.** {figure['alt']}", "",
                  "**Simplificaciones respecto de la vista completa:**", ""]
        lines += [f"- {item}" for item in figure["simplifications"]]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def readme_root(doc, rows):
    lines = ["# Figuras para la Memoria de Tesis y el Capstone", "",
             "Figuras documentales generadas desde `model/document_figures.yml`; no editar a mano. Son un segundo "
             "nivel, pensado para Word con formato APA 7: una figura por página, PNG a 300 ppp, texto de 9 pt o más "
             "al ancho indicado y etiquetas en español. El título, la nota, el párrafo de llamada y el texto "
             "alternativo de cada figura están en el README de su carpeta. Las vistas técnicas completas siguen en "
             "`out/` y la trazabilidad en `out/trazabilidad.md`.", "",
             "Estados de implementación, explicados en la nota de cada figura: línea o borde continuo, implementado; "
             "ámbar discontinuo, parcial (implementado en parte o de otra forma); rojo punteado, propuesto (modelado, "
             "sin implementar). En las secuencias la línea discontinua indica una respuesta, por lo que un mensaje "
             "parcial se dibuja en ámbar grueso.", "",
             "| Orden | Figura | Carpeta | Documento | Sección propuesta | Orientación | Ancho (cm) |",
             "|---|---|---|---|---|---|---|"]
    for figure in sorted(doc["figures"], key=lambda f: f["order"]):
        row = rows[figure["id"]]
        lines.append(f"| {figure['order']} | [{figure['id']}.png]({figure['folder']}/{figure['id']}.png) — "
                     f"{figure['title']} | [{figure['folder']}]({figure['folder']}/README.md) | "
                     f"{' y '.join(figure['destination']['documents'])} | {figure['destination']['section']} | "
                     f"{ORIENTATION_ES[figure['orientation']]} | {es(row['width_cm'])} |")
    lines += ["", "[Hoja de contactos](hoja-de-contactos.png): miniaturas de todas las figuras para revisión; no se inserta "
              "en los documentos.", ""]
    return "\n".join(lines)


def contact_sheet(doc, rows, out, build):
    figures = sorted(doc["figures"], key=lambda f: f["order"])
    build = Path(build).resolve()
    cells, per_row = [], 5
    for figure in figures:
        png = rows[figure["id"]]["png"]
        cells.append(f'<TD><TABLE BORDER="0" CELLSPACING="2"><TR><TD FIXEDSIZE="TRUE" WIDTH="230" HEIGHT="275">'
                     f'<IMG SCALE="TRUE" SRC="{escape(os.path.relpath(png.resolve(), build))}"/></TD></TR><TR><TD><FONT POINT-SIZE="11">'
                     f'{figure["order"]}. {escape(figure["id"])}</FONT></TD></TR></TABLE></TD>')
    rows_html = "".join("<TR>" + "".join(cells[i:i + per_row]) + "</TR>" for i in range(0, len(cells), per_row))
    source = build / "hoja-de-contactos.dot"  # image paths are relative to build, where dot runs
    source.write_text('digraph hoja { graph [bgcolor="white" pad=0.2] node [shape=plain fontname="DejaVu Sans"]\n'
                      f'  sheet [label=<<TABLE BORDER="0" CELLSPACING="10">{rows_html}</TABLE>>]\n}}\n', encoding="utf-8")
    target = Path(out).resolve() / "hoja-de-contactos.png"
    run(["dot", "-Tpng", "-Gdpi=110", source.name, "-o", str(target)], cwd=build)


def check_outputs(doc, out=OUT, build=BUILD, rows=None):
    """Errors in out/figuras and build/figuras against the document-figure rules."""
    out, build, errors = Path(out), Path(build), []
    figures = {f["id"]: f for f in doc["figures"]}
    pngs = sorted(p for p in out.rglob("*.png") if p.name != "hoja-de-contactos.png")
    if any(out.rglob("*.svg")):
        errors.append("out/figuras must not contain SVG files")
    stems = [p.stem for p in pngs]
    if sorted(stems) != sorted(figures):
        errors.append(f"PNG set differs from the model: {sorted(set(stems) ^ set(figures))}")
    readmes = {p.parent: p.read_text(encoding="utf-8") for p in out.rglob("README.md")}
    for png in pngs:
        figure = figures.get(png.stem)
        if not figure:
            continue
        if SPLIT.search(png.stem) or not NAME.fullmatch(png.stem):
            errors.append(f"{png.name}: split or non kebab-case name")
        if png.parent.name != figure["folder"]:
            errors.append(f"{png.name}: wrong folder")
        if f"({png.name})" not in readmes.get(png.parent, ""):
            errors.append(f"{png.name}: no entry in {png.parent.name}/README.md")
        width, height, dpi = png_info(png)
        max_w, max_h = PAGES[figure["orientation"]]
        if dpi != PNG_DPI:
            errors.append(f"{png.name}: {dpi} ppp instead of {PNG_DPI}")
        if width > max_w / 2.54 * PNG_DPI + 3 or height > max_h / 2.54 * PNG_DPI + 3:
            errors.append(f"{png.name}: {width}×{height} px exceeds {max_w}×{max_h} cm at {PNG_DPI} ppp")
        svg = build / figure["folder"] / f"{png.stem}.svg"
        if svg.exists():
            _, _, _, smallest, _ = measure(svg, figure["orientation"])
            if round(smallest, 1) < MIN_POINTS:
                errors.append(f"{png.name}: smallest text {smallest:.1f} pt < {MIN_POINTS}")
            text = svg.read_text(encoding="utf-8")
            for pattern in FORBIDDEN:
                if pattern.search(text):
                    errors.append(f"{svg.name}: intermediate SVG contains {pattern.pattern!r}")
        else:
            errors.append(f"{png.name}: missing intermediate SVG {svg.relative_to(build.parent.parent) if build.is_absolute() else svg}")
    if not (out / "README.md").exists():
        errors.append("out/figuras/README.md is missing")
    return errors


def generate(out=OUT, build=BUILD):
    m = models()
    errors, specs = validate(m)
    if errors:
        raise Invalid("invalid document figures:\n" + "\n".join(errors))
    doc = m["figures"]
    out, build = Path(out), Path(build)
    if out.exists():
        shutil.rmtree(out)
    if build.exists():
        shutil.rmtree(build)
    out.mkdir(parents=True)
    build.mkdir(parents=True)
    rows = {}
    for figure in sorted(doc["figures"], key=lambda f: f["order"]):
        rows[figure["id"]] = render(figure, specs[figure["id"]], out, build)
    for folder in doc["folders"]:
        mine = sorted((f for f in doc["figures"] if f["folder"] == folder), key=lambda f: f["order"])
        (out / folder).mkdir(exist_ok=True)
        (out / folder / "README.md").write_text(readme_folder(doc, folder, mine, rows), encoding="utf-8")
    (out / "README.md").write_text(readme_root(doc, rows), encoding="utf-8")
    contact_sheet(doc, rows, out, build)
    problems = check_outputs(doc, out, build, rows)
    if problems:
        raise Invalid("document figure checks failed:\n" + "\n".join(problems))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.validate_only:
            errors, specs = validate(models())
            if errors:
                raise Invalid("\n".join(errors))
            print(f"DOCUMENT FIGURES VALIDATION PASSED ({len(specs)} figures)")
            return 0
        rows = generate()
    except (Invalid, RuntimeError, OSError, yaml.YAMLError) as error:
        print(f"document figures failed: {error}", file=sys.stderr)
        return 1
    for row in sorted(rows.values(), key=lambda r: r["png"].parent.name):
        print(f"generated: {row['png'].relative_to(ROOT)} ({row['orientation']}, {row['width_cm']:.1f}×"
              f"{row['height_cm']:.1f} cm, min {row['min_pt']:.1f} pt, {row['layout']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
