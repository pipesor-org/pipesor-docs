#!/usr/bin/env python3
"""Traceability matrix of every diagram (out/trazabilidad.md).

For each diagram, every drawn element maps to its model ID, its sources (ADR, DD, contracts)
and its implementation state with evidence (repo:path:line) from model/implementation_status.yml,
model/design.yml, model/sequence_presentation.yml and model/deployment_presentation.yml.
Generated; never edit the output by hand. It records evidence, it does not approve anything.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

import yaml

try:
    from . import c4, evidence, implementation_status
except ImportError:
    import c4
    import evidence
    import implementation_status

ROOT = evidence.ROOT
OUT = ROOT / "out" / "trazabilidad.md"
STATE_ES = {**evidence.STATUS_TEXT, None: "sin estado"}


def load(name):
    path = ROOT / "model" / name
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def sources(values):
    """ADR and DD identifiers first, then the remaining source references, deduplicated."""
    result = []
    for value in values or []:
        value = str(value)
        if match := re.fullmatch(r"SRC_ADR_(\d{3})", value):
            value = f"ADR-{match.group(1)}"
        elif match := re.search(r"(ADR-\d{3})", value):
            value = match.group(1)
        elif match := re.search(r"#(DD-\d{3})", value):
            value = match.group(1)
        if value not in result:
            result.append(value)
    return ", ".join(result) or "—"


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def refs(entry):
    if not isinstance(entry, dict):
        return "—"
    values = entry.get("evidence") or []
    text = "<br>".join(f"`{v}`" for v in values)
    reason = entry.get("reason") or entry.get("note") or ""
    return (text + ("<br>" if text and reason else "") + cell(reason)) or "—"


def state_of(entry):
    return STATE_ES.get(entry.get("status") if isinstance(entry, dict) else None, "sin estado")


def document_figures(match):
    """Document figures (out/figuras/) that `match` selects from model/document_figures.yml."""
    figures = (load("document_figures.yml") or {}).get("figures") or []
    found = [f"`out/figuras/{f['folder']}/{f['id']}.png`" for f in figures if match(f)]
    return ", ".join(found) or "—"


def c4_section(architecture, overlay):
    lines = []
    projections, _ = c4.prepare(architecture)
    elements = {e["id"]: e for e in architecture["elements"]}
    relationships = {r["id"]: r for r in architecture["relationships"]}
    arch = overlay.get("architecture") or {}
    for projection in projections:
        view = projection.view
        lines += [f"### {view['title']} (`{view['id']}`)", "",
                  f"Figuras: `out/{view['id']}.svg`" + ("" if view["kind"] != "c4_container" else ", `out/c4_expo_*`")
                  + "; para documentos: " + document_figures(
                      lambda f, v=view: f.get("view") == v["id"] or (v["kind"] == "c4_container" and f["kind"] == "c4_container"))
                  + ".", "",
                  "| Elemento dibujado | ID de modelo | Estado del modelo | Fuentes | Implementación | Evidencia |",
                  "|---|---|---|---|---|---|"]
        for node in projection.outside + projection.inside:
            if node["id"] == "aiops":
                lines.append(f"| {cell(node['name'])} | `{architecture['architecture']['id']}` | "
                             f"{architecture['architecture']['status']} | — | sistema completo | — |")
                continue
            entry = (arch.get("elements") or {}).get(node["id"])
            lines.append(f"| {cell(node['name'])} | `{node['id']}` | {node.get('status', '—')} | "
                         f"{sources(node.get('source'))} | {state_of(entry)} | {refs(entry)} |")
        lines += ["", "| Relación dibujada | ID(s) de modelo | Fuentes | Implementación | Evidencia |", "|---|---|---|---|---|"]
        for rel in projection.relationships:
            ids = rel.get("ids", [rel["id"]])
            for rid in ids:
                model_rel = relationships[rid]
                entry = (arch.get("relationships") or {}).get(rid)
                drawn = f"{elements.get(rel['from'], {'name': rel['from']}).get('name', rel['from'])} → " \
                        f"{elements.get(rel['to'], {'name': rel['to']}).get('name', rel['to'])}: {model_rel['label']}"
                if rel["from"] == "aiops" or rel["to"] == "aiops":
                    drawn = f"{rel['from']} → {rel['to']} (agregada): {model_rel['label']}"
                lines.append(f"| {cell(drawn)} | `{rid}` | {sources(model_rel.get('source'))} | {state_of(entry)} | {refs(entry)} |")
        lines.append("")
    return lines


def er_section(domain, overlay):
    dom = overlay.get("domain") or {}
    lines = ["### Modelo de datos (ER) — `out/er.svg`", "",
             "Figuras para documentos, una por esquema: " + document_figures(lambda f: f["kind"] == "data") + ".", "",
             "| Tabla | ID de entidad | Owner | Estado del modelo | Fuentes | Implementación | Evidencia (CREATE TABLE) |",
             "|---|---|---|---|---|---|---|"]
    for e in domain["entities"]:
        entry = (dom.get("entities") or {}).get(e["id"])
        lines.append(f"| `{e['schema']}.{e['table']}` | `{e['id']}` | {e.get('owner_container', '—')} | {e.get('status')} | "
                     f"{sources(e.get('source'))} | {state_of(entry)} | {refs(entry)} |")
    lines += ["", "Columnas y restricciones con estado propio:", "",
              "| Objeto | Implementación | Evidencia o motivo |", "|---|---|---|"]
    for section in ("attributes", "constraints"):
        for key, entry in (dom.get(section) or {}).items():
            lines.append(f"| `{key}` | {state_of(entry)} | {refs(entry)} |")
    verification = overlay.get("domain_verification") or {}
    lines += ["", f"Verificación estructural: {verification.get('date', '—')}, {verification.get('method', '—')}. "
              f"Divergencias registradas en {', '.join(verification.get('decisions', []))}.", ""]
    return lines


def design_section(design):
    lines = []
    classes = {c["id"]: c for c in design.get("classes", [])}
    for diagram in design.get("class_diagrams", []):
        lines += [f"### {diagram.get('title', diagram['id'])} — `out/{diagram['id']}.svg`", "",
                  "| Clase | Estereotipo | Estado de diseño | Persistencia | Implementación | Evidencia |", "|---|---|---|---|---|---|"]
        for cid in diagram.get("elements", []):
            cls = classes.get(cid, {})
            impl = cls.get("implementation") or {}
            persisted = cls.get("persisted_as")
            persisted = persisted.get("table") if isinstance(persisted, dict) else persisted
            lines.append(f"| `{cid}` | {cls.get('stereotype', '—')} | {cls.get('status', '—')} | {cell(persisted or '—')} | "
                         f"{state_of(impl)} | {refs(impl)} |")
        lines.append("")
    return lines


def walk_steps(steps, found):
    for step in steps or []:
        if "message" in step:
            found.append(step["message"])
        if "fragment" in step:
            for branch in step["fragment"].get("branches", []):
                walk_steps(branch.get("steps"), found)
    return found


def sequence_section(model):
    lines = []
    for sequence in model.get("sequences", []):
        participants = {p["id"]: p for p in sequence.get("participants", [])}
        lines += [f"### {sequence.get('title', sequence['id'])} — `out/{sequence['id']}.svg`", "",
                  "| Nº | Emisor → receptor | Mensaje | Relación del modelo | Implementación | Evidencia |", "|---|---|---|---|---|---|"]
        for number, message in enumerate(walk_steps(sequence.get("steps"), []), 1):
            names = [participants.get(message.get(end), {}).get("name", message.get(end)) for end in ("from", "to")]
            relation = f"`{message['relationship']}`" if message.get("relationship") else "implementación no modelada"
            entry = {"status": message.get("state"), "evidence": message.get("evidence"), "note": message.get("note")}
            lines.append(f"| {number} | {cell(' → '.join(map(str, names)))} | {cell(message.get('text', ''))} | {relation} | "
                         f"{state_of(entry)} | {refs(entry)} |")
        lines.append("")
    return lines


def deployment_section(model):
    lines = []
    figures = model.get("figures") or model.get("views") or []
    nodes = {n["id"]: n for n in model.get("nodes", [])}
    for figure in figures:
        members = figure.get("nodes") or figure.get("elements") or []
        lines += [f"### {figure.get('title', figure.get('id'))} — `out/{figure.get('id')}.svg`", "",
                  "| Nodo | Elemento del modelo | Estado | Evidencia o motivo |", "|---|---|---|---|"]
        for member in members:
            node = nodes.get(member, member) if isinstance(member, str) else member
            if not isinstance(node, dict):
                continue
            element = f"`{node['element']}`" if node.get("element") else "implementación no modelada"
            text = refs({"evidence": node.get("evidence"), "reason": node.get("reason")})
            lines.append(f"| {cell(node.get('name', node.get('id')))} | {element} | {node.get('state', '—')} | {text} |")
        lines.append("")
    return lines


def generate():
    architecture, domain = load("architecture.yml"), load("domain.yml")
    overlay = implementation_status.load()
    errors = implementation_status.validate(overlay, architecture, domain)
    if errors:
        raise ValueError("invalid implementation overlay:\n" + "\n".join(errors))
    repos = overlay.get("repositories", {})
    lines = ["# Matriz de trazabilidad de los diagramas", "",
             "Generada desde los modelos; no editar a mano. Cada elemento de cada diagrama remite a su ID de modelo, "
             "a sus fuentes (ADR, DD, contratos) y a la evidencia de implementación `repo:ruta:línea` en las revisiones "
             "fijadas abajo. La evidencia localiza el código; no aprueba decisiones ni acredita comportamiento en runtime.", "",
             f"Corte de evidencia: {overlay.get('evidence_cutoff', '—')}.", "",
             "| Repositorio | Ruta | Revisión |", "|---|---|---|"]
    lines += [f"| {key} | `{value['path']}` | `{value['revision']}` |" for key, value in repos.items()]
    observation = overlay.get("deployment_observation") or {}
    if observation:
        lines += ["", f"Observación de despliegue ({observation.get('environment')}, {observation.get('observed_at')}): "
                      f"{observation.get('container_apps')}; {observation.get('postgresql')}.", ""]
    lines += ["## C4", ""] + c4_section(architecture, overlay)
    lines += ["## Clases (UML)", ""] + design_section(load("design.yml"))
    lines += ["## Modelo de datos", ""] + er_section(domain, overlay)
    sequences = load("sequence_presentation.yml")
    if sequences:
        lines += ["## Secuencias", ""] + sequence_section(sequences)
    deployment = load("deployment_presentation.yml")
    if deployment:
        lines += ["## Despliegue", ""] + deployment_section(deployment)
    return "\n".join(lines).rstrip() + "\n"


def main():
    try:
        text = generate()
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as error:
        print(f"traceability failed: {error}", file=sys.stderr)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"generated: out/trazabilidad.md ({text.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
