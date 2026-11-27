#!/usr/bin/env python3
"""Deployment views of Pipesor: the dev runtime in Azure, and environments and delivery.

``model/deployment_presentation.yml`` declares each figure. Every node, resource group and edge
cites an existing element or relationship of ``model/architecture.yml`` or is marked as an
implementation the model does not have (``implementation_only``), always with ``repo:path:line``
evidence at the revisions pinned in ``model/implementation_status.yml`` and a state:

- ``deployed``: seen by the read-only observation of 27/11/2026 (``deployment_observation``);
- ``implemented``: in IaC or code, but not observed or not active;
- ``proposed``: declared in documents, or a Terraform root without workloads;
- ``tbd``: not defined anywhere; carries its reason instead of evidence.

The views do not add architecture, approve a deployment or prove runtime behaviour. The
divergence between ``deployment.mvp_preparation.deployment_authorized`` and the observed dev
environment is drawn as a note and never resolved here.

``main()`` writes build/<id>.dot, out/<id>.svg and out/despliegue_guia.md; ``--document`` also
writes the A4 print variants (out/doc/<id>.svg and .png); ``--validate-only`` only validates.
``render_documents()`` is the entry point for the document figures generator.
"""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re
import subprocess
import textwrap

import yaml
from graphviz import Digraph

try:
    from . import evidence
except ImportError:
    import evidence

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "model" / "deployment_presentation.yml"
ARCHITECTURE = ROOT / "model" / "architecture.yml"
OVERLAY = ROOT / "model" / "implementation_status.yml"
BUILD = ROOT / "build"
OUT = ROOT / "out"
DOC_OUT = OUT / "doc"
GUIDE = OUT / "despliegue_guia.md"

STATES = ("deployed", "implemented", "proposed", "tbd")
CATEGORIES = ("prototype", "external", "persistence", "platform")
KIND_CATEGORY = {"actor": "external", "external_system": "external", "datastore": "persistence",
                 "container": "prototype", "component": "prototype"}
GROUP_KINDS = ("resource", "reading")
OBSERVATION_META = ("environment", "observed_at", "method")
FIGURE_ID = re.compile(r"^deploy_[a-z][a-z0-9_]*$")
LOCAL_ID = re.compile(r"^[a-z][a-z0-9_]*$")
SOURCE = re.compile(r"^(?P<path>(?:docs|model)/[^:\s]+):(?P<start>[1-9]\d*)(?:-(?P<end>[1-9]\d*))?$")

NODE_KEYS = {"id", "name", "element", "also_elements", "runs", "implementation_only", "category", "group",
             "details", "facts", "state", "observation", "observed_status", "model_fact", "evidence", "sources", "reason"}
GROUP_KEYS = {"id", "kind", "parent", "title", "state", "observation", "model_fact", "evidence", "sources", "note"}
EDGE_KEYS = {"id", "from", "to", "label", "description", "relationships", "state", "observation",
             "evidence", "sources", "reason"}
NOTE_KEYS = {"id", "attach_to", "lines", "model_fact", "expected", "observation", "sources"}
NOT_DRAWN_KEYS = {"name", "state", "reason", "evidence", "sources"}
LAYOUT_KEYS = {"ranks", "align", "loose"}
FIGURE_KEYS = {"id", "title", "rankdir", "wrap", "summary", "layout", "groups", "nodes", "edges", "notes", "not_drawn"}
DEFAULT_WRAP = 26
TOP_KEYS = {"model_version", "architecture_source", "overlay_source", "purpose", "authorization",
            "max_nodes_per_figure", "evidence_limits", "states", "figures"}

# Presentation: line style encodes the state, fill colour the category (document_figures palette).
FONT = 14
FONT_NAME = "DejaVu Sans"
STATE_STYLE = {"deployed": "solid", "implemented": "dashed", "proposed": "dotted", "tbd": "dotted"}
STATE_PEN = {"deployed": 2.4, "implemented": 1.5, "proposed": 1.6, "tbd": 1.4}
PALETTE = {"prototype": ("#EFF6FF", "#2563EB"), "external": ("#F1F5F9", "#64748B"),
           "persistence": ("#ECFDF5", "#059669"), "platform": ("#FFFFFF", "#475569"),
           "tbd": ("#E5E7EB", "#6B7280")}
NOTE_COLORS = ("#FFFBEB", "#B45309")
EDGE_COLOR = "#475569"
STATE_TEXT = {"deployed": "desplegado (observado el 27/11)", "implemented": "implementado, no observado o inactivo",
              "proposed": "propuesto", "tbd": "TBD: no definido"}
STATE_LINE = {"deployed": "continuo grueso", "implemented": "discontinuo", "proposed": "punteado",
              "tbd": "punteado gris"}
CATEGORY_TEXT = {"prototype": "Azul: Pipesor (servicios, jobs, entornos)",
                 "external": "Gris: actores y servicios externos",
                 "persistence": "Verde: persistencia y secretos",
                 "platform": "Blanco: plataforma o paso de entrega no modelado",
                 "tbd": "Gris oscuro: TBD"}
# A4 print candidates: page, rank direction, legend columns (0 = legend in the guide), edge labels.
DOC_LAYOUTS = tuple((page, rankdir, columns, "label")
                    for columns in (2, 3, 0)
                    for page, rankdir in (("portrait", "TB"), ("portrait", "LR"), ("landscape", "LR"),
                                          ("landscape", "TB")))


class ValidationError(ValueError):
    def __init__(self, errors):
        super().__init__("; ".join(errors))
        self.errors = errors


# --------------------------------------------------------------------------- loading

def load(model_path=MODEL, architecture_path=ARCHITECTURE, overlay_path=OVERLAY):
    read = lambda path: yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return read(model_path), read(architecture_path), read(overlay_path)


def observation_keys(overlay):
    """Observed resources of deployment_observation: its text entries other than the metadata."""
    observed = overlay.get("deployment_observation") or {}
    return {key for key, value in observed.items() if key not in OBSERVATION_META and isinstance(value, str)}


