#!/usr/bin/env python3
"""Compile the class-design SSOT into PlantUML/SVG figures and their A4 print variants.

CD-1..CD-3 render the proposed design of recommendation_service; CD-4 onward render the
bounded-context diagrams transcribed from code. Every class carries the implementation status
of model/design.yml: plain (implemented), amber (partial, divergent), red dashed (not
implemented) or gray dotted (external). ``render_documents()`` writes the print variants to
out/doc for tools/generators/document_figures.py; ``--documents`` runs it from the command line.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import re
import shutil
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "generators"))
from validate_design import load_models, validate_design  # noqa: E402
import evidence  # noqa: E402

BUILD = ROOT / "build"
OUT = ROOT / "out"
JAR = ROOT / "tools/plantuml.jar"
LAYERS = ("interfaces", "application", "domain", "infrastructure", "unlayered", "external")
COLORS = {"interfaces": "#EAF2FA", "application": "#EDF5F0",
          "domain": "#FFF7E8", "infrastructure": "#F1EFF7",
          "unlayered": "#F3F6F6", "external": "#F0F0F0"}
LAYER_LABELS = {"unlayered": "outside the layer packages"}
# Implementation status marks: inline class style and the label shown under the stereotype.
AMBER, RED, GRAY = "#B26A00", "#C62828", "#6B7280"
MARKS = {"implemented": ("", None),
         "partial": (f"line:{AMBER[1:]};line.bold", "partial"),
         "divergent": (f"line:{AMBER[1:]};line.bold", "divergent"),
         "not_implemented": (f"line:{RED[1:]};line.dashed", "not implemented"),
         "external": (f"line:{GRAY[1:]};line.dotted", "external")}
STATUS_LEGEND = (f"  Implementation at the pinned revisions (model/implementation_status.yml): plain = implemented · "
                 f"<color:{AMBER}><b>amber</b></color> = partial or divergent · "
                 f"<color:{RED}><b>red dashed</b></color> = not implemented · "
                 f"<color:{GRAY}>gray dotted</color> = external")
STATUS_LEGEND_LINES = (f"  Code status: plain = implemented · <color:{AMBER}><b>amber</b></color> = partial or divergent",
                       f"  <color:{RED}><b>red dashed</b></color> = not implemented · <color:{GRAY}>gray dotted</color> = external")
PLACEHOLDER = re.compile(r"\b(?:None|null|TBD)\b")
# Print variants (A4, 2.54 cm margins): candidate directions, wrapping and the PNG resolution.
DIRECTIONS = {"TB": "top to bottom direction", "LR": "left to right direction"}
# Print layouts: (direction, package clusters, wrap, layer anchors). wrap=k puts an invisible edge
# from each class of a layer to the k-th next one, so a rank holds at most k classes of that layer;
# anchors=False drops the invisible edges that stack the layers. The part that carries the diagram
# notes also tries them in a floating note instead of the legend.
PRINT_LAYOUTS = tuple([("TB", clusters, wrap, anchors) for clusters in (True, False) for wrap in (None, 2)
                       for anchors in (True, False)]
                      + [("LR", clusters, None, True) for clusters in (True, False)])
DOC_WRAP = 40
PNG_DPI = 300


def literal(value, allow_none=False):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("empty/non-string diagram text")
    probe = re.sub(r"\|\s*None\b", "", value) if allow_none else value
    if PLACEHOLDER.search(probe):
        raise ValueError(f"unresolved diagram text: {value!r}")
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def status_of(item):
    return item.get("implementation", {}).get("status", "implemented")


def short_refs(item):
    """Code references grouped by file: ``Incident.java:17-46, 50-89``."""
    files = {}
    for value in item.get("implementation", {}).get("evidence", []):
        ref = evidence.parse(value)
        lines = f"{ref.start}" if ref.start == ref.end else f"{ref.start}-{ref.end}"
        files.setdefault(Path(ref.path).name, [])
        if lines not in files[Path(ref.path).name]:
            files[Path(ref.path).name].append(lines)
    return [f"{name}:{', '.join(lines)}" for name, lines in files.items()]


def storage_text(item):
    storage = item.get("storage")
    if not storage:
        return None
    form, tables = storage["form"], storage.get("tables", [])
    if form == "not_persisted":
        return "not persisted"
    if form == "json_column":
        return f"JSON in {tables[0]}.{storage['columns'][0]}"
    if form == "flattened":
        return "columns of " + ", ".join(tables)
    return "maps to " + ", ".join(tables)


def annotations(item, implemented_view):
    """Note lines of a class: persistence, notes and, for code-derived views, the code references."""
    lines = []
    if item.get("persisted_as"):
        lines.append("persisted_as: " + item["persisted_as"])
    if item.get("persistence"):
        lines.extend(["Shared PostgreSQL:" if item["persistence"]["store"] == "postgresql_operational_store"
                      else "pgvector store:", *item["persistence"]["tables"]])
    text = storage_text(item)
    if text:
        lines.append(text)
    lines.extend(item.get("notes", []))
    if implemented_view and item["status"] == "implemented":
        lines.append("code: " + ", ".join(short_refs(item)))
    return lines


def member_lines(text, document, compartment="field"):
    """One class member; print variants break long signatures after top-level commas or after "): "."""
    if not document or len(text) <= DOC_WRAP:
        return [f"  {text}"]
    pieces, current, depth = [], "", 0
    for index, char in enumerate(text):
        current += char
        depth += char in "<[" and 1 or (char in ">]" and -1 or 0)
        if char == " " and text[index - 1] in ",:" and (depth == 0 or text[index - 2] == ")"):
            pieces.append(current)
            current = ""
    pieces.append(current)
    lines, current = [], ""
    for piece in pieces:
        if current.strip() and len(current) + len(piece) > DOC_WRAP:
            lines.append(current.rstrip())
            current = "\u00a0\u00a0\u00a0\u00a0" + piece
        else:
            current += piece
    lines.append(current.rstrip())
    # Continuations stay in their compartment: {method} keeps a broken signature among the methods.
    return [f"  {lines[0]}", *[f"  {{{compartment}}}{line}" for line in lines[1:]]]


def node_lines(item, *, summary=False, implemented_view=False, document=False, package=None):
    """PlantUML lines of one class. `package` (print variants without clusters) fills the box with
    its layer color and names the package on the first line."""
    kind = item.get("kind", "class")
    cid = item["id"]
    mark, label = MARKS[status_of(item)]
    stereotypes = f"<<{item['stereotype']}>>" + (f" <<{label}>>" if label else "")
    python = item.get("container_language") == "Python"
    style = ";".join(part for part in (COLORS[item["layer"]] if package else "", mark) if part)
    style = "" if not style else (style if style.startswith("#") else "#" + style)
    lines = [f'{kind} "{literal(item["name"])}" as {cid} {stereotypes}{" " + style if style else ""} {{']
    if package:
        lines.append(f"  {{field}}<i>{literal(package)}</i>")
    if not summary:
        for value in item.get("values", []):
            lines.append(f"  {literal(value)}")
        for attribute in item["attributes"]:
            optional = " [optional]" if attribute.get("nullable") and not python else ""
            lines.extend(member_lines(f'-{attribute["name"]}: {literal(attribute["type"], python)}{optional}', document))
        for method in item["methods"]:
            # Parameter types retain the contract, while names are available in SSOT.
            params = "…" if method.get("parameters_elided") else ", ".join(
                literal(p["type"], python) for p in method.get("parameters", []))
            lines.extend(member_lines(f'+{method["name"]}({params}): {literal(method["returns"], python)}', document,
                                      "method"))
    notes = [] if summary else annotations(item, implemented_view)
    inside = document or implemented_view  # code-derived views keep notes in the box; proposals keep note shapes
    if inside and notes:
        lines.append("  --")
        for note in notes:
            for part in textwrap.wrap(note, DOC_WRAP, break_long_words=False, break_on_hyphens=False):
                lines.append("  {field}<i>" + literal(part, True) + "</i>")
    lines.append("}")
    if notes and not inside:
        lines.extend([f"note bottom of {cid}",
                      *["  " + literal(note, True) for note in notes], "end note"])
    return lines


def diagram_context(design, diagram):
    rules = design["design_rules"]["containers"][diagram["container"]]
    repos = evidence.repositories()
    repo = rules["repository"]
    implemented = diagram.get("kind") == "bounded_context"
    if not implemented:
        mode = "Proposed design"
    elif diagram.get("summary_members"):
        mode = "Implemented code vs proposed design"
    else:
        mode = "Implemented code"
    revision = f"{repo}@{repos[repo]['revision']}"
    return rules, implemented, mode, revision


def package_label(layer, package, rules, implemented):
    base = rules.get("base_package")
    if implemented and base and package.startswith(base + "."):
        package = package[len(base) + 1:]
    return package


def generate_puml(design, diagram, *, document=False, members=None, title=None, direction="TB", clusters=True,
                  notes_in=None, wrap=None, anchors=True, float_notes=False):
    """PlantUML source of a figure. Print variants (`document`) may show a subset of members, drop the
    package clusters (`clusters=False`: layer fill and package line per class) and refer to the part
    that carries the diagram notes (`notes_in`)."""
    classes = {item["id"]: item for item in design["classes"]}
    rules, implemented, mode, revision = diagram_context(design, diagram)
    members = list(members or diagram["elements"])
    summary = set(diagram.get("summary_members", []))
    groups = defaultdict(lambda: defaultdict(list))
    for cid in members:
        item = {**classes[cid], "container_language": rules["language"]}
        groups[item["layer"]][package_label(item["layer"], item["package"], rules, implemented)].append(item)
    lines = [
        "@startuml",
        "' Generated from model/design.yml; do not edit manually.",
        f"' Class/proxy nodes: {len(members)}",
        DIRECTIONS[direction],
        "hide empty members",
        "hide circle",
        "skinparam classAttributeIconSize 0",
        "skinparam defaultFontName DejaVu Sans",
        "skinparam defaultFontSize 12",
        "skinparam shadowing false",
        "skinparam packageStyle rectangle",
        f"skinparam nodesep {10 if document else 40}",
        f"skinparam ranksep {18 if document else 55}",
        "skinparam ArrowColor #536578",
        "skinparam classBorderColor #536578",
        "skinparam NoteBackgroundColor #FFFFF4",
        "skinparam NoteBorderColor #C9BB8B",
        *(["skinparam legendFontSize 12", "skinparam titleFontSize 12"] if document else []),
        "title",
        *([literal(part) for part in textwrap.wrap(title or diagram["title"], 2 * DOC_WRAP - 10,
                                                    break_long_words=False)]
          if document else [literal(title or diagram["title"])]),
    ]
    if document:
        # The title carries the container line of the screen legend.
        if implemented:
            lines.append(f"{literal(mode)} · code at {revision}")
            lines.append(f"{diagram['container']} · {rules['language']} / {rules['framework']}")
        else:
            lines.append(f"{literal(mode)} · Zoom-In: {literal(diagram['zoom_target'])}")
            lines.append("recommendation_service · Java / Spring Boot · status: proposed")
        lines.extend(["end title", ""])
    else:
        lines.append(f'Zoom-In: {literal(diagram["zoom_target"])}')
        lines.append(literal(mode) + (f" · code at {revision}" if implemented else " · implementation status marked"))
        lines.extend(["end title",
                      f'footer Model {literal(design["model_version"])} - {diagram["id"]} - {mode}', ""])
    for index, layer in enumerate(LAYERS):
        if layer not in groups:
            continue
        if not clusters:
            for package, items in groups[layer].items():
                for item in items:
                    lines.extend(node_lines(item, summary=item["id"] in summary, implemented_view=implemented,
                                            document=document, package=package))
            continue
        label = LAYER_LABELS.get(layer, layer) + "\\n" + "\\n".join(groups[layer])
        lines.append(f'package "{label}" as layer_{index} {COLORS[layer]} {{')
        for items in groups[layer].values():
            for item in items:
                lines.extend("  " + line for line in node_lines(
                    item, summary=item["id"] in summary, implemented_view=implemented, document=document))
        lines.extend(["}", ""])
    # Presentation-only anchors order layer clusters vertically. They add no
    # classes or dependency semantics to the model or membership lists.
    heads = [next(iter(groups[layer].values()))[0]["id"]
             for layer in LAYERS if layer in groups]
    for before, after in zip(heads, heads[1:]) if anchors else ():
        lines.append(f"{before} -[hidden]down-> {after}")
    if wrap:
        for layer in LAYERS:
            ids = [item["id"] for items in groups.get(layer, {}).values() for item in items]
            lines.extend(f"{ids[i]} -[hidden]down-> {ids[i + wrap]}" for i in range(len(ids) - wrap))
    for rel in design["relationships"]:
        if rel["from"] not in members or rel["to"] not in members:
            continue
        lines.append(relationship_line(rel, classes))
    if document and float_notes and not notes_in and diagram.get("notes"):
        # Print variants place the diagram notes in a floating note that the layout puts beside the classes.
        lines.append('note as DiagramNotes')
        lines.append("  <b>Diagram notes</b>")
        for note in diagram["notes"]:
            parts = textwrap.wrap(note, DOC_WRAP, break_long_words=False, break_on_hyphens=False)
            lines.extend("  " + ("• " if index == 0 else "   ") + literal(part, True) for index, part in enumerate(parts))
        lines.append("end note")
    lines.extend(["", "legend bottom"])
    if implemented and not document:
        lines.append(f"  {diagram['container']} / {rules['language']} / {rules['framework']} / "
                     f"status: implemented code at {revision}")
    if implemented and summary and set(summary) & set(members):
        lines.append("  Classes without members: proposed design (status: proposed)")
    if not implemented and not document:
        lines.append("  recommendation_service / Java / Spring Boot / status: proposed")
    if not implemented and not notes_in:
        lines.append("  Logical CQRS / same PostgreSQL instance / dependencies through interfaces")
    if notes_in and diagram.get("notes"):
        lines.append(f"  Diagram notes: see {notes_in}.")
    for note in [] if notes_in or float_notes else diagram.get("notes", []):
        if document:
            lines.extend("  " + literal(part, True) for part in
                         textwrap.wrap(note, 2 * DOC_WRAP, break_long_words=False, break_on_hyphens=False))
        else:
            lines.append("  " + literal(note, True))
    if not clusters:
        lines.append("  Fill by layer: " + " ".join(f"<back:{COLORS[layer]}> {LAYER_LABELS.get(layer, layer)} </back>"
                                                 for layer in LAYERS if layer in groups))
    lines.extend(STATUS_LEGEND_LINES if document else (STATUS_LEGEND,))
    lines.extend(["endlegend", "@enduml", ""])
    return "\n".join(lines)


def relationship_line(rel, classes):
    source, target = classes[rel["from"]], classes[rel["to"]]
    missing = "not_implemented" in {status_of(source), status_of(target)}
    color = f"[{RED},dashed]" if missing else ""
    src_layer, dst_layer = LAYERS.index(source["layer"]), LAYERS.index(target["layer"])
    direction = "" if src_layer == dst_layer else ("down" if src_layer < dst_layer else "up")
    if rel.get("ownership") == "composition":
        arrow = f"*-{color}-"
    elif rel["type"] == "implements":
        arrow = f".[{RED}]{direction}.|>" if missing else f"..{direction}|>"
    elif rel["type"] == "realizes":
        arrow = f".{direction}.>"
    else:
        arrow = f"-{color}{direction}->"
    multiplicity = f' "{literal(rel["multiplicity"])}"' if rel.get("multiplicity") else ""
    label = rel.get("label", rel["type"])
    if rel.get("protocol"):
        label += " / " + rel["protocol"]
    return f'{rel["from"]} {arrow}{multiplicity} {rel["to"]} : {literal(label)}'


def navigation_markdown(design, architecture):
    """Link existing C4 figures without regenerating or changing C4 sources."""
    views = {item["id"]: item for item in architecture["views"]}
    containers = design["design_rules"]["containers"]
    lines = ["# Navegación C4 → diseño de clases", "",
             f"Modelo {design['model_version']} — CD-1..CD-3: diseño propuesto; CD-4 en adelante: código implementado", "",
             "SSOT: `model/design.yml`. Las figuras C4 existentes conservan su modelo y membresía. Cada clase marca su",
             "estado de implementación (`implementation.status`) con la evidencia de `model/implementation_status.yml`.", ""]
    for diagram in design["class_diagrams"]:
        did, zoom = diagram["id"], diagram["zoom_target"]
        nav = containers[diagram["container"]]["navigation_views"]
        if diagram.get("kind") == "bounded_context":
            nav = nav[:2]
        lines.extend([
            f"## {diagram['title']}", "",
            " → ".join([
                f"[C4 Context (`{nav[0]}`)]({nav[0]}.svg)",
                *[f"[`{vid}`]({vid}.svg)" for vid in nav[1:]],
                f"`{zoom}`", f"[{did}]({did}.svg)",
            ]), "",
            f"Zoom-In: `{zoom}`; {len(diagram['elements'])} clases/nodos, incluidos proxies.", "",
        ])
    rec_nav = containers["recommendation_service"]["navigation_views"]
    lines.extend([
        "`diagnostic_output_component` se realiza dentro de CD-2 por `DiagnosticOutputComposer` y su dominio interno.", "",
        f"La vista `{rec_nav[-1]}` amplía `{views[rec_nav[-1]]['zoom_target']}` desde `{views[rec_nav[-1]]['zoom_from']}`.", "",
        "Las clases compartidas de CD-1 son referencias al mismo diseño detallado en CD-2/CD-3; se cuentan en cada figura.", "",
        "CD-4..CD-11 amplían cada contenedor desde `c4_container_processing`: raíces de agregado, entidades y value",
        "objects del código, con su persistencia en `model/domain.yml` y referencias `archivo:línea`.", "",
    ])
    return "\n".join(lines)


def run_plantuml(paths, out_dir, fmt="svg"):
    command = ["java", "-Djava.awt.headless=true", "-DPLANTUML_LIMIT_SIZE=16384", "-jar", str(JAR), "-charset",
               "UTF-8", f"-t{fmt}", "-failfast2", "-nometadata", "-o", str(out_dir), *map(str, paths)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"PlantUML failed ({result.returncode}): {result.stdout}\n{result.stderr}")


def check_svg(svg):
    if not svg.is_file() or not svg.stat().st_size:
        raise ValueError(f"missing/empty SVG: {svg}")
    tree = ET.parse(svg)
    if tree.getroot().tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError(f"not an SVG: {svg}")
    visible = " ".join("".join(node.itertext()) for node in tree.iter("{http://www.w3.org/2000/svg}text"))
    if PLACEHOLDER.search(re.sub(r"\|\s*None\b", "", visible)):
        raise ValueError(f"unresolved visible placeholder in {svg}")


def compile_svgs(paths):
    run_plantuml(paths, OUT)
    for source in paths:
        check_svg(OUT / f"{source.stem}.svg")


# ------------------------------------------------------------------------------------------
# A4 print variants
# ------------------------------------------------------------------------------------------
def print_compositions(diagram):
    """(figure id, title, members) per part: the whole figure first, then its declared print parts."""
    whole = [(diagram["id"], diagram["title"], diagram["elements"])]
    parts = diagram.get("print_parts")
    if not parts:
        return [whole]
    base = diagram["title"].split(" — ", 1)[-1]
    split = [(f"{diagram['id']}{p['suffix']}",
              f"{diagram['id']}{p['suffix']} — {base} ({index}/{len(parts)}: {p['title']})", p["elements"])
             for index, p in enumerate(parts, 1)]
    return [whole, split]


def normalize_svg_root(svg_path):
    """PlantUML writes width/height after xmlns and in a style; set_svg_print_size expects them first."""
    text = svg_path.read_text(encoding="utf-8")
    match = re.match(r'<svg ([^>]*?)>', text)
    attrs = match.group(1)
    width = re.search(r'\bwidth="([^"]+)"', attrs).group(1)
    height = re.search(r'\bheight="([^"]+)"', attrs).group(1)
    attrs = re.sub(r'\s*\b(?:width|height)="[^"]+"', "", attrs)
    attrs = re.sub(r'style="width:[^;"]*;height:[^;"]*;', 'style="', attrs)
    svg_path.write_text(f'<svg width="{width}" height="{height}" {attrs.strip()}>' + text[match.end():],
                        encoding="utf-8")


def _figures_module():
    try:
        from . import document_figures  # type: ignore
    except ImportError:
        import document_figures  # type: ignore
    return document_figures


def measure_print(design, build):
    """Render every print candidate once and measure it on both A4 pages.

    Returns ({(figure id, layout): source path}, {figure id: [(layout, page, scale, width_cm,
    height_cm, smallest_pt)]}), layout being one of PRINT_LAYOUTS.
    """
    figures = _figures_module()
    if build.exists():
        shutil.rmtree(build)
    build.mkdir(parents=True)
    candidates = {}
    for diagram in design["class_diagrams"]:
        for composition in print_compositions(diagram):
            first = composition[0][0]
            for index, (fid, title, members) in enumerate(composition):
                # The part that carries the diagram notes also tries them as a floating note.
                floats = (False, True) if index == 0 and diagram.get("notes") else (False,)
                for layout in [(*base, float_notes) for base in PRINT_LAYOUTS for float_notes in floats]:
                    direction, clusters, wrap, anchors, float_notes = layout
                    name = (f"{fid}__{direction}{'' if clusters else '_flat'}{f'_w{wrap}' if wrap else ''}"
                            f"{'' if anchors else '_free'}{'_note' if float_notes else ''}.puml")
                    (build / name).write_text(generate_puml(
                        design, diagram, document=True, members=members, title=title, direction=direction,
                        clusters=clusters, wrap=wrap, anchors=anchors, float_notes=float_notes,
                        notes_in=first if index else None), encoding="utf-8")
                    candidates[(fid, layout)] = build / name
    run_plantuml(candidates.values(), build)
    measured = {}
    for (fid, layout), path in candidates.items():
        svg = path.with_suffix(".svg")
        check_svg(svg)
        normalize_svg_root(svg)
        for page in figures.PAGES:
            scale, width, height, smallest = figures.printed_sizes(svg, page)
            measured.setdefault(fid, []).append((layout, page, scale, width, height, smallest))
    return candidates, measured


def render_documents(out=None, build=None, models=None):
    """Write out/doc/<id>.svg|png (300 ppp) for every class figure and return their print metadata.

    Each figure is tried whole and, when declared, as its print parts: top-to-bottom or
    left-to-right, with or without package clusters, on a portrait or landscape A4 page. The whole
    figure wins when its smallest text reaches document_figures.MIN_POINTS; otherwise every part
    must reach it.
    """
    figures = _figures_module()
    out = Path(out or figures.OUT)
    build = Path(build or figures.BUILD) / "classes"
    design, architecture, domain = models or load_models(
        [ROOT / "model/design.yml", ROOT / "model/architecture.yml", ROOT / "model/domain.yml"])
    errors = validate_design(design, architecture, domain)
    if errors:
        raise ValueError("design preflight failed:\n" + "\n".join(errors))
    out.mkdir(parents=True, exist_ok=True)
    candidates, measured = measure_print(design, build)
    chosen, results = [], []
    for diagram in design["class_diagrams"]:
        selection = None
        for composition in print_compositions(diagram):
            picks = [(fid, title, best(measured[fid], figures.MIN_POINTS, figures.TARGET_POINTS))
                     for fid, title, _ in composition]
            if all(pick for _, _, pick in picks):
                selection = picks
                break
        if not selection:
            tried = "; ".join(f"{fid}: {max(o[5] for o in measured[fid]):.1f} pt" for comp in print_compositions(diagram)
                              for fid, _, _ in comp)
            raise ValueError(f"{diagram['id']}: no print composition reaches {figures.MIN_POINTS} pt (best {tried})")
        for fid, title, (layout, page, scale, width, height, smallest) in selection:
            chosen.append((fid, layout, width))
            results.append({"id": fid, "title": title, "page": page, "legend": "en la figura",
                            "width_cm": round(width, 2), "height_cm": round(height, 2), "min_pt": round(smallest, 1),
                            "diagram": diagram["id"], "source": "model/design.yml"})
    keep = {fid for fid, *_ in chosen}
    for stale in out.glob("CD-*"):
        if re.fullmatch(r"CD-\d+[a-z]?\.(?:svg|png)", stale.name) and stale.stem not in keep:
            stale.unlink()
    png_dir = build / "png"
    png_dir.mkdir()
    for (fid, layout, width), result in zip(chosen, results):
        source, svg = candidates[(fid, layout)], out / f"{fid}.svg"
        shutil.copyfile(source.with_suffix(".svg"), svg)
        figures.set_svg_print_size(svg, result["width_cm"], result["height_cm"])
        view_width = float(ET.parse(svg).getroot().get("viewBox").split()[2])
        # PlantUML rasterizes one SVG unit per pixel; scale it to 300 ppp at the printed width.
        factor = (width / 2.54 * PNG_DPI) / view_width
        text = source.read_text(encoding="utf-8").replace(
            "hide empty members", f"scale {factor:.4f}\nhide empty members", 1)
        (png_dir / f"{fid}.puml").write_text(text, encoding="utf-8")
    run_plantuml(sorted(png_dir.glob("*.puml")), png_dir, "png")
    for fid, *_ in chosen:
        png = out / f"{fid}.png"
        shutil.copyfile(png_dir / f"{fid}.png", png)
        figures.set_png_dpi(png, PNG_DPI)
    return results


def best(options, minimum, target):
    """Best (layout, page, ...) reaching `minimum` points: larger text, package clusters, portrait,
    smaller printed area, then the simplest layout (top-to-bottom, no wrap)."""
    passing = [option for option in options if option[5] >= minimum]
    if not passing:
        return None
    return max(passing, key=lambda o: (round(min(o[5], target), 1), o[0][1], o[1] == "portrait", -o[3] * o[4],
                                       o[0][0] == "TB", o[0][3], -(o[0][2] or 0), not o[0][4]))


def main(argv=None):
    defaults = [ROOT / "model/design.yml", ROOT / "model/architecture.yml", ROOT / "model/domain.yml"]
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--documents", action="store_true", help="also write the A4 print variants to out/doc")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    paths = [*args.paths, *defaults[len(args.paths):]][:3]
    try:
        design, architecture, domain = load_models(paths)
        errors = validate_design(design, architecture, domain)
        if errors:
            raise ValueError("design preflight failed:\n" + "\n".join(errors))
        # Complete all model/text preflight before touching generated files.
        sources = [(diagram, generate_puml(design, diagram)) for diagram in design["class_diagrams"]]
        navigation = navigation_markdown(design, architecture)
        BUILD.mkdir(parents=True, exist_ok=True)
        OUT.mkdir(parents=True, exist_ok=True)
        generated = []
        for diagram, source in sources:
            path = BUILD / f"{diagram['id']}.puml"
            path.write_text(source, encoding="utf-8")
            generated.append(path)
        compile_svgs(generated)
        (OUT / "navegacion_zoom.md").write_text(navigation, encoding="utf-8")
        for diagram, _ in sources:
            print(f"generated: build/{diagram['id']}.puml -> out/{diagram['id']}.svg; "
                  f"nodes={len(diagram['elements'])}")
        print("generated: out/navegacion_zoom.md")
        if args.documents:
            for figure in render_documents(models=(design, architecture, domain)):
                print(f"generated: out/doc/{figure['id']}.png ({figure['page']}, {figure['width_cm']:.1f}x"
                      f"{figure['height_cm']:.1f} cm, min {figure['min_pt']:.1f} pt)")
    except Exception as exc:
        print(f"Class generation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
