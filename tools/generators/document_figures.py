#!/usr/bin/env python3
"""Print-legible document variants of the presentation and C4 component views.

The slide views (16:9, left to right) become unreadable when a document scales
them to a text column: inserted at 15.9 cm their text prints at 3-6 pt. These
variants keep each view's declared membership and canonical relationships,
number the arrows and size every text for the printed page. Each figure is
rendered in several candidate compositions; the chosen one keeps every text at
or above MIN_POINTS once inserted at its stated size on an A4 page.

The C4 container views keep their curated positions and routes (only the text
grows and the slide title and legend leave the drawing). The other views are
laid out by Graphviz dot.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
from pathlib import Path
import re
import struct
import subprocess
import textwrap
import xml.etree.ElementTree as ET
import zlib

import yaml
from graphviz import Digraph

try:
    from . import c4
    from . import c4_container_presentation as c4_expo
    from . import logical_presentation as logical
    from . import physical_presentation as physical
except ImportError:
    import c4
    import c4_container_presentation as c4_expo
    import logical_presentation as logical
    import physical_presentation as physical

ROOT = logical.ROOT
OUT = ROOT / "out" / "doc"
BUILD = ROOT / "build" / "doc"
CM_PER_POINT = 2.54 / 72
# A4 with 2.54 cm margins; the height keeps room for the APA number, title and note.
PAGES = {"portrait": (15.9, 22.0), "landscape": (24.6, 14.0)}
# Candidate compositions: page, rank direction, legend columns (0 moves the legend to the guide).
# Edge numbers are real labels first (dot reserves room for them); free labels only when that
# room would push the text under MIN_POINTS.
LAYOUTS = tuple((page, rankdir, columns, edge)
                for edge in ("label", "xlabel")
                for page, rankdir, columns in (("portrait", "TB", 2), ("portrait", "TB", 3), ("portrait", "LR", 2),
                                               ("landscape", "LR", 3), ("landscape", "TB", 3),
                                               ("landscape", "LR", 0), ("landscape", "TB", 0)))
MIN_POINTS = 8.0
TARGET_POINTS = 9.0  # figures smaller than the page shrink until their smallest text reaches this size
PNG_DPI = 300
FONT = 14
STYLES = {"sync": "solid", "async": "dashed", "event": "dotted", "governance": "dashed"}
KINDS = {"actor": "Person", "external_system": "External system", "datastore": "Data container",
         "container": "Container", "component": "Component"}
LEGEND = ("Blue: prototype · Gray: actors and external systems · Green: persistence · "
          "Solid: synchronous · Dashed: asynchronous · Dotted: event")
C4_KEY = ("Without stereotypes: blue boxes are containers of the prototype, gray boxes are people and "
          "external systems, the green cylinder is a data container and the dashed frame is the system boundary.")


@dataclass
class Figure:
    """One view ready to draw: nodes grouped in boxes and numbered relationships."""
    id: str
    title: str
    source: str
    groups: list  # (group id, title or None, dashed boundary?, [element ids])
    elements: dict
    relationships: list  # dicts with from, to, label, protocol, style
    details: dict  # element id -> list of secondary text lines
    stereotypes: bool
    note: str = ""
    fixed: str = ""  # curated neato -n2 source; legend always in the guide
    detail_wrap: int = 28


def lines(value, width):
    return "<BR/>".join(escape(line) for line in textwrap.wrap(value, width, break_long_words=False,
                                                                break_on_hyphens=False))


def node_style(element, outside=False):
    attrs = {"fillcolor": "#EFF6FF", "color": "#2563EB", "fontcolor": "#0F172A"}
    if outside or element["kind"] in {"actor", "external_system"}:
        attrs.update(fillcolor="#F1F5F9", color="#64748B", style="dashed,filled")
    if element["kind"] == "actor":
        attrs.update(shape="oval", style="filled")
    if element["kind"] == "datastore":
        attrs.update(shape="cylinder", fillcolor="#ECFDF5", color="#059669", style="filled")
    return attrs


def node_label(figure, eid):
    element = figure.elements[eid]
    rows = []
    if figure.stereotypes:
        rows.append(f'<TR><TD><FONT COLOR="#334155">[{KINDS[element["kind"]]}]</FONT></TD></TR>')
    rows.append(f'<TR><TD><FONT POINT-SIZE="{FONT + 2}"><B>{lines(element["name"], 20)}</B></FONT></TD></TR>')
    for detail in filter(None, figure.details.get(eid, [])):
        rows.append(f'<TR><TD><FONT COLOR="#334155">{lines(detail, figure.detail_wrap)}</FONT></TD></TR>')
    return '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="1" CELLPADDING="1">' + "".join(rows) + "</TABLE>>"


def legend_label(figure, columns):
    entries = [(f"{n:02d}", r["label"], r["protocol"]) for n, r in enumerate(figure.relationships, 1)]
    per_column = -(-len(entries) // columns)
    width = 26 if columns == 2 else 30
    stacks = []
    for column in range(columns):
        rows = "".join(f'<TR><TD ALIGN="RIGHT" VALIGN="TOP"><B>{number}</B></TD>'
                       f'<TD ALIGN="LEFT" BALIGN="LEFT" VALIGN="TOP">{lines(label, width)}<BR/>'
                       f'<FONT COLOR="#475569">{escape(protocol)}</FONT></TD></TR>'
                       for number, label, protocol in entries[column * per_column:(column + 1) * per_column])
        stacks.append(f'<TD VALIGN="TOP"><TABLE BORDER="0" CELLBORDER="0" CELLSPACING="3">{rows}</TABLE></TD>')
    footer = lines(LEGEND + (" · " + figure.note if figure.note else ""), 40 * columns)
    return ('<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="4" CELLPADDING="0">'
            f'<TR>{"".join(stacks)}</TR>'
            f'<TR><TD COLSPAN="{columns}" ALIGN="LEFT" BALIGN="LEFT"><FONT COLOR="#334155">{footer}</FONT></TD></TR>'
            "</TABLE>>")


def generate_dot(figure, rankdir, columns, edge="label"):
    graph = Digraph(figure.id, comment=f"GENERATED — sources: {figure.source} + model/architecture.yml")
    graph.attr(rankdir=rankdir, newrank="true", bgcolor="white", pad="0.15", nodesep="0.3", ranksep="0.2",
               fontname="DejaVu Sans", fontsize=str(FONT), forcelabels="true")
    if columns:
        graph.attr(labelloc="b", labeljust="l", label=legend_label(figure, columns))
    graph.attr("node", shape="box", style="rounded,filled", fontname="DejaVu Sans", fontsize=str(FONT),
               margin="0.1,0.06", penwidth="1.4")
    graph.attr("edge", fontname="DejaVu Sans", fontsize=str(FONT), color="#475569", arrowsize="0.7",
               penwidth="1.2")
    outside = {eid for _, _, dashed, members in figure.groups if dashed is None for eid in members}
    for gid, title, dashed, members in figure.groups:
        def add(target):
            for eid in members:
                attrs = node_style(figure.elements[eid], eid in outside)
                target.node(eid, node_label(figure, eid), tooltip=figure.elements[eid]["name"], **attrs)
        if title is None:
            add(graph)
            continue
        with graph.subgraph(name="cluster_" + gid) as cluster:
            cluster.attr(label=title, labelloc="t", labeljust="c", fontsize=str(FONT), fontcolor="#1E293B", margin="6",
                         color="#2563EB" if dashed else "#CBD5E1", style="dashed,rounded" if dashed else "rounded")
            add(cluster)
    for number, r in enumerate(figure.relationships, 1):
        # A real edge label reserves layout space, so numbers never sit on boxes or titles.
        graph.edge(r["from"], r["to"], **{edge: f"<<B>{number:02d}</B>>"}, id=r["id"],
                   tooltip=f"{number:02d}: {r['label']} ({r['protocol']})", style=STYLES[r["style"]])
    return graph.source


def printed_sizes(svg_path, page):
    """Return (scale, width_cm, height_cm, smallest printed point size) when inserted on `page`."""
    root = ET.parse(svg_path).getroot()
    _, _, width, height = (float(v) for v in root.get("viewBox").split())
    page_width, page_height = PAGES[page]
    sizes = [float(el.get("font-size")) for el in root.iter()
             if el.tag.endswith("text") and el.get("font-size") and "".join(el.itertext()).strip()]
    scale = min(page_width / (width * CM_PER_POINT), page_height / (height * CM_PER_POINT),
                TARGET_POINTS / min(sizes))
    return scale, width * CM_PER_POINT * scale, height * CM_PER_POINT * scale, min(sizes) * scale


def set_svg_print_size(svg_path, width_cm, height_cm):
    text = svg_path.read_text(encoding="utf-8")
    text = re.sub(r'<svg width="[^"]+" height="[^"]+"', f'<svg width="{width_cm:.2f}cm" height="{height_cm:.2f}cm"',
                  text, count=1)
    svg_path.write_text(text, encoding="utf-8")


def set_png_dpi(png_path, dpi):
    """Write a pHYs chunk so word processors insert the PNG at its printed size."""
    data = png_path.read_bytes()
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
    out = bytearray(signature)
    for kind, body in chunks:
        out += struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    png_path.write_bytes(bytes(out))


def presentation_figures(module, model_path, *, technology):
    presentation, architecture = logical.load_models(model_path)
    elements, projections = module.prepare(presentation, architecture)
    figures = []
    for view, relations in projections:
        details = {}
        for eid in view["elements"]:
            if technology:
                # Text instead of icons: icons widen every node and cost about one point of
                # printed text. One joined line keeps nodes short.
                details[eid] = [" · ".join(physical.technology_lines(elements[eid]))]
        groups = [(g["id"], g["title"], False, g["elements"]) for g in view["groups"]]
        rels = [{**r, "label": presentation["relationship_labels"][r["id"]]} for r in relations]
        figures.append(Figure(view["id"], view["title"], str(model_path.relative_to(ROOT)), groups, elements,
                              rels, details, stereotypes=False, detail_wrap=44 if technology else 28))
    return figures


def c4_expo_figures():
    presentation, architecture = logical.load_models(c4_expo.MODEL)
    figures = []
    for view, projection in c4_expo.prepare(presentation, architecture):
        elements = {e["id"]: e for e in projection.inside + projection.outside}
        rels = [{**r, "label": presentation["relationship_labels"][r["id"]]} for r in projection.relationships]
        note = C4_KEY + (" PostgreSQL/pgvector: one physical instance (ADR-018)." if projection.combined_postgres else "")
        fixed = c4_expo.generate_dot(presentation, architecture, view, projection, document=True)
        figures.append(Figure(view["id"], projection.view["title"], "model/c4_container_presentation.yml", [],
                              elements, rels, {}, stereotypes=False, note=note, fixed=fixed))
    return figures


def c4_component_figures():
    architecture = yaml.safe_load((ROOT / "model/architecture.yml").read_text(encoding="utf-8"))
    projections, _ = c4.prepare(architecture)
    layers = {layer["id"]: layer for layer in architecture["layers"]}
    figures = []
    for projection in projections:
        view = projection.view
        if view["kind"] != "c4_component":
            continue
        elements = {e["id"]: e for e in projection.inside + projection.outside}
        warnings = set()
        # Neighbours outside the boundary are context: name and technology only.
        details = {e["id"]: [part for part in (c4.technology(e, warnings),
                                               c4.description(e, layers, warnings) if e in projection.inside else "")
                             if part]
                   for e in projection.inside + projection.outside}
        container = next(e for e in architecture["elements"] if e["id"] == view["container"])
        groups = [("outside", None, None, [e["id"] for e in projection.outside]),
                  (view["container"], container["name"], True, [e["id"] for e in projection.inside])]
        figures.append(Figure(view["id"], view["title"], "model/architecture.yml", groups, elements,
                              projection.relationships, details, stereotypes=True))
    return figures


def figures():
    return (presentation_figures(logical, logical.MODEL, technology=False)
            + presentation_figures(physical, physical.MODEL, technology=True)
            + c4_expo_figures() + c4_component_figures())


def engine(figure):
    return ["neato", "-n2"] if figure.fixed else ["dot"]


def choose(figure_id, results):
    """Pick among (layout, scale, width_cm, height_cm, smallest_pt) results.

    Only compositions reaching MIN_POINTS qualify. Prefer a self-contained figure
    (legend inside), then numbers with reserved room, then larger text, then a
    smaller printed area.
    """
    passing = [r for r in results if r[4] >= MIN_POINTS]
    if not passing:
        tried = "; ".join(f"{'/'.join(map(str, layout))}: {smallest:.1f} pt" for layout, *_, smallest in results)
        raise ValueError(f"{figure_id}: no layout reaches {MIN_POINTS} pt ({tried})")
    return max(passing, key=lambda r: (r[0][2] > 0, r[0][3] == "label", round(r[4], 1), -r[2] * r[3]))


def render(figure, out=OUT, build=BUILD):
    """Render every candidate composition and keep the one `choose` selects."""
    build.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    svg = out / f"{figure.id}.svg"
    source = build / f"{figure.id}.dot"
    layouts = [(page, "fixed", 0, "xlabel") for page in PAGES] if figure.fixed else LAYOUTS
    results = []
    for layout in layouts:
        source.write_text(figure.fixed or generate_dot(figure, *layout[1:]), encoding="utf-8")
        subprocess.run([*engine(figure), "-Tsvg", str(source), "-o", str(svg)], check=True, cwd=ROOT)
        results.append((layout, *printed_sizes(svg, layout[0])))
    layout, scale, width_cm, height_cm, smallest = choose(figure.id, results)
    page, columns = layout[0], layout[2]
    source.write_text(figure.fixed or generate_dot(figure, *layout[1:]), encoding="utf-8")
    subprocess.run([*engine(figure), "-Tsvg", str(source), "-o", str(svg)], check=True, cwd=ROOT)
    set_svg_print_size(svg, width_cm, height_cm)
    png = svg.with_suffix(".png")
    subprocess.run([*engine(figure), "-Tpng", f"-Gdpi={PNG_DPI * scale:.2f}", str(source), "-o", str(png)], check=True, cwd=ROOT)
    set_png_dpi(png, PNG_DPI)
    return page, columns, width_cm, height_cm, smallest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    selected = figures()
    if args.validate_only:
        print(f"DOCUMENT FIGURES VALIDATION PASSED ({len(selected)} views)")
        return
    guide = ["# Figuras para documentos", "",
             "Variantes de impresión de las vistas de presentación y del C4 de componentes. Generado desde los",
             "mismos modelos que las vistas para diapositivas; diseño propuesto, sin acreditar implementación.", "",
             f"Cada figura se comprobó para A4 con márgenes de 2,54 cm: vertical {PAGES['portrait'][0]} × "
             f"{PAGES['portrait'][1]} cm o apaisada {PAGES['landscape'][0]} × {PAGES['landscape'][1]} cm como máximo.",
             f"Insertada al ancho indicado, ningún texto queda por debajo de {MIN_POINTS:g} pt. El PNG declara "
             f"{PNG_DPI} ppp; insertarlo al 100 % conserva ese tamaño. Reducirlo más baja la legibilidad.", "",
             "Las flechas llevan números. Si la leyenda cabe legible, va bajo el dibujo; si no, la tabla de",
             "relaciones de esa figura está al final de esta guía para colocarla junto a la figura.", "",
             "| Figura | Vista | Página | Leyenda | Ancho × alto (cm) | Texto mínimo (pt) |", "|---|---|---|---|---|---|"]
    external = []
    for figure in selected:
        page, columns, width_cm, height_cm, smallest = render(figure)
        if not columns:
            external.append(figure)
        guide.append(f"| [{figure.id}]({figure.id}.png) ([SVG]({figure.id}.svg)) | {figure.title} | "
                     f"{'vertical' if page == 'portrait' else 'apaisada'} | "
                     f"{'en la figura' if columns else 'tabla en esta guía'} | {width_cm:.1f} × {height_cm:.1f} | "
                     f"{smallest:.1f} |")
        print(f"generated: out/doc/{figure.id}.png ({page}, legend {'inside' if columns else 'in guide'}, "
              f"{width_cm:.1f}x{height_cm:.1f} cm, min {smallest:.1f} pt)")
    for figure in external:
        guide.extend(["", f"## Relaciones de {figure.id}", "",
                      f"{figure.title}. {LEGEND}. {figure.note}".rstrip(), "",
                      "| Nº | Origen → destino | Relación | Protocolo |", "|---|---|---|---|"])
        for number, r in enumerate(figure.relationships, 1):
            guide.append(f"| {number:02d} | {figure.elements[r['from']]['name']} → {figure.elements[r['to']]['name']} | "
                         f"{r['label']} | {r['protocol']} |")
    guide.append("")
    (OUT / "guia_figuras.md").write_text("\n".join(guide), encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, TypeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Document figures failed: {error}") from error