def model_fact(architecture, path):
    node = architecture
    for part in str(path).split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(path)
        node = node[part]
    return node


def figure_index(figure):
    groups = {g["id"]: g for g in figure.get("groups") or [] if isinstance(g, dict) and "id" in g}
    nodes = {n["id"]: n for n in figure.get("nodes") or [] if isinstance(n, dict) and "id" in n}
    return groups, nodes


def subtree_groups(groups, gid):
    found, pending = [], [gid]
    while pending:
        current = pending.pop(0)
        found.append(current)
        pending.extend(g["id"] for g in groups.values() if g.get("parent") == current)
    return found


def group_nodes(figure, gid):
    """Nodes of a group and its descendants, in declared order."""
    groups, _ = figure_index(figure)
    members = set(subtree_groups(groups, gid))
    return [n for n in figure.get("nodes") or [] if n.get("group") in members]


def node_elements(node):
    return {e for e in [node.get("element"), *(node.get("also_elements") or []), *(node.get("runs") or [])] if e}


def endpoint_elements(figure, endpoint):
    groups, nodes = figure_index(figure)
    if endpoint in nodes:
        return node_elements(nodes[endpoint])
    return set().union(*(node_elements(n) for n in group_nodes(figure, endpoint))) if endpoint in groups else set()


# --------------------------------------------------------------------------- validation

def check_sources(values, where, root):
    errors = []
    if not isinstance(values, list) or not values:
        return [f"{where}: sources must be a non-empty list"]
    for value in values:
        match = SOURCE.fullmatch(value) if isinstance(value, str) else None
        if not match:
            errors.append(f"{where}: invalid source {value!r}; expected docs/...:line[-line]")
            continue
        path = Path(root) / match["path"]
        start, end = int(match["start"]), int(match["end"] or match["start"])
        if not path.is_file():
            errors.append(f"{where}: source file {match['path']} does not exist")
        elif end < start or end > len(path.read_text(encoding="utf-8").splitlines()):
            errors.append(f"{where}: source lines {start}-{end} outside {match['path']}")
    return errors


def check_common(item, where, ctx):
    """Evidence, sources, state, observation and model fact of a node, group or edge."""
    errors = []
    state = item.get("state")
    if state not in STATES:
        return [f"{where}: invalid state {state!r}; expected one of {', '.join(STATES)}"]
    if state == "tbd":
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            errors.append(f"{where}: tbd requires a non-empty reason")
        if "evidence" in item:
            errors.extend(evidence.validate_refs(item["evidence"], ctx["repos"], where))
    else:
        errors.extend(evidence.validate_refs(item.get("evidence"), ctx["repos"], where))
    if "sources" in item:
        errors.extend(check_sources(item["sources"], where, ctx["root"]))
    if state == "deployed":
        if item.get("observation") not in ctx["observations"]:
            errors.append(f"{where}: deployed requires an observation among {sorted(ctx['observations'])}")
    elif "observation" in item:
        errors.append(f"{where}: observation is only allowed on deployed items")
    if "model_fact" in item:
        try:
            model_fact(ctx["architecture"], item["model_fact"])
        except KeyError:
            errors.append(f"{where}: model_fact {item['model_fact']!r} does not exist in architecture.yml")
    return errors


def check_element(eid, where, ctx):
    element = ctx["elements"].get(eid)
    if element is None:
        return [f"{where}: element {eid!r} does not exist in architecture.yml"]
    if element.get("status") == "open_question":
        return [f"{where}: element {eid!r} is an open question"]
    return []


def unknown_keys(item, allowed, where):
    extra = sorted(set(item) - allowed)
    return [f"{where}: unknown keys {', '.join(extra)}"] if extra else []


