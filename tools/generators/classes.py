#!/usr/bin/env python3
"""Compile the class-design SSOT into PlantUML/SVG figures.

CD-1..CD-3 render the proposed design of recommendation_service; CD-4 onward render the
bounded-context diagrams transcribed from code. Every class carries the implementation status
of model/design.yml: plain (implemented), amber (partial, divergent), red dashed (not
implemented) or gray dotted (external).
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import re
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
PLACEHOLDER = re.compile(r"\b(?:None|null|TBD)\b")
# Width (characters) of the note lines kept inside the class boxes of code-derived views.
NOTE_WRAP = 40


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


def node_lines(item, *, summary=False, implemented_view=False):
    """PlantUML lines of one class."""
    kind = item.get("kind", "class")
    cid = item["id"]
    mark, label = MARKS[status_of(item)]
    stereotypes = f"<<{item['stereotype']}>>" + (f" <<{label}>>" if label else "")
    python = item.get("container_language") == "Python"
    style = f" #{mark}" if mark else ""
    lines = [f'{kind} "{literal(item["name"])}" as {cid} {stereotypes}{style} {{']
    if not summary:
        for value in item.get("values", []):
            lines.append(f"  {literal(value)}")
        for attribute in item["attributes"]:
            optional = " [optional]" if attribute.get("nullable") and not python else ""
            lines.append(f'  -{attribute["name"]}: {literal(attribute["type"], python)}{optional}')
        for method in item["methods"]:
            # Parameter types retain the contract, while names are available in SSOT.
            params = "…" if method.get("parameters_elided") else ", ".join(
                literal(p["type"], python) for p in method.get("parameters", []))
            lines.append(f'  +{method["name"]}({params}): {literal(method["returns"], python)}')
    notes = [] if summary else annotations(item, implemented_view)
    inside = implemented_view  # code-derived views keep notes in the box; proposals keep note shapes
    if inside and notes:
        lines.append("  --")
        for note in notes:
            for part in textwrap.wrap(note, NOTE_WRAP, break_long_words=False, break_on_hyphens=False):
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


def generate_puml(design, diagram):
    """PlantUML source of a class figure."""
    classes = {item["id"]: item for item in design["classes"]}
    rules, implemented, mode, revision = diagram_context(design, diagram)
    members = list(diagram["elements"])
    summary = set(diagram.get("summary_members", []))
    groups = defaultdict(lambda: defaultdict(list))
    for cid in members:
        item = {**classes[cid], "container_language": rules["language"]}
        groups[item["layer"]][package_label(item["layer"], item["package"], rules, implemented)].append(item)
    lines = [
        "@startuml",
        "' Generated from model/design.yml; do not edit manually.",
        f"' Class/proxy nodes: {len(members)}",
        "top to bottom direction",
        "hide empty members",
        "hide circle",
        "skinparam classAttributeIconSize 0",
        "skinparam defaultFontName DejaVu Sans",
        "skinparam defaultFontSize 12",
        "skinparam shadowing false",
        "skinparam packageStyle rectangle",
        "skinparam nodesep 40",
        "skinparam ranksep 55",
        "skinparam ArrowColor #536578",
        "skinparam classBorderColor #536578",
        "skinparam NoteBackgroundColor #FFFFF4",
        "skinparam NoteBorderColor #C9BB8B",
        "title",
        literal(diagram["title"]),
        f'Zoom-In: {literal(diagram["zoom_target"])}',
        literal(mode) + (f" · code at {revision}" if implemented else " · implementation status marked"),
        "end title",
        f'footer Model {literal(design["model_version"])} - {diagram["id"]} - {mode}',
        "",
    ]
    for index, layer in enumerate(LAYERS):
        if layer not in groups:
            continue
        label = LAYER_LABELS.get(layer, layer) + "\\n" + "\\n".join(groups[layer])
        lines.append(f'package "{label}" as layer_{index} {COLORS[layer]} {{')
        for items in groups[layer].values():
            for item in items:
                lines.extend("  " + line for line in node_lines(
                    item, summary=item["id"] in summary, implemented_view=implemented))
        lines.extend(["}", ""])
    # Presentation-only anchors order layer clusters vertically. They add no
    # classes or dependency semantics to the model or membership lists.
    heads = [next(iter(groups[layer].values()))[0]["id"]
             for layer in LAYERS if layer in groups]
    for before, after in zip(heads, heads[1:]):
        lines.append(f"{before} -[hidden]down-> {after}")
    for rel in design["relationships"]:
        if rel["from"] not in members or rel["to"] not in members:
            continue
        lines.append(relationship_line(rel, classes))
    lines.extend(["", "legend bottom"])
    if implemented:
        lines.append(f"  {diagram['container']} / {rules['language']} / {rules['framework']} / "
                     f"status: implemented code at {revision}")
    if implemented and summary and set(summary) & set(members):
        lines.append("  Classes without members: proposed design (status: proposed)")
    if not implemented:
        lines.append("  recommendation_service / Java / Spring Boot / status: proposed")
        lines.append("  Logical CQRS / same PostgreSQL instance / dependencies through interfaces")
    for note in diagram.get("notes", []):
        lines.append("  " + literal(note, True))
    lines.extend([STATUS_LEGEND, "endlegend", "@enduml", ""])
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


def run_plantuml(paths, out_dir):
    command = ["java", "-Djava.awt.headless=true", "-DPLANTUML_LIMIT_SIZE=16384", "-jar", str(JAR), "-charset",
               "UTF-8", "-tsvg", "-failfast2", "-nometadata", "-o", str(out_dir), *map(str, paths)]
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


def main(argv=None):
    defaults = [ROOT / "model/design.yml", ROOT / "model/architecture.yml", ROOT / "model/domain.yml"]
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path)
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
    except Exception as exc:
        print(f"Class generation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
