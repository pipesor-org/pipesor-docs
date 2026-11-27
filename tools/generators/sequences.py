#!/usr/bin/env python3
"""Sequence diagrams of model/sequence_presentation.yml, validated and rendered with PlantUML.

Every message cites an existing relationship of model/architecture.yml whose ends match its
participants, or is marked implementation-only with a reason; every message carries an
implementation state and repo:path:line evidence (tools/generators/evidence.py). The generator
draws what the model and the code say; it adds no architecture and proves no runtime behaviour.

Outputs: build/<id>.puml and out/<id>.svg (full views), out/secuencias_guia.md (Spanish guide
with the evidence of every step) and, with --document or render_documents(), print variants for
A4 in out/doc/ (long sequences split at their sections, numbering kept continuous).
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

try:
    from . import evidence
except ImportError:  # executed as a script
    import evidence

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "model" / "sequence_presentation.yml"
ARCHITECTURE = ROOT / "model" / "architecture.yml"
BUILD = ROOT / "build"
OUT = ROOT / "out"
DOC_BUILD = BUILD / "doc"
DOC_OUT = OUT / "doc"
GUIDE = OUT / "secuencias_guia.md"
JAR = ROOT / "tools" / "plantuml.jar"

ID = re.compile(r"^[a-z][a-z0-9_]*$")
SEQUENCE_ID = re.compile(r"^seq_[a-z0-9_]+$")
STYLES = ("sync", "async", "reply", "self")
FRAGMENTS = ("alt", "opt", "loop", "par", "group")
SINGLE_BRANCH = ("opt", "loop", "group")
# partial, divergent and not_implemented use the colours and words of the C4 views (c4.STATE_TAGS).
STATE_COLORS = {"implemented": "#2E7D32", "partial": "#B45309", "divergent": "#6D28D9",
                "not_implemented": "#B91C1C", "external": "#607D8B"}
STATE_TAGS = {"implemented": "", "partial": "[partial]", "divergent": "[differs]",
              "not_implemented": "[not implemented]", "external": "[external]"}
STATE_LEGEND = {"implemented": "implemented", "partial": "partially implemented",
                "divergent": "implemented differently", "not_implemented": "modeled, not implemented",
                "external": "external, not verifiable in code"}
# Element kind -> (PlantUML shape, stereotype, fill). Blue: prototype, gray: people and external
# systems, green: persistence, as in the other figures.
KINDS = {"actor": ("actor", "actor", "#ECEFF1"), "external_system": ("participant", "external", "#ECEFF1"),
         "container": ("participant", "container", "#DCE9F7"), "component": ("participant", "component", "#DCE9F7"),
         "datastore": ("database", "datastore", "#E3F1E3")}
UNMODELED = "implementation-only"  # stereotype and style class of participants absent from the model
IMPLEMENTATION_ONLY = ("participant", UNMODELED, "#FFFFFF")
ARROWS = {"sync": "->", "async": "-->>", "reply": "-->", "self": "->"}
FONT = 12
TITLE_FONT = 14
# Message labels are wrapped here, not by PlantUML: a label may use the room of every lifeline gap
# its arrow spans, so long arrows keep one or two lines and short ones stay narrow.
CHARS_PER_GAP = {"full": 40, "print": 22}
MAX_CHARS = {"full": 110, "print": 60}
PER_GAP_OPTIONS = (17, 22, 30)  # label widths tried for every print candidate; the most legible wins
NOTE_CHARS = 48  # characters per note line (notes appear in the full view only)
GUARD_WRAP = {"full": 90, "print": 48}  # characters per line of a fragment guard
TITLE_WRAP = {"full": 140}  # characters per title line
FOOTER = "Generated from model/sequence_presentation.yml; evidence in out/secuencias_guia.md"
CANDIDATE_SPAN = 3  # sections added per PlantUML run while extending a print part

MODEL_KEYS = {"model_version", "purpose", "authorization", "architecture_source", "evidence_source",
              "audit_sources", "sequences"}
SEQUENCE_KEYS = {"id", "title", "purpose", "participants", "steps", "untested"}
PARTICIPANT_KEYS = {"id", "name", "element", "implementation_only", "kind", "evidence", "parent"}
MESSAGE_KEYS = {"from", "to", "style", "text", "relationship", "implementation_only", "reason", "state",
                "evidence", "idempotency", "note"}
FRAGMENT_KEYS = {"kind", "label", "branches"}
BRANCH_KEYS = {"guard", "steps"}


def text(value):
    return isinstance(value, str) and bool(value.strip())


def load_models(model_path=MODEL, architecture_path=ARCHITECTURE):
    with Path(model_path).open(encoding="utf-8") as stream:
        presentation = yaml.safe_load(stream)
    with Path(architecture_path).open(encoding="utf-8") as stream:
        architecture = yaml.safe_load(stream)
    return presentation, architecture


# --------------------------------------------------------------------------------------------
# Validation


def iter_steps(steps):
    """Depth-first (document order) walk: yields ('message'|'fragment'|'section', value)."""
    for step in steps:
        if "message" in step:
            yield "message", step["message"]
        elif "fragment" in step:
            yield "fragment", step["fragment"]
            for branch in step["fragment"]["branches"]:
                yield from iter_steps(branch["steps"])
        elif "section" in step:
            yield "section", step["section"]


def messages(steps):
    return [value for kind, value in iter_steps(steps) if kind == "message"]


class Context:
    """Architecture lookups shared by validation and rendering."""

    def __init__(self, architecture):
        self.elements = {e["id"]: e for e in architecture.get("elements", [])}
        self.relationships = {r["id"]: r for r in architecture.get("relationships", [])}

    def scope(self, participant):
        """Element that represents a participant: its element, or the parent of an implementation-only one."""
        return participant.get("element") or participant.get("parent")

    def matches(self, endpoint, element):
        """A relationship end matches a participant element, its container or one of its components."""
        if element is None:
            return False
        return (endpoint == element or self.elements.get(element, {}).get("parent") == endpoint
                or self.elements.get(endpoint, {}).get("parent") == element)


def validate(presentation, architecture, repos=None):
    """Return a list of errors; empty when the presentation model is consistent."""
    repos = evidence.repositories() if repos is None else repos
    ctx = Context(architecture)
    errors = []
    if not isinstance(presentation, dict):
        return ["presentation: expected a mapping"]
    for key in sorted(set(presentation) - MODEL_KEYS):
        errors.append(f"presentation: unknown key {key!r}")
    if presentation.get("architecture_source") != "model/architecture.yml":
        errors.append("architecture_source must be model/architecture.yml")
    sequences = presentation.get("sequences")
    if not isinstance(sequences, list) or not sequences:
        return errors + ["sequences: expected a non-empty list"]
    seen = set()
    for index, sequence in enumerate(sequences):
        where = f"sequences[{index}]"
        if not isinstance(sequence, dict):
            errors.append(f"{where}: expected a mapping")
            continue
        sid = sequence.get("id")
        if not isinstance(sid, str) or not SEQUENCE_ID.fullmatch(sid):
            errors.append(f"{where}: id must match {SEQUENCE_ID.pattern}")
        elif sid in seen:
            errors.append(f"{where}: duplicate sequence id {sid!r}")
        seen.add(sid)
        where = f"sequence {sid}"
        errors.extend(validate_sequence(sequence, ctx, repos, where))
    # Print parts are named <id>_p<n>; they must not collide with another sequence.
    for sid in seen:
        if isinstance(sid, str) and re.fullmatch(r".+_p\d+", sid) and re.sub(r"_p\d+$", "", sid) in seen:
            errors.append(f"sequence {sid}: id collides with a print part of another sequence")
    return errors


def validate_sequence(sequence, ctx, repos, where):
    errors = [f"{where}: unknown key {key!r}" for key in sorted(set(sequence) - SEQUENCE_KEYS)]
    for key in ("title", "purpose"):
        if not text(sequence.get(key)):
            errors.append(f"{where}: {key} is required")
    untested = sequence.get("untested", [])
    if not isinstance(untested, list) or not all(text(item) for item in untested):
        errors.append(f"{where}: untested must be a list of texts")
    participants = sequence.get("participants")
    known = {}
    if not isinstance(participants, list) or not participants:
        errors.append(f"{where}: participants must be a non-empty list")
        participants = []
    for participant in participants:
        if not isinstance(participant, dict):
            errors.append(f"{where}: participant must be a mapping")
            continue
        pid = participant.get("id")
        pwhere = f"{where} participant {pid}"
        if not isinstance(pid, str) or not ID.fullmatch(pid):
            errors.append(f"{pwhere}: invalid id")
            continue
        if pid in known:
            errors.append(f"{pwhere}: duplicate participant id")
        known[pid] = participant
        errors.extend(f"{pwhere}: unknown key {key!r}" for key in sorted(set(participant) - PARTICIPANT_KEYS))
        if not text(participant.get("name")):
            errors.append(f"{pwhere}: name is required")
        element = participant.get("element")
        if participant.get("implementation_only") is True:
            if element is not None:
                errors.append(f"{pwhere}: an implementation-only participant cannot name an element")
            if not text(participant.get("kind")):
                errors.append(f"{pwhere}: kind is required for an implementation-only participant")
            errors.extend(evidence.validate_refs(participant.get("evidence"), repos, pwhere))
            parent = participant.get("parent")
            if parent is not None and parent not in ctx.elements:
                errors.append(f"{pwhere}: unknown parent element {parent!r}")
        else:
            if "implementation_only" in participant:
                errors.append(f"{pwhere}: implementation_only must be true when present")
            for key in ("kind", "evidence", "parent"):
                if key in participant:
                    errors.append(f"{pwhere}: {key} only applies to implementation-only participants")
            if element not in ctx.elements:
                errors.append(f"{pwhere}: unknown architecture element {element!r}")
            elif ctx.elements[element].get("status") == "open_question":
                errors.append(f"{pwhere}: element {element!r} is an open question")
            elif ctx.elements[element].get("kind") not in KINDS:
                errors.append(f"{pwhere}: unsupported element kind {ctx.elements[element].get('kind')!r}")
    steps = sequence.get("steps")
    if not isinstance(steps, list) or not steps:
        return errors + [f"{where}: steps must be a non-empty list"]
    used = set()
    errors.extend(validate_steps(steps, ctx, repos, known, used, where, top=True))
    if not errors:
        if not messages(steps):
            errors.append(f"{where}: no messages")
        for pid in known:
            if pid not in used:
                errors.append(f"{where}: participant {pid!r} is never used")
    return errors


def validate_steps(steps, ctx, repos, known, used, where, top):
    errors = []
    if not isinstance(steps, list) or not steps:
        return [f"{where}: steps must be a non-empty list"]
    if not any(isinstance(s, dict) and ("message" in s or "fragment" in s) for s in steps):
        errors.append(f"{where}: needs at least one message or fragment")
    for index, step in enumerate(steps):
        swhere = f"{where} step {index + 1}"
        if not isinstance(step, dict) or len(step) != 1 or next(iter(step)) not in ("message", "fragment", "section"):
            errors.append(f"{swhere}: a step is exactly one of message, fragment or section")
            continue
        kind, value = next(iter(step.items()))
        if kind == "section":
            if not top:
                errors.append(f"{swhere}: sections are only allowed at the top level")
            if not text(value):
                errors.append(f"{swhere}: section title is required")
        elif kind == "message":
            errors.extend(validate_message(value, ctx, repos, known, used, swhere))
        else:
            errors.extend(validate_fragment(value, ctx, repos, known, used, swhere))
    return errors


def validate_fragment(fragment, ctx, repos, known, used, where):
    if not isinstance(fragment, dict):
        return [f"{where}: fragment must be a mapping"]
    errors = [f"{where}: unknown fragment key {key!r}" for key in sorted(set(fragment) - FRAGMENT_KEYS)]
    kind = fragment.get("kind")
    if kind not in FRAGMENTS:
        errors.append(f"{where}: fragment kind must be one of {', '.join(FRAGMENTS)}")
    if not text(fragment.get("label")):
        errors.append(f"{where}: fragment label is required")
    branches = fragment.get("branches")
    if not isinstance(branches, list) or not branches:
        return errors + [f"{where}: fragment has no branches"]
    if kind in SINGLE_BRANCH and len(branches) != 1:
        errors.append(f"{where}: {kind} takes exactly one branch")
    if kind in ("alt", "par") and len(branches) < 2:
        errors.append(f"{where}: {kind} needs at least two branches")
    for index, branch in enumerate(branches):
        bwhere = f"{where} branch {index + 1}"
        if not isinstance(branch, dict):
            errors.append(f"{bwhere}: branch must be a mapping")
            continue
        errors.extend(f"{bwhere}: unknown branch key {key!r}" for key in sorted(set(branch) - BRANCH_KEYS))
        if not text(branch.get("guard")):
            errors.append(f"{bwhere}: guard is required")
        steps = branch.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"{bwhere}: empty fragment branch")
            continue
        errors.extend(validate_steps(steps, ctx, repos, known, used, bwhere, top=False))
    return errors


def validate_message(message, ctx, repos, known, used, where):
    if not isinstance(message, dict):
        return [f"{where}: message must be a mapping"]
    errors = [f"{where}: unknown message key {key!r}" for key in sorted(set(message) - MESSAGE_KEYS)]
    source, target, style = message.get("from"), message.get("to"), message.get("style")
    for end in (source, target):
        if end not in known:
            errors.append(f"{where}: unknown participant {end!r}")
        else:
            used.add(end)
    if style not in STYLES:
        errors.append(f"{where}: style must be one of {', '.join(STYLES)}")
    elif (style == "self") != (source == target):
        errors.append(f"{where}: style self is required exactly when from and to are the same participant")
    if not text(message.get("text")):
        errors.append(f"{where}: text is required")
    if message.get("state") not in evidence.STATUSES:
        errors.append(f"{where}: state must be one of {', '.join(evidence.STATUSES)}")
    for key in ("idempotency", "note"):
        if key in message and not text(message[key]):
            errors.append(f"{where}: {key} must be a non-empty text")
    errors.extend(evidence.validate_refs(message.get("evidence"), repos, where))
    relationship = message.get("relationship")
    if message.get("implementation_only") is True:
        if relationship is not None:
            errors.append(f"{where}: an implementation-only message cannot cite a relationship")
        if not text(message.get("reason")):
            errors.append(f"{where}: implementation-only messages need a reason")
        return errors
    if "implementation_only" in message:
        errors.append(f"{where}: implementation_only must be true when present")
    if "reason" in message:
        errors.append(f"{where}: reason only applies to implementation-only messages")
    if style == "self":
        return errors + [f"{where}: internal (self) steps are implementation-only"]
    if relationship is None:
        return errors + [f"{where}: cite a relationship or mark the message implementation_only with a reason"]
    rel = ctx.relationships.get(relationship)
    if rel is None:
        return errors + [f"{where}: unknown relationship {relationship!r}"]
    if rel.get("status") == "open_question":
        errors.append(f"{where}: relationship {relationship!r} is an open question")
    if source in known and target in known:
        first, second = ctx.scope(known[source]), ctx.scope(known[target])
        if style == "reply":
            first, second = second, first
        if not (ctx.matches(rel["from"], first) and ctx.matches(rel["to"], second)):
            errors.append(f"{where}: relationship {relationship!r} ({rel['from']} -> {rel['to']}) does not match "
                          f"{source} -> {target}" + (" (reply runs it backwards)" if style == "reply" else ""))
    return errors


# --------------------------------------------------------------------------------------------
# PlantUML


def creole(value):
    """Escape PlantUML creole markup in model text ('~' is creole's escape, so a literal one is a code point)."""
    value = value.replace("~", "\0")
    for token in ("<", "**", "//", "__", "--", "\"\""):
        value = value.replace(token, "~" + token)
    return value.replace("\0", "<U+007E>")


def wrap_text(value, width):
    """Greedy word wrap; words longer than a line break after '/', '_', '?', '&', ',', '.', '=' or '-'."""
    pieces = []  # (text, glued to the previous piece)
    for word in value.split():
        if len(word) <= width:
            pieces.append((word, False))
            continue
        chunk, glued = "", False
        for segment in (s for s in re.findall(r"[^/_?&,.=-]*[/_?&,.=-]?", word) if s):
            if chunk and len(chunk) + len(segment) > width:
                pieces.append((chunk, glued))
                chunk, glued = "", True
            chunk += segment
        pieces.append((chunk, glued))
    lines = []
    for piece, glued in pieces:
        joiner = "" if glued else " "
        if lines and len(lines[-1]) + len(joiner) + len(piece) <= width:
            lines[-1] += joiner + piece
        else:
            lines.append(piece)
    return lines


def wrapped(value, width):
    return "\\n".join(creole(line) for line in wrap_text(value, width))


def participant_line(participant, ctx):
    if participant.get("implementation_only"):
        shape, stereotype, fill = IMPLEMENTATION_ONLY
    else:
        shape, stereotype, fill = KINDS[ctx.elements[participant["element"]]["kind"]]
    return f'{shape} "{participant["name"]}" as {participant["id"]} <<{stereotype}>> {fill}'


def message_label(message, width):
    lines = [creole(line) for line in wrap_text(message["text"], width)]
    if message.get("implementation_only"):
        lines = [f"<i>{line}</i>" for line in lines]
    tag = STATE_TAGS[message["state"]]
    if tag:
        tag = f"<color:{STATE_COLORS[message['state']]}><b>{tag}</b></color>"
        if len(lines[-1]) + len(STATE_TAGS[message["state"]]) < width:
            lines[-1] += " " + tag
        else:
            lines.append(tag)
    return "\\n".join(lines)


def label_width(message, order, mode, per_gap=None):
    """Characters per line: the room of the lifeline gaps the arrow spans."""
    span = max(abs(order[message["to"]] - order[message["from"]]), 1)
    return min((per_gap or CHARS_PER_GAP[mode]) * span, MAX_CHARS[mode])


def legend_lines(mode):
    """Short lines: arrow colour and tag give the implementation state of each message."""
    def item(state, text=None):
        tag = STATE_TAGS[state]
        return (f"<color:{STATE_COLORS[state]}>━━</color> " + (f"<b>{tag}</b> " if tag else "")
                + (text or STATE_LEGEND[state]))
    return ["legend bottom left",
            f"Arrow colour and tag: {item('implemented')}   {item('partial', 'in part')}",
            f"{item('divergent')}   {item('not_implemented', 'modeled only')}",
            f"{item('external', 'not verifiable in code')}   <i>italic</i>: implemented, not modeled",
            "──▶ call   ╌╌▶ reply   ╌╌▷ asynchronous   dashed box: not in architecture.yml",
            # Print variants hide the stereotypes, as the other document figures do.
            *(["Boxes: blue container or component · gray external system or person · green datastore"]
              if mode == "print" else []),
            "endlegend"]


def header(title, mode, start):
    return ["@startuml",
            "skinparam shadowing false",
            f"skinparam defaultFontSize {FONT}",
            *(f"skinparam {name}FontSize {FONT}" for name in
              ("participant", "actor", "database", "arrow", "note", "legend", "footer", "sequenceGroup",
               "sequenceGroupHeader", "sequenceDivider", "sequenceStereotype", "sequenceBox", "sequenceReference")),
            f"skinparam titleFontSize {TITLE_FONT}",
            "skinparam sequenceLifeLineBorderColor #9E9E9E",
            "skinparam legendBackgroundColor #FFFFFF",
            "skinparam legendBorderColor #9E9E9E",
            "<style>",
            "participant {",
            f"  .{UNMODELED} {{",
            "    LineStyle 5-3",
            "    LineColor #707070",
            "  }",
            "}",
            "</style>",
            "hide footbox",
            *(["hide stereotype"] if mode == "print" else []),
            # Print variants carry their title in the document caption, as the other document figures.
            *([f"title {wrapped(title, TITLE_WRAP[mode])}"] if mode == "full" else []),
            f"autonumber {start}"]


def emit(steps, mode, order, lines, depth=0, per_gap=None):
    pad = "  " * depth
    for step in steps:
        if "section" in step:
            lines.append(f"== {creole(step['section'])} ==")
        elif "message" in step:
            m = step["message"]
            color = STATE_COLORS[m["state"]]
            arrow = ARROWS[m["style"]]
            label = message_label(m, label_width(m, order, mode, per_gap))
            lines.append(f"{pad}{m['from']} -[{color}]{arrow[1:]} {m['to']} : {label}")
            if mode == "full" and m.get("note"):
                lines.append(f"{pad}note right #FFF8E1: {wrapped(m['note'], NOTE_CHARS)}")
        else:
            f = step["fragment"]
            for index, branch in enumerate(f["branches"]):
                guard = wrapped(branch["guard"], GUARD_WRAP[mode])
                if f["kind"] == "loop":
                    guard = wrapped(f["label"], GUARD_WRAP[mode])
                elif f["kind"] == "group":
                    guard = f"{wrapped(f['label'], GUARD_WRAP[mode])} [{guard}]"
                lines.append(f"{pad}{f['kind'] if index == 0 else 'else'} {guard}")
                emit(branch["steps"], mode, order, lines, depth + 1, per_gap)
            lines.append(f"{pad}end")


def generate_puml(sequence, ctx, *, mode="full", steps=None, start=1, title=None, participants=None, per_gap=None):
    """PlantUML source of a sequence (or of a print part when steps/participants are given)."""
    steps = sequence["steps"] if steps is None else steps
    if participants is None:
        participants = sequence["participants"]
    lines = header(title or sequence["title"], mode, start)
    lines.extend(participant_line(p, ctx) for p in participants)
    emit(steps, mode, {p["id"]: index for index, p in enumerate(participants)}, lines, per_gap=per_gap)
    lines.extend(legend_lines(mode))
    lines.extend([f"footer {creole(FOOTER)}", "@enduml", ""])
    return "\n".join(lines)


def plantuml(paths, out_dir, fmt="svg"):
    """Compile PlantUML sources into out_dir (absolute) and return the produced files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    command = ["java", "-Djava.awt.headless=true", "-DPLANTUML_LIMIT_SIZE=16384", "-jar", str(JAR),
               "-charset", "UTF-8", f"-t{fmt}", "-failfast2", "-nometadata", "-o", str(out_dir.resolve()),
               *map(str, paths)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"PlantUML failed ({result.returncode}): {result.stdout}{result.stderr}".strip())
    produced = [out_dir / f"{Path(p).stem}.{fmt}" for p in paths]
    for path in produced:
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"PlantUML did not produce {path}")
    return produced


def normalize_svg(path):
    """Put width/height first on the root and drop the CSS size, so the print size can be set."""
    data = path.read_text(encoding="utf-8")
    start = data.index("<svg")
    end = data.index(">", start)
    head = data[start:end]
    width = re.search(r' width="([^"]+)"', head).group(1)
    height = re.search(r' height="([^"]+)"', head).group(1)
    head = re.sub(r' (?:width|height)="[^"]+"', "", head)
    head = re.sub(r"width:[^;\"]+;height:[^;\"]+;", "", head)
    head = head.replace("<svg", f'<svg width="{width}" height="{height}"', 1)
    path.write_text(data[:start] + head + data[end:], encoding="utf-8")


# --------------------------------------------------------------------------------------------
# Guide


def numbered(steps):
    """[(number or None, kind, value, depth)] in document order; messages are numbered from 1."""
    rows, counter = [], [0]

    def walk(items, depth):
        for step in items:
            if "message" in step:
                counter[0] += 1
                rows.append((counter[0], "message", step["message"], depth))
            elif "section" in step:
                rows.append((None, "section", step["section"], depth))
            else:
                rows.append((None, "fragment", step["fragment"], depth))
                for branch in step["fragment"]["branches"]:
                    first = counter[0] + 1
                    walk(branch["steps"], depth + 1)
                    branch_range = (first, counter[0])
                    rows.append((None, "branch", (branch, branch_range), depth))
    walk(steps, 0)
    return rows


def cell(value):
    return value.replace("|", "\\|").replace("\n", " ")


def guide(presentation, ctx, repos):
    names = {}
    lines = ["# Diagramas de secuencia: guía y evidencia", "",
             "Generado por `tools/generators/sequences.py` desde `model/sequence_presentation.yml`; no editar a mano.",
             "Autorizado por el responsable el 27/11/2026 (decisión 1): cada mensaje cita una relación `rel_*`",
             "existente de `model/architecture.yml` o se marca como implementación no modelada, siempre con estado",
             "y evidencia `repo:ruta:línea`. Lo implementado y no modelado no se ha añadido a la arquitectura.", "",
             "**Alcance de la evidencia.** Un diagrama generado no acredita comportamiento en runtime. La evidencia",
             "es código o IaC en la revisión fijada (tabla siguiente), leída en una auditoría de solo lectura del",
             "27/11/2026, no una ejecución observada. Las decisiones pendientes y preguntas abiertas que se",
             "mencionan en las notas siguen abiertas: el diagrama las señala, no las resuelve.", "",
             "| Repositorio | Clon | Revisión |", "|---|---|---|"]
    cited = {evidence.parse(ref).repo for ref in evidence.collect(presentation)}
    for key, entry in repos.items():
        if key in cited:
            lines.append(f"| `{key}` | `{entry['path']}` | `{entry['revision']}` |")
    lines += ["", "## Cómo leer los diagramas", "",
              "- Color de la flecha y etiqueta = estado de implementación: "
              + "; ".join(f"{STATE_LEGEND[s]} = {evidence.STATUS_TEXT[s]}" + (f" (`{STATE_TAGS[s]}`)" if STATE_TAGS[s] else "")
                          for s in evidence.STATUSES) + ".",
              "- Texto en cursiva: implementación no modelada (sin relación en `architecture.yml`). Las cajas blancas",
              "  con borde discontinuo («implementation-only») son participantes que solo existen en el código.",
              "- Flecha continua: llamada síncrona. Discontinua con punta abierta: mensaje asíncrono (broker, cola,",
              "  outbox). Discontinua con punta llena: respuesta. Flecha sobre el mismo participante: paso interno.",
              "- Una relación del contenedor se acepta para un participante componente y al revés; las respuestas",
              "  recorren la relación en sentido inverso.",
              "- Las notas solo aparecen en la vista completa (`out/<id>.svg`); en la impresión están en esta guía.",
              "- La impresión omite el título (va en el pie de figura del documento) y los estereotipos, como las",
              "  demás figuras para documentos: azul, contenedor o componente; gris, sistema externo o persona; verde,",
              "  almacén de datos; blanca con borde discontinuo, implementación no modelada.",
              "- Las variantes de impresión A4 (`out/doc/seq_*`) dividen las secuencias largas por secciones en",
              "  partes con numeración continua; sus tamaños están en `out/doc/guia_figuras.md`.", ""]
    for sequence in presentation["sequences"]:
        participants = {p["id"]: p for p in sequence["participants"]}
        names = {pid: p["name"] for pid, p in participants.items()}
        all_messages = messages(sequence["steps"])
        counts = {s: sum(1 for m in all_messages if m["state"] == s) for s in evidence.STATUSES}
        unmodeled = sum(1 for m in all_messages if m.get("implementation_only"))
        lines += [f"## {sequence['id']}: {sequence['title']}", "",
                  f"Figura completa: [{sequence['id']}.svg]({sequence['id']}.svg). Fuente: `build/{sequence['id']}.puml`.", "",
                  sequence["purpose"].strip(), "",
                  f"{len(all_messages)} mensajes: "
                  + ", ".join(f"{counts[s]} {evidence.STATUS_TEXT[s]}" for s in evidence.STATUSES if counts[s])
                  + f"; {unmodeled} de implementación no modelada.", "",
                  "### Participantes", "",
                  "| Alias | Nombre | Elemento del modelo | Evidencia |", "|---|---|---|---|"]
        for p in sequence["participants"]:
            if p.get("implementation_only"):
                inside = f" dentro de `{p['parent']}`" if p.get("parent") else ""
                element = f"implementación no modelada{inside}: {cell(p['kind'])}"
                refs = "<br>".join(f"`{r}`" for r in p["evidence"])
            else:
                element = f"`{p['element']}` ({ctx.elements[p['element']]['kind']})"
                refs = ""
            lines.append(f"| `{p['id']}` | {cell(p['name'])} | {element} | {refs} |")
        lines += ["", "### Pasos", "",
                  "| Nº | emisor → receptor | mensaje | estado | relación del modelo o «implementación no modelada» | evidencia (repo:ruta:línea) |",
                  "|---|---|---|---|---|---|"]
        fragments = []
        for number, kind, value, depth in numbered(sequence["steps"]):
            if kind == "section":
                lines.append(f"| | **{cell(value)}** | | | | |")
            elif kind == "fragment":
                fragments.append((value, depth, []))
            elif kind == "branch":
                branch, (first, last) = value
                for fragment, fdepth, branches in reversed(fragments):
                    if any(b is branch for b in fragment["branches"]) and len(branches) < len(fragment["branches"]):
                        branches.append((branch["guard"], first, last))
                        break
            else:
                m = value
                body = cell(m["text"])
                if m.get("idempotency"):
                    body += f"<br>*Idempotencia:* {cell(m['idempotency'])}"
                if m.get("note"):
                    body += f"<br>*Nota:* {cell(m['note'])}"
                if m.get("implementation_only"):
                    relation = f"implementación no modelada: {cell(m['reason'])}"
                else:
                    rel = ctx.relationships[m["relationship"]]
                    relation = f"`{m['relationship']}` ({cell(rel.get('label', ''))})"
                refs = "<br>".join(f"`{r}`" for r in m["evidence"])
                arrow = f"{names[m['from']]} → {names[m['to']]}" + ("" if m["style"] in ("sync",) else f" ({m['style']})")
                lines.append(f"| {number} | {cell(arrow)} | {body} | {evidence.STATUS_TEXT[m['state']]} | "
                             f"{relation} | {refs} |")
        lines += ["", "### Fragmentos", ""]
        for fragment, depth, branches in fragments:
            indent = "  " * depth
            lines.append(f"{indent}- `{fragment['kind']}` {cell(fragment['label'])}:")
            for guard, first, last in branches:
                span = "sin mensajes" if last < first else (f"paso {first}" if first == last else f"pasos {first}–{last}")
                lines.append(f"{indent}  - [{cell(guard)}] → {span}")
        lines += ["", "### Sin prueba de integración", "",
                  "Según la auditoría de solo lectura del 27/11/2026; no se ha ejecutado ningún flujo para esta guía.", ""]
        lines += [f"- {item}" for item in sequence.get("untested", [])]
        lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------------------------
# Print variants


@dataclass
class Part:
    id: str
    title: str
    sequence: dict
    steps: list
    start: int
    participants: list
    per_gap: int = CHARS_PER_GAP["print"]

    def puml(self, ctx):
        return generate_puml(self.sequence, ctx, mode="print", steps=self.steps, start=self.start,
                             title=self.title, participants=self.participants, per_gap=self.per_gap)


def sections(sequence):
    """Split the top-level steps at each section marker."""
    groups = []
    for step in sequence["steps"]:
        if "section" in step or not groups:
            groups.append([])
        groups[-1].append(step)
    return groups


def part_of(sequence, groups, first, last, title_suffix, per_gap=CHARS_PER_GAP["print"]):
    """Sections first..last of a sequence, with the lifelines they use and continuous numbering."""
    steps = [step for group in groups[first:last + 1] for step in group]
    start = 1 + sum(len(messages(group)) for group in groups[:first])
    used = set()
    for m in messages(steps):
        used.update((m["from"], m["to"]))
    participants = [p for p in sequence["participants"] if p["id"] in used]
    return Part("", sequence["title"] + title_suffix, sequence, steps, start, participants, per_gap)


def measure(parts, ctx, directory):
    """Render candidate parts in one PlantUML run and return their printed sizes per page."""
    doc = _document_figures()
    sources = []
    for index, part in enumerate(parts):
        source = directory / f"candidate_{index:03d}.puml"
        source.write_text(part.puml(ctx), encoding="utf-8")
        sources.append(source)
    return [{page: doc.printed_sizes(svg, page) for page in doc.PAGES} for svg in plantuml(sources, directory)]


def plan_parts(sequence, ctx, directory):
    """Split a sequence at section boundaries into the fewest parts legible on an A4 page.

    Returns [(first group, last group, page, label width)]. A uniform orientation is preferred
    when it needs no more parts than a mixed one; portrait wins ties.
    """
    doc = _document_figures()
    groups = sections(sequence)
    best = {}  # (first, last) -> {page: (smallest printed pt, label width)}

    def legible(first, last):
        if (first, last) not in best:
            # One PlantUML run measures the next few extensions of a part that starts at `first`.
            ends = range(last, min(last + CANDIDATE_SPAN, len(groups)))
            keys = [(end, width) for end in ends for width in PER_GAP_OPTIONS]
            candidates = [part_of(sequence, groups, first, end, "", width) for end, width in keys]
            for (end, width), result in zip(keys, measure(candidates, ctx, directory)):
                entry = best.setdefault((first, end), {})
                for page in doc.PAGES:
                    if page not in entry or result[page][3] > entry[page][0]:
                        entry[page] = (result[page][3], width)
        return best[(first, last)]

    def fits(first, last, pages):
        return any(legible(first, last)[page][0] >= doc.MIN_POINTS for page in pages)

    def greedy(pages):
        plan, first = [], 0
        while first < len(groups):
            if not fits(first, first, pages):
                return None
            last = first
            while last + 1 < len(groups) and fits(first, last + 1, pages):
                last += 1
            page = next(p for p in pages if legible(first, last)[p][0] >= doc.MIN_POINTS)
            plan.append((first, last, page, legible(first, last)[page][1]))
            first = last + 1
        return plan

    plans = [plan for plan in (greedy(("portrait",)), greedy(("landscape",))) if plan]
    mixed = greedy(("portrait", "landscape"))
    if mixed is None:
        bad = next(i for i in range(len(groups)) if not fits(i, i, tuple(doc.PAGES)))
        title = groups[bad][0].get("section", "(untitled)")
        raise ValueError(f"{sequence['id']}: section {title!r} does not reach {doc.MIN_POINTS} pt on an A4 page")
    uniform = min(plans, key=len) if plans else None
    return uniform if uniform and len(uniform) <= len(mixed) else mixed


def print_parts(sequence, ctx, directory):
    groups = sections(sequence)
    plan = plan_parts(sequence, ctx, directory)
    parts = []
    for number, (first, last, page, width) in enumerate(plan, 1):
        suffix = "" if len(plan) == 1 else f" (part {number} of {len(plan)})"
        part = part_of(sequence, groups, first, last, suffix, width)
        part.id = sequence["id"] if len(plan) == 1 else f"{sequence['id']}_p{number}"
        parts.append((part, page))
    return parts


def _document_figures():
    # Imported on use: document_figures may import this module to collect the print variants.
    try:
        from . import document_figures
    except ImportError:
        import document_figures
    return document_figures


def render_parts(planned, ctx, out, build, scratch):
    """Render [(part, page)] in two PlantUML runs (SVG, then PNG at 300 dpi of the printed width)."""
    doc = _document_figures()
    sources = []
    for part, _ in planned:
        source = build / f"{part.id}.puml"
        source.write_text(part.puml(ctx), encoding="utf-8")
        sources.append(source)
    svgs = plantuml(sources, out)
    figures, png_sources = [], []
    for (part, page), source, svg in zip(planned, sources, svgs):
        normalize_svg(svg)
        _, width_cm, height_cm, smallest = doc.printed_sizes(svg, page)
        if smallest < doc.MIN_POINTS:
            raise ValueError(f"{part.id}: smallest text {smallest:.1f} pt on {page}")
        doc.set_svg_print_size(svg, width_cm, height_cm)
        view_width = float(re.search(r'viewBox="[\d.]+ [\d.]+ ([\d.]+)', svg.read_text(encoding="utf-8")).group(1))
        # PlantUML draws one pixel per SVG unit at 96 dpi; scale it to PNG_DPI at the printed width.
        dpi = round(96 * (width_cm / 2.54 * doc.PNG_DPI) / view_width)
        png_source = scratch / f"{part.id}.puml"
        png_source.write_text(source.read_text(encoding="utf-8").replace(
            "@startuml\n", f"@startuml\nskinparam dpi {dpi}\n", 1), encoding="utf-8")
        png_sources.append(png_source)
        figures.append({"id": part.id, "title": part.title, "page": page, "legend": "en la figura",
                        "width_cm": round(width_cm, 2), "height_cm": round(height_cm, 2),
                        "min_pt": round(smallest, 2)})
    for png in plantuml(png_sources, out, "png"):
        doc.set_png_dpi(png, doc.PNG_DPI)
    return figures


def render_part(part, page, ctx, out, build, scratch):
    return render_parts([(part, page)], ctx, out, build, scratch)[0]


def render_documents(out=DOC_OUT, build=DOC_BUILD, model_path=MODEL, architecture_path=ARCHITECTURE):
    """Print variants for A4 (out/doc/<id>.svg and .png at 300 dpi); returns one dict per figure.

    Each dict has id, title, page ('portrait' or 'landscape'), legend ('en la figura'), width_cm,
    height_cm and min_pt (smallest printed text once inserted at that size).
    """
    presentation, architecture = load_models(model_path, architecture_path)
    errors = validate(presentation, architecture)
    if errors:
        raise ValueError("sequence presentation invalid:\n" + "\n".join(errors))
    ctx = Context(architecture)
    out, build = Path(out), Path(build)
    out.mkdir(parents=True, exist_ok=True)
    build.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pipesor-seq-") as tmp:
        scratch = Path(tmp)
        directories = []
        for sequence in presentation["sequences"]:
            directories.append(scratch / sequence["id"])
            directories[-1].mkdir()
        # Sequences are planned independently; results keep the model order.
        with ThreadPoolExecutor(max_workers=len(directories)) as pool:
            plans = list(pool.map(lambda args: print_parts(args[0], ctx, args[1]),
                                  zip(presentation["sequences"], directories)))
        planned = [item for plan in plans for item in plan]
        expected = {part.id for part, _ in planned}
        for stale in [*out.glob("seq_*.svg"), *out.glob("seq_*.png"), *build.glob("seq_*.puml")]:
            if stale.stem not in expected:
                stale.unlink()
        return render_parts(planned, ctx, out, build, scratch)


# --------------------------------------------------------------------------------------------


def render_full(presentation, ctx, out=OUT, build=BUILD):
    out.mkdir(parents=True, exist_ok=True)
    build.mkdir(parents=True, exist_ok=True)
    expected = {s["id"] for s in presentation["sequences"]}
    for stale in [*out.glob("seq_*.svg"), *build.glob("seq_*.puml")]:
        if stale.stem not in expected:
            stale.unlink()
    sources = []
    for sequence in presentation["sequences"]:
        source = build / f"{sequence['id']}.puml"
        source.write_text(generate_puml(sequence, ctx), encoding="utf-8")
        sources.append(source)
    svgs = plantuml(sources, out)
    for svg in svgs:
        normalize_svg(svg)
    return svgs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--validate-only", action="store_true", help="validate the model and stop")
    parser.add_argument("--document", action="store_true", help="also render the A4 print variants in out/doc")
    args = parser.parse_args(argv)
    presentation, architecture = load_models()
    repos = evidence.repositories()
    errors = evidence.validate_repositories(repos) + validate(presentation, architecture, repos)
    if errors:
        print("SEQUENCE VALIDATION FAILED", file=sys.stderr)
        print("\n".join(f"- {e}" for e in errors), file=sys.stderr)
        return 1
    total = sum(len(messages(s["steps"])) for s in presentation["sequences"])
    if args.validate_only:
        print(f"SEQUENCE VALIDATION PASSED ({len(presentation['sequences'])} sequences, {total} messages)")
        return 0
    if shutil.which("java") is None:
        print("java is required to run PlantUML", file=sys.stderr)
        return 1
    ctx = Context(architecture)
    for svg in render_full(presentation, ctx):
        print(f"generated: {svg.relative_to(ROOT)}")
    GUIDE.write_text(guide(presentation, ctx, repos), encoding="utf-8")
    print(f"generated: {GUIDE.relative_to(ROOT)}")
    if args.document:
        for figure in render_documents():
            print(f"generated: out/doc/{figure['id']}.svg/.png ({figure['page']}, {figure['width_cm']:.1f}x"
                  f"{figure['height_cm']:.1f} cm, min {figure['min_pt']:.1f} pt)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