def validate_figure(figure, ctx, max_nodes):
    errors = []
    fid = figure.get("id")
    if not isinstance(fid, str) or not FIGURE_ID.fullmatch(fid):
        return [f"figure {fid!r}: id must match {FIGURE_ID.pattern}"]
    for key in ("title", "summary"):
        if not isinstance(figure.get(key), str) or not figure[key].strip():
            errors.append(f"{fid}: {key} is required")
    if figure.get("rankdir") not in ("LR", "TB"):
        errors.append(f"{fid}: rankdir must be LR or TB")
    extra = sorted(set(figure) - FIGURE_KEYS)
    if extra:
        errors.append(f"{fid}: unknown keys {', '.join(extra)}")
    wrap = figure.get("wrap", DEFAULT_WRAP)
    if type(wrap) is not int or not 16 <= wrap <= 40:
        errors.append(f"{fid}: wrap must be an integer between 16 and 40")
    seen = set()

    def declare(item, kind):
        iid = item.get("id") if isinstance(item, dict) else None
        if not isinstance(iid, str) or not LOCAL_ID.fullmatch(iid):
            errors.append(f"{fid}: {kind} id {iid!r} is invalid")
            return None
        if iid in seen:
            errors.append(f"{fid}: duplicate id {iid!r}")
        seen.add(iid)
        return iid

    groups = figure.get("groups") or []
    nodes = figure.get("nodes") or []
    edges = figure.get("edges") or []
    if not nodes:
        errors.append(f"{fid}: nodes must be a non-empty list")
    for group in groups:
        declare(group, "group")
    for node in nodes:
        declare(node, "node")
    group_ids = {g["id"] for g in groups if isinstance(g, dict) and "id" in g}
    node_ids = {n["id"]: n for n in nodes if isinstance(n, dict) and "id" in n}

    for group in groups:
        gid = group.get("id")
        where = f"{fid}.groups.{gid}"
        errors.extend(unknown_keys(group, GROUP_KEYS, where))
        if not isinstance(group.get("title"), str) or not group["title"].strip():
            errors.append(f"{where}: title is required")
        parent = group.get("parent")
        if parent is not None and parent not in group_ids:
            errors.append(f"{where}: unknown parent {parent!r}")
        ancestors, current = set(), parent
        while current is not None and current in group_ids:
            if current in ancestors or current == gid:
                errors.append(f"{where}: parent cycle")
                break
            ancestors.add(current)
            current = next(g for g in groups if g.get("id") == current).get("parent")
        if group.get("kind") == "resource":
            errors.extend(check_common(group, where, ctx))
            if group.get("state") == "tbd":
                errors.append(f"{where}: a resource group cannot be tbd")
        elif group.get("kind") == "reading":
            if "state" in group or "observation" in group:
                errors.append(f"{where}: reading groups are not resources and carry no state")
            if not isinstance(group.get("note"), str) or not group["note"].strip():
                errors.append(f"{where}: reading groups require a note")
            if "evidence" in group:
                errors.extend(evidence.validate_refs(group["evidence"], ctx["repos"], where))
            if "sources" in group:
                errors.extend(check_sources(group["sources"], where, ctx["root"]))
        else:
            errors.append(f"{where}: kind must be one of {', '.join(GROUP_KINDS)}")

    for node in nodes:
        nid = node.get("id")
        where = f"{fid}.nodes.{nid}"
        errors.extend(unknown_keys(node, NODE_KEYS, where))
        if not isinstance(node.get("name"), str) or not node["name"].strip():
            errors.append(f"{where}: name is required")
        if node.get("group") is not None and node["group"] not in group_ids:
            errors.append(f"{where}: unknown group {node['group']!r}")
        for key in ("details", "facts"):
            values = node.get(key, [])
            if not isinstance(values, list) or not all(isinstance(d, str) and d.strip() for d in values):
                errors.append(f"{where}: {key} must be a list of non-empty strings")
        errors.extend(check_common(node, where, ctx))
        if node.get("state") == "tbd":
            for key in ("element", "implementation_only", "also_elements", "runs", "category", "group"):
                if key in node:
                    errors.append(f"{where}: a tbd node cannot declare {key}")
        else:
            has_element = "element" in node
            only = node.get("implementation_only") is True
            if has_element == only:
                errors.append(f"{where}: declare exactly one of element or implementation_only: true")
            if "implementation_only" in node and not only:
                errors.append(f"{where}: implementation_only must be true when present")
            if has_element:
                errors.extend(check_element(node["element"], where, ctx))
                if "category" in node:
                    errors.append(f"{where}: the category of a model element comes from its kind")
            if only:
                if node.get("category") not in CATEGORIES:
                    errors.append(f"{where}: implementation_only nodes require a category in {', '.join(CATEGORIES)}")
                for key in ("also_elements", "runs"):
                    if key in node:
                        errors.append(f"{where}: {key} requires a model element")
            for key in ("also_elements", "runs"):
                values = node.get(key, [])
                if not isinstance(values, list):
                    errors.append(f"{where}: {key} must be a list")
                    continue
                for eid in values:
                    errors.extend(check_element(eid, where, ctx))
        if "observed_status" in node and node.get("state") != "deployed":
            errors.append(f"{where}: observed_status requires the deployed state")

    distinct = {n["element"] for n in nodes if isinstance(n, dict) and n.get("element")}
    if len(distinct) > ctx["limit"]:
        errors.append(f"{fid}: {len(distinct)} model elements exceed max_nodes_per_view {ctx['limit']}")
    if len(nodes) > max_nodes:
        errors.append(f"{fid}: {len(nodes)} nodes exceed max_nodes_per_figure {max_nodes}")

    endpoints = group_ids | set(node_ids)
    for edge in edges:
        eid = declare(edge, "edge")
        where = f"{fid}.edges.{eid}"
        errors.extend(unknown_keys(edge, EDGE_KEYS, where))
        source, target = edge.get("from"), edge.get("to")
        unknown = [end for end in (source, target) if end not in endpoints]
        for end in unknown:
            errors.append(f"{where}: unknown endpoint {end!r}")
        if unknown:
            continue
        if source == target:
            errors.append(f"{where}: an edge needs two different endpoints")
        for end in (source, target):
            if node_ids.get(end, {}).get("state") == "tbd":
                errors.append(f"{where}: tbd nodes are listed in the TBD panel and take no edges")
        for outer, inner in ((source, target), (target, source)):
            if outer in group_ids and inner in endpoints - {outer}:
                members = set(subtree_groups(figure_index(figure)[0], outer))
                if inner in members or node_ids.get(inner, {}).get("group") in members:
                    errors.append(f"{where}: {inner!r} lies inside {outer!r}")
        for key in ("label", "description"):
            if not isinstance(edge.get(key), str) or not edge[key].strip():
                errors.append(f"{where}: {key} is required")
        errors.extend(check_common(edge, where, ctx))
        for rid in edge.get("relationships", []) or []:
            relation = ctx["relationships"].get(rid)
            if relation is None:
                errors.append(f"{where}: relationship {rid!r} does not exist in architecture.yml")
                continue
            if relation["from"] not in endpoint_elements(figure, source) or \
                    relation["to"] not in endpoint_elements(figure, target):
                errors.append(f"{where}: relationship {rid!r} ({relation['from']} -> {relation['to']}) "
                              f"does not join the elements of {source!r} and {target!r}")

    for note in figure.get("notes") or []:
        nid = declare(note, "note")
        where = f"{fid}.notes.{nid}"
        errors.extend(unknown_keys(note, NOTE_KEYS, where))
        if node_ids.get(note.get("attach_to"), {}).get("state") in (None, "tbd"):
            errors.append(f"{where}: attach_to must name a drawn node")
        lines_ = note.get("lines")
        if not isinstance(lines_, list) or not lines_ or not all(isinstance(t, str) and t.strip() for t in lines_):
            errors.append(f"{where}: lines must be a non-empty list of strings")
        if "model_fact" in note:
            try:
                actual = model_fact(ctx["architecture"], note["model_fact"])
            except KeyError:
                errors.append(f"{where}: model_fact {note['model_fact']!r} does not exist in architecture.yml")
            else:
                if "expected" in note and actual != note["expected"]:
                    errors.append(f"{where}: {note['model_fact']} is {actual!r}, the note expects {note['expected']!r}")
        if "observation" in note and note["observation"] not in ctx["observations"]:
            errors.append(f"{where}: unknown observation {note['observation']!r}")
        if "sources" in note:
            errors.extend(check_sources(note["sources"], where, ctx["root"]))

    drawn = {nid for nid, node in node_ids.items() if node.get("state") != "tbd"}
    errors.extend(validate_layout(figure, drawn, {e.get("id") for e in edges if isinstance(e, dict)}))

    for index, item in enumerate(figure.get("not_drawn") or []):
        where = f"{fid}.not_drawn[{index}]"
        errors.extend(unknown_keys(item, NOT_DRAWN_KEYS, where))
        for key in ("name", "reason"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(f"{where}: {key} is required")
        if item.get("state") == "deployed":
            errors.append(f"{where}: an observed item must be drawn")
        errors.extend(check_common(item, where, ctx))
    return errors


def validate_layout(figure, node_ids, edge_ids):
    """Presentation-only placement hints: ranks, aligned chains and loose edges."""
    fid, errors = figure.get("id"), []
    layout = figure.get("layout") or {}
    if not isinstance(layout, dict) or set(layout) - LAYOUT_KEYS:
        return [f"{fid}.layout: only {', '.join(sorted(LAYOUT_KEYS))} are allowed"]
    placed = []
    for rank in layout.get("ranks") or []:
        if not isinstance(rank, list) or not rank:
            errors.append(f"{fid}.layout.ranks: each rank must be a non-empty list")
            continue
        placed.extend(rank)
    for nid in placed:
        if nid not in node_ids:
            errors.append(f"{fid}.layout.ranks: unknown or tbd node {nid!r}")
    for nid in sorted({n for n in placed if placed.count(n) > 1}):
        errors.append(f"{fid}.layout.ranks: node {nid!r} appears in more than one rank")
    for chain in layout.get("align") or []:
        if not isinstance(chain, list) or len(chain) < 2 or any(nid not in node_ids for nid in chain):
            errors.append(f"{fid}.layout.align: each chain must list at least two known, drawn nodes")
    for eid in layout.get("loose") or []:
        if eid not in edge_ids:
            errors.append(f"{fid}.layout.loose: unknown edge {eid!r}")
    return errors


def validate(presentation, architecture, overlay, root=ROOT):
    """Every structural and referential error of the presentation model (empty list when valid)."""
    errors = []
    extra = sorted(set(presentation) - TOP_KEYS)
    if extra:
        errors.append(f"unknown top-level keys {', '.join(extra)}")
    if presentation.get("architecture_source") != "model/architecture.yml":
        errors.append("architecture_source must be model/architecture.yml")
    if presentation.get("overlay_source") != "model/implementation_status.yml":
        errors.append("overlay_source must be model/implementation_status.yml")
    authorization = presentation.get("authorization") or {}
    if not authorization.get("date") or not authorization.get("decisions"):
        errors.append("authorization requires date and decisions")
    states = presentation.get("states") or {}
    if tuple(states) != STATES:
        errors.append(f"states must declare exactly {', '.join(STATES)} in that order")
    limits = presentation.get("evidence_limits", [])
    if not isinstance(limits, list) or not all(isinstance(item, str) and item.strip() for item in limits):
        errors.append("evidence_limits must be a list of non-empty strings")
    max_nodes = presentation.get("max_nodes_per_figure")
    if type(max_nodes) is not int or max_nodes < 1:
        errors.append("max_nodes_per_figure must be a positive integer")
        max_nodes = 22
    repos = overlay.get("repositories") or {}
    errors.extend(evidence.validate_repositories(repos))
    observations = observation_keys(overlay)
    if (overlay.get("deployment_observation") or {}).get("environment") != "dev" or not observations:
        errors.append("implementation_status.yml: deployment_observation of dev is required")
    limit = ((architecture.get("architecture") or {}).get("view_constraints") or {}).get("max_nodes_per_view")
    if type(limit) is not int or limit < 1:
        errors.append("architecture.view_constraints.max_nodes_per_view must be a positive integer")
        limit = 15
    ctx = {"architecture": architecture, "repos": repos, "observations": observations, "root": root,
           "limit": limit, "elements": {e["id"]: e for e in architecture.get("elements") or []},
           "relationships": {r["id"]: r for r in architecture.get("relationships") or []}}
    figures = presentation.get("figures")
    if not isinstance(figures, list) or not figures:
        return errors + ["figures must be a non-empty list"]
    ids = [f.get("id") for f in figures if isinstance(f, dict)]
    for duplicate in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"duplicate figure id {duplicate!r}")
    for figure in figures:
        errors.extend(validate_figure(figure, ctx, max_nodes))
    return errors


def check(presentation, architecture, overlay, root=ROOT):
    errors = validate(presentation, architecture, overlay, root)
    if errors:
        raise ValidationError(errors)
    return presentation["figures"]


# --------------------------------------------------------------------------- Graphviz

def lines(value, width, left=False):
    """Wrapped HTML-label text; an explicit newline in the model forces a break."""
    wrapped = [escape(line) for part in value.split("\n")
               for line in textwrap.wrap(part, width, break_long_words=False, break_on_hyphens=False)]
    if left:  # a left-aligned break ends every line, the last one included
        return "".join(f'{line}<BR ALIGN="LEFT"/>' for line in wrapped)
    return "<BR/>".join(wrapped)


def category(node, elements):
    if node["state"] == "tbd":
        return "tbd"
    if node.get("element"):
        return KIND_CATEGORY[elements[node["element"]]["kind"]]
    return node["category"]


def node_attributes(node, elements):
    kind = category(node, elements)
    fill, border = PALETTE[kind]
    style = STATE_STYLE[node["state"]]
    attrs = {"fillcolor": fill, "color": border, "penwidth": f"{STATE_PEN[node['state']]:.1f}",
             "fontcolor": "#374151" if kind == "tbd" else "#0F172A"}
    if kind == "persistence":
        attrs.update(shape="cylinder", style=f"filled,{style}")
    else:
        attrs.update(shape="box", style=f"rounded,filled,{style}")
    return attrs


def node_label(node, wrap=DEFAULT_WRAP):
    rows = [f'<TR><TD><B>{lines(node["name"], wrap)}</B></TD></TR>']
    for detail in node.get("details") or []:
        rows.append(f'<TR><TD><FONT COLOR="#334155">{lines(detail, wrap + 2)}</FONT></TD></TR>')
    if node.get("observed_status"):
        rows.append(f'<TR><TD><FONT COLOR="{NOTE_COLORS[1]}"><B>{lines(node["observed_status"], wrap + 6)}'
                    '</B></FONT></TD></TR>')
    return '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">' + "".join(rows) + "</TABLE>>"


def note_label(note, wrap=2 * DEFAULT_WRAP):
    rows = "".join(f'<TR><TD ALIGN="LEFT" BALIGN="LEFT">{lines(text, wrap)}</TD></TR>' for text in note["lines"])
    return '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="1">' + rows + "</TABLE>>"


def legend_entries(figure, elements):
    states = [s for s in STATES if any(i.get("state") == s for i in
                                       (figure.get("nodes") or []) + (figure.get("edges") or [])
                                       + (figure.get("groups") or []))]
    used = []
    for node in figure.get("nodes") or []:
        kind = category(node, elements)
        if kind not in used:
            used.append(kind)
    kinds = [k for k in (*CATEGORIES, "tbd") if k in used]
    entries = [(f'BORDER="1" STYLE="{STATE_STYLE[s]}" COLOR="{EDGE_COLOR}"', f"Trazo {STATE_LINE[s]}: {STATE_TEXT[s]}")
               for s in states]
    entries += [(f'BORDER="1" COLOR="{PALETTE[k][1]}" BGCOLOR="{PALETTE[k][0]}"', CATEGORY_TEXT[k]) for k in kinds]
    if figure.get("notes"):
        entries.append((f'BORDER="1" COLOR="{NOTE_COLORS[1]}" BGCOLOR="{NOTE_COLORS[0]}"',
                        "Ámbar: divergencia entre el modelo y lo observado"))
    if any(g.get("kind") == "reading" for g in figure.get("groups") or []):
        entries.append(('BORDER="1" COLOR="#CBD5E1"', "Marco gris claro: agrupación de lectura, no un recurso"))
    return entries


def edge_numbers(figure):
    """Edges are numbered in declared order; the guide and the print legend use the same numbers."""
    return {edge["id"]: number for number, edge in enumerate(figure.get("edges") or [], 1)}


def legend_table(figure, elements, columns, numbered):
    cells = []
    if numbered:
        cells += [(f'<TD ALIGN="RIGHT" VALIGN="TOP"><B>{number:02d}</B></TD>', edge["label"])
                  for number, edge in enumerate(figure.get("edges") or [], 1)]
    cells += [(f'<TD {sample} WIDTH="22" HEIGHT="14"> </TD>', text) for sample, text in legend_entries(figure, elements)]
    per_column = -(-len(cells) // columns)
    width = 30 if columns >= 3 else 38
    stacks = []
    for column in range(columns):
        rows = "".join(f'<TR>{left}<TD ALIGN="LEFT" BALIGN="LEFT" VALIGN="TOP">{lines(text, width)}</TD></TR>'
                       for left, text in cells[column * per_column:(column + 1) * per_column])
        stacks.append(f'<TD VALIGN="TOP"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="3">{rows}</TABLE></TD>')
    return f'<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2" CELLPADDING="0"><TR>{"".join(stacks)}</TR></TABLE>'


def tbd_panel(figure, columns=3):
    """TBD points have no edges: one fixed panel under the drawing instead of free-floating nodes."""
    pending = [n for n in figure["nodes"] if n["state"] == "tbd"]
    if not pending:
        return ""
    fill, border = PALETTE["tbd"]
    cells = [f'<TD BORDER="1" STYLE="dotted" COLOR="{border}" BGCOLOR="{fill}"><FONT COLOR="#374151"><B>TBD</B>'
             f'<BR/>{lines(node["name"], figure.get("wrap", DEFAULT_WRAP))}</FONT></TD>' for node in pending]
    rows = "".join(f'<TR>{"".join(cells[i:i + columns])}</TR>' for i in range(0, len(cells), columns))
    return (f'<TABLE BORDER="1" STYLE="rounded" COLOR="#CBD5E1" CELLBORDER="0" CELLSPACING="6" CELLPADDING="4">'
            f'<TR><TD COLSPAN="{columns}" ALIGN="LEFT"><B>No definido (TBD)</B></TD></TR>{rows}</TABLE>')


def figure_label(figure, elements, columns, title=None, numbered=False):
    """Graph label under the drawing: title (views only), TBD panel and legend; None when empty."""
    parts = []
    if title:
        parts.append(f'<FONT POINT-SIZE="{FONT + 4}"><B>{escape(title)}</B></FONT>')
    panel = tbd_panel(figure)
    if panel:
        parts.append(panel)
    if columns:
        parts.append(legend_table(figure, elements, columns, numbered))
    if not parts:
        return None
    rows = "".join(f'<TR><TD ALIGN="LEFT">{part}</TD></TR>' for part in parts)
    return f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="4" CELLPADDING="0">{rows}</TABLE>>'


def anchor(figure, endpoint):
    """Graphviz node and cluster name of an endpoint (clusters attach to their first node)."""
    groups, nodes = figure_index(figure)
    if endpoint in nodes:
        return endpoint, None
    return group_nodes(figure, endpoint)[0]["id"], f"cluster_{endpoint}"


def generate_dot(figure, architecture, *, rankdir=None, legend_columns=3, document=False):
    """Deterministic DOT source of a figure; the view adds its title above the legend."""
    elements = {e["id"]: e for e in architecture.get("elements") or []}
    wrap = figure.get("wrap", DEFAULT_WRAP)
    graph = Digraph(figure["id"], comment="GENERATED from model/deployment_presentation.yml; do not edit")
    graph.attr(rankdir=rankdir or figure["rankdir"], newrank="true", compound="true", bgcolor="white",
               pad="0.15", nodesep="0.14", ranksep="0.22", fontname=FONT_NAME, fontsize=str(FONT),
               labelloc="b", labeljust="l")
    label = figure_label(figure, elements, legend_columns, None if document else figure["title"], numbered=document)
    if label:
        graph.attr(label=label)
    graph.attr("node", fontname=FONT_NAME, fontsize=str(FONT), margin="0.1,0.05")
    graph.attr("edge", fontname=FONT_NAME, fontsize=str(FONT), color=EDGE_COLOR, fontcolor="#1E293B",
               arrowsize="0.7")

    def add_node(target, node):
        target.node(node["id"], node_label(node, wrap), tooltip=node["name"], **node_attributes(node, elements))

    def add_group(target, group):
        with target.subgraph(name=f"cluster_{group['id']}") as cluster:
            if group["kind"] == "reading":
                style, color, pen = "rounded", "#CBD5E1", "1.2"
            else:
                style, color, pen = f"rounded,{STATE_STYLE[group['state']]}", EDGE_COLOR, \
                    f"{STATE_PEN[group['state']]:.1f}"
            cluster.attr(label=f"<<B>{lines(group['title'], 64, left=True)}</B>>", labeljust="l", labelloc="t",
                         style=style, color=color, penwidth=pen, fontcolor="#1E293B", fontsize=str(FONT),
                         margin="6")
            for node in figure["nodes"]:
                if node.get("group") == group["id"]:
                    add_node(cluster, node)
            for child in figure.get("groups") or []:
                if child.get("parent") == group["id"]:
                    add_group(cluster, child)

    for node in figure["nodes"]:
        if node.get("group") is None and node["state"] != "tbd":
            add_node(graph, node)
    for group in figure.get("groups") or []:
        if group.get("parent") is None:
            add_group(graph, group)
    for note in figure.get("notes") or []:
        fill, border = NOTE_COLORS
        graph.node(note["id"], note_label(note, 2 * wrap), shape="note", style="filled", fillcolor=fill, color=border,
                   fontcolor="#78350F", penwidth="1.4", tooltip=" ".join(note["lines"]))
        # From the node to its note: the note sits one rank after the node it annotates.
        graph.edge(note["attach_to"], note["id"], style="dotted", color=border, arrowhead="none", penwidth="1.4")

    layout = figure.get("layout") or {}
    ranks = layout.get("ranks") or []
    # Declared position of each ranked node: (rank, place in the rank).
    place = {nid: (index, position) for index, rank in enumerate(ranks) for position, nid in enumerate(rank)}
    for members in ranks:
        with graph.subgraph() as same:
            same.attr(rank="same")
            for nid in members:
                same.node(nid)
    loose = set(layout.get("loose") or [])
    numbers = edge_numbers(figure)
    oriented = []
    for edge in figure.get("edges") or []:
        tail, ltail = anchor(figure, edge["from"])
        head, lhead = anchor(figure, edge["to"])
        reverse = tail in place and head in place and place[tail] > place[head]
        if reverse:
            # Drawn from source to target, laid out from target to source: keeps the declared ranks
            # and, inside a rank, the declared left-to-right order.
            tail, head, ltail, lhead = head, tail, lhead, ltail
        oriented.append((edge, tail, head, ltail, lhead, reverse))
    linked = {(place[t][0], place[h][0]) for e, t, h, *_ in oriented
              if t in place and h in place and e["id"] not in loose}
    for index, (upper, lower) in enumerate(zip(ranks, ranks[1:])):
        if (index, index + 1) not in linked:
            # Invisible and weightless: orders consecutive ranks that no edge orders.
            graph.edge(upper[0], lower[0], style="invis", weight="0")
    joined = {frozenset((t, h)) for _, t, h, *_ in oriented}
    for rank in ranks:
        for left, right in zip(rank, rank[1:]):
            if frozenset((left, right)) not in joined:
                # Invisible: keeps the declared left-to-right order inside the rank.
                graph.edge(left, right, style="invis")
    for chain in layout.get("align") or []:
        # Invisible and heavy: keeps the chain in one column.
        for upper, lower in zip(chain, chain[1:]):
            graph.edge(upper, lower, style="invis", weight="20")

    for edge, tail, head, ltail, lhead, reverse in oriented:
        attrs = {"id": edge["id"]}
        if reverse:
            attrs["dir"] = "back"
        if ltail:
            attrs["ltail"] = ltail
        if lhead:
            attrs["lhead"] = lhead
        if edge["id"] in loose:
            attrs.update(constraint="false", weight="0")
        number = f"<B>{numbers[edge['id']]:02d}</B>"
        text = number if document else f"{number} {lines(edge['label'], 22)}"
        attrs.update(label=f"<{text}>", tooltip=edge["description"],
                     style=STATE_STYLE[edge["state"]], penwidth=f"{STATE_PEN[edge['state']]:.1f}")
        if edge["state"] == "tbd":
            attrs["color"] = PALETTE["tbd"][1]
        graph.edge(tail, head, **attrs)
    return graph.source


def run_dot(source, target, *extra):
    subprocess.run(["dot", *extra, f"-T{target.suffix[1:]}", str(source), "-o", str(target)], check=True, cwd=ROOT)


def render_view(figure, architecture, build=BUILD, out=OUT):
    build.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    source = build / f"{figure['id']}.dot"
    source.write_text(generate_dot(figure, architecture), encoding="utf-8")
    run_dot(source, out / f"{figure['id']}.svg")
    return out / f"{figure['id']}.svg"


def _print_helpers():
    """document_figures supplies the A4 page sizes and the print helpers (imported only for print)."""
    try:
        from . import document_figures
    except ImportError:
        import document_figures
    return document_figures


def render_document(figure, architecture, out=DOC_OUT, build=BUILD):
    """Render every A4 candidate and keep the one document_figures.choose selects."""
    doc = _print_helpers()
    out.mkdir(parents=True, exist_ok=True)
    build.mkdir(parents=True, exist_ok=True)
    fid = figure["id"]
    svg, png, source = out / f"{fid}.svg", out / f"{fid}.png", build / f"{fid}_doc.dot"
    results = []
    for layout in DOC_LAYOUTS:
        source.write_text(generate_dot(figure, architecture, rankdir=layout[1], legend_columns=layout[2],
                                       document=True), encoding="utf-8")
        run_dot(source, svg)
        results.append((layout, *doc.printed_sizes(svg, layout[0])))
    layout, scale, width_cm, height_cm, smallest = doc.choose(fid, results)
    source.write_text(generate_dot(figure, architecture, rankdir=layout[1], legend_columns=layout[2],
                                   document=True), encoding="utf-8")
    run_dot(source, svg)
    doc.set_svg_print_size(svg, width_cm, height_cm)
    run_dot(source, png, f"-Gdpi={doc.PNG_DPI * scale:.2f}")
    doc.set_png_dpi(png, doc.PNG_DPI)
    return {"id": fid, "title": figure["title"], "page": layout[0],
            "legend": "en la figura" if layout[2] else "tabla en la guía",
            "width_cm": round(width_cm, 2), "height_cm": round(height_cm, 2), "min_pt": round(smallest, 2)}


def render_documents(out=DOC_OUT, build=BUILD):
    """Print variants of every deployment figure: out/doc/<id>.svg and .png (300 ppp).

    Returns one dict per figure with id, title, page ('portrait' or 'landscape'), legend
    ('en la figura' or 'tabla en la guía'), width_cm, height_cm and min_pt.
    """
    presentation, architecture, overlay = load()
    return [render_document(figure, architecture, out, build) for figure in check(presentation, architecture, overlay)]


# --------------------------------------------------------------------------- guide

def code(value):
    return f"`{value}`"


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def citations(item):
    refs = []
    if item.get("observation"):
        refs.append(f"observación 27/11 ({code(item['observation'])})")
    refs += [code(ref) for ref in item.get("evidence") or []]
    refs += [f"doc. {code(ref)}" for ref in item.get("sources") or []]
    return "<br>".join(refs) or "—"


def state_cell(item):
    if item["state"] == "tbd":
        return f"TBD: {cell(item['reason'])}"
    text = STATE_TEXT[item["state"]]
    return f"{text}; {cell(item['observed_status'])}" if item.get("observed_status") else text


def model_cell(node):
    if node["state"] == "tbd":
        return "— (no definido)"
    if node.get("element"):
        parts = [code(node["element"])]
        if node.get("also_elements"):
            parts.append("misma instancia: " + ", ".join(code(e) for e in node["also_elements"]))
        if node.get("runs"):
            parts.append("ejecuta " + ", ".join(code(e) for e in node["runs"]))
    else:
        parts = ["«implementación no modelada»"]
    if node.get("model_fact"):
        parts.append("hecho " + code(node["model_fact"]))
    return "; ".join(parts)


def endpoint_name(figure, endpoint):
    groups, nodes = figure_index(figure)
    return nodes[endpoint]["name"] if endpoint in nodes else f"[{groups[endpoint]['title']}]"


def figure_section(figure, repos):
    fid = figure["id"]
    groups, nodes = figure_index(figure)
    text = [f"## {figure['title']} (`{fid}`)", "",
            f"Vista: [SVG]({fid}.svg) · Impresión A4 (`--document`): [SVG](doc/{fid}.svg) · [PNG](doc/{fid}.png)", "",
            " ".join(figure["summary"].split()), "",
            "En la vista, cada flecha lleva su número y su etiqueta; en la versión impresa solo el número, y esta "
            "guía hace de leyenda (tabla de aristas y leyenda de estados y colores)."
            + (" Los puntos TBD no tienen aristas: van en el recuadro «No definido (TBD)» bajo el dibujo."
               if any(n["state"] == "tbd" for n in figure["nodes"]) else ""), ""]
    elements = {n.get("element") for n in figure["nodes"] if n.get("element")}
    only = [n for n in figure["nodes"] if n.get("implementation_only")]
    tbd = [n for n in figure["nodes"] if n["state"] == "tbd"]
    text += [f"{len(figure['nodes'])} nodos: {len(elements)} elementos distintos del modelo, "
             f"{len(only)} implementaciones no modeladas y {len(tbd)} puntos TBD.", ""]
    text += ["### Nodos", "", "| Nodo | Elemento del modelo o «implementación no modelada» | Estado | Evidencia |",
             "|---|---|---|---|"]
    for node in figure["nodes"]:
        extra = [*(node.get("details") or []), *(node.get("facts") or [])]
        name = node["name"] + (f" ({'; '.join(extra)})" if extra else "")
        text.append(f"| {cell(name)} | {model_cell(node)} | {state_cell(node)} | {citations(node)} |")
    if groups:
        text += ["", "### Grupos", "", "| Grupo | Tipo | Estado | Evidencia |", "|---|---|---|---|"]
        for group in figure["groups"]:
            kind = "recurso" if group["kind"] == "resource" else f"agrupación de lectura: {cell(group['note'])}"
            if group.get("model_fact"):
                kind += f"; hecho {code(group['model_fact'])}"
            state = STATE_TEXT[group["state"]] if group["kind"] == "resource" else "—"
            text.append(f"| {cell(group['title'])} | {kind} | {state} | {citations(group)} |")
    text += ["", "### Aristas", "", "| Nº | Arista | Relación del modelo | Estado | Evidencia |",
             "|---|---|---|---|---|"]
    for number, edge in enumerate(figure.get("edges") or [], 1):
        name = f"{endpoint_name(figure, edge['from'])} → {endpoint_name(figure, edge['to'])}: {edge['label']}"
        relations = ", ".join(code(r) for r in edge.get("relationships") or []) or "«implementación no modelada»"
        text.append(f"| {number:02d} | {cell(name)}. {cell(' '.join(edge['description'].split()))} | {relations} | "
                    f"{state_cell(edge)} | {citations(edge)} |")
    for note in figure.get("notes") or []:
        text += ["", "### Divergencia", "",
                 f"Nota junto a «{nodes[note['attach_to']]['name']}»: " + " ".join(note["lines"]) + ".",
                 f"Hecho del modelo: {code(note['model_fact'])} = {code(str(note.get('expected')).lower())}; "
                 f"observación 27/11 ({code(note['observation'])})."
                 + (" Fuente: " + ", ".join(code(s) for s in note.get("sources") or []) + "." if note.get("sources") else "")
                 + " La figura muestra la divergencia; no cambia architecture.yml ni acredita una autorización."]
    if figure.get("not_drawn"):
        text += ["", "### Implementado y no dibujado", "", "| Elemento | Estado | Motivo | Evidencia |",
                 "|---|---|---|---|"]
        for item in figure["not_drawn"]:
            text.append(f"| {cell(item['name'])} | {STATE_TEXT[item['state']] if item['state'] != 'tbd' else 'TBD'} | "
                        f"{cell(item['reason'])} | {citations(item)} |")
    return text + [""]


def guide(presentation, architecture, overlay):
    observed = overlay["deployment_observation"]
    repos = overlay["repositories"]
    used = sorted({evidence.parse(ref).repo for ref in evidence.collect(presentation)})
    text = ["# Diagramas de despliegue", "",
            "Generado desde `model/deployment_presentation.yml` con `tools/generators/deployment.py`. Hechos de "
            "`model/architecture.yml`; evidencia `repo:ruta:línea` en las revisiones fijadas en "
            "`model/implementation_status.yml`. No editar a mano.", "",
            f"Autorización: {presentation['authorization']['date']}, decisiones "
            + " y ".join(str(d) for d in presentation["authorization"]["decisions"]) + ". "
            + " ".join(presentation["authorization"]["scope"].split()), "",
            "Las figuras no añaden arquitectura ni aprueban un despliegue. Lo que existe en IaC o en código y no "
            "está en el modelo figura como «implementación no modelada» y no se añade a `architecture.yml`.", "",
            "## Observación del 27/11", "",
            f"Observación del entorno `{observed['environment']}` el {observed['observed_at']}: {observed['method']}. "
            "En la guía se cita como «observación 27/11».", ""]
    for key in sorted(observation_keys(overlay)):
        text.append(f"- `{key}`: {observed[key]}.")
    if observed.get("evidence"):
        text += ["", "Evidencia de la observación: " + ", ".join(code(ref) for ref in observed["evidence"]) + "."]
    text += ["", "Solo esos recursos se observaron. Los demás (red, Container Apps Environment, Key Vault, Foundry, "
             "Log Analytics, identidades, GHCR) constan en IaC y van como implementados: no se volvieron a comprobar. La "
             "configuración privada de dev (tfvars) no se leyó; se cita el ejemplo versionado "
             "`environments/dev/terraform.tfvars.example`.", "",
             "## Leyenda", "", "| Trazo de nodos, grupos y aristas | Estado | Significado |", "|---|---|---|"]
    for state in STATES:
        text.append(f"| {STATE_LINE[state]} | {STATE_TEXT[state]} | {presentation['states'][state]} |")
    text += ["", "| Color de relleno | Categoría |", "|---|---|"]
    for kind in (*CATEGORIES, "tbd"):
        text.append(f"| {PALETTE[kind][0]} con borde {PALETTE[kind][1]} | {CATEGORY_TEXT[kind]} |")
    text += [f"| {NOTE_COLORS[0]} con borde {NOTE_COLORS[1]} | Nota ámbar: divergencia entre el modelo y lo observado |",
             "", "La categoría de un elemento del modelo sale de su `kind` (actor y sistema externo: gris; "
             "datastore: verde; contenedor: azul). Los marcos gris claro son agrupaciones de lectura, no recursos.",
             "", "## Límites de la evidencia", ""]
    text += [f"- {' '.join(item.split())}" for item in presentation.get("evidence_limits") or []]
    text += ["", "## Revisiones de la evidencia", "", "| Clave | Repositorio | Revisión |", "|---|---|---|"]
    for key in used:
        text.append(f"| `{key}` | `{repos[key]['path']}` | `{repos[key]['revision']}` |")
    text.append("")
    for figure in presentation["figures"]:
        text += figure_section(figure, repos)
    return "\n".join(text).rstrip() + "\n"


# --------------------------------------------------------------------------- entry point

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--document", action="store_true", help="also write the A4 print variants in out/doc")
    args = parser.parse_args(argv)
    presentation, architecture, overlay = load()
    figures = check(presentation, architecture, overlay)
    if args.validate_only:
        print(f"DEPLOYMENT VALIDATION PASSED ({len(figures)} figures)")
        return 0
    for figure in figures:
        print(f"generated: {render_view(figure, architecture).relative_to(ROOT)}")
    GUIDE.write_text(guide(presentation, architecture, overlay), encoding="utf-8")
    print(f"generated: {GUIDE.relative_to(ROOT)}")
    if args.document:
        for result in render_documents():
            print(f"generated: out/doc/{result['id']}.svg|png ({result['page']}, legend {result['legend']}, "
                  f"{result['width_cm']:.1f}x{result['height_cm']:.1f} cm, min {result['min_pt']:.1f} pt)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as error:
        raise SystemExit("DEPLOYMENT VALIDATION FAILED\n" + "\n".join(f"- {e}" for e in error.errors))
    except (KeyError, TypeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Deployment views failed: {error}") from error
