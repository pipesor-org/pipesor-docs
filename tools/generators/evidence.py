#!/usr/bin/env python3
"""Implementation evidence shared by the implementation overlay and the presentation models.

An evidence reference is ``<repository>:<path>:<line>`` or ``<repository>:<path>:<start>-<end>``.
The repository key and its pinned revision come from ``model/implementation_status.yml``. A
reference records where a modeled fact is realised in code or IaC. It does not create
architecture, approve a decision or prove runtime behaviour.

``python tools/generators/evidence.py --workspace <dir>`` checks every reference of every model
against local clones at the pinned revisions with ``git show``. It is optional because CI has no
sibling clones; the structural checks in ``validate`` always run.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
OVERLAY = ROOT / "model" / "implementation_status.yml"
REFERENCE = re.compile(r"^(?P<repo>[a-z][a-z0-9_]*):(?P<path>[^:\s]+):(?P<start>[1-9]\d*)(?:-(?P<end>[1-9]\d*))?$")
REVISION = re.compile(r"^[0-9a-f]{7,40}$")
# Implementation states of a modeled fact (architecture, domain or design).
STATUSES = ("implemented", "partial", "divergent", "not_implemented", "external")
STATUS_TEXT = {
    "implemented": "implementado",
    "partial": "implementado en parte",
    "divergent": "implementado de otra forma",
    "not_implemented": "modelado, no implementado",
    "external": "externo, no verificable en el código",
}


@dataclass(frozen=True)
class Reference:
    repo: str
    path: str
    start: int
    end: int

    @property
    def short(self):
        lines = f"{self.start}" if self.start == self.end else f"{self.start}-{self.end}"
        return f"{Path(self.path).name}:{lines}"

    def __str__(self):
        lines = f"{self.start}" if self.start == self.end else f"{self.start}-{self.end}"
        return f"{self.repo}:{self.path}:{lines}"


def load_overlay(path=OVERLAY):
    with Path(path).open(encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def repositories(overlay=None):
    overlay = load_overlay() if overlay is None else overlay
    return overlay.get("repositories") or {}


def parse(value):
    match = REFERENCE.fullmatch(value) if isinstance(value, str) else None
    if not match:
        raise ValueError(f"invalid evidence reference {value!r}; expected repo:path:line[-line]")
    start = int(match["start"])
    end = int(match["end"] or start)
    if end < start:
        raise ValueError(f"invalid evidence range {value!r}")
    return Reference(match["repo"], match["path"], start, end)


def validate_repositories(repos):
    errors = []
    if not isinstance(repos, dict) or not repos:
        return ["repositories: expected a non-empty mapping"]
    for key, entry in repos.items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", str(key)):
            errors.append(f"repositories.{key}: invalid key")
        if not isinstance(entry, dict) or not entry.get("path") or not REVISION.fullmatch(str(entry.get("revision", ""))):
            errors.append(f"repositories.{key}: expected path and a hexadecimal revision")
    return errors


def validate_refs(values, repos, where):
    """Structural check of a list of references against the declared repositories."""
    errors = []
    if not isinstance(values, list) or not values:
        return [f"{where}: evidence must be a non-empty list"]
    for value in values:
        try:
            ref = parse(value)
        except ValueError as error:
            errors.append(f"{where}: {error}")
            continue
        if ref.repo not in repos:
            errors.append(f"{where}: unknown repository {ref.repo!r} in {value!r}")
    return errors


def check_workspace(values, repos, workspace):
    """Verify that each referenced file exists at the pinned revision and has the cited lines."""
    errors, cache = [], {}
    for value in values:
        ref = parse(value)
        entry = repos[ref.repo]
        key = (ref.repo, ref.path)
        if key not in cache:
            clone = Path(workspace) / entry["path"]
            result = subprocess.run(["git", "-C", str(clone), "show", f"{entry['revision']}:{ref.path}"],
                                    capture_output=True, text=True)
            cache[key] = result.stdout.count("\n") + (0 if result.stdout.endswith("\n") else 1) if result.returncode == 0 else None
        lines = cache[key]
        if lines is None:
            errors.append(f"{value}: file not found at {ref.repo}@{entry['revision']}")
        elif ref.end > lines:
            errors.append(f"{value}: line {ref.end} beyond end of file ({lines} lines)")
    return errors


def collect(node, found=None):
    """Every evidence list under any key named 'evidence' in a loaded model."""
    found = [] if found is None else found
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "evidence" and isinstance(value, list):
                found.extend(v for v in value if isinstance(v, str))
            else:
                collect(value, found)
    elif isinstance(node, list):
        for value in node:
            collect(value, found)
    return found


MODELS_WITH_EVIDENCE = ("implementation_status.yml", "design.yml", "sequence_presentation.yml",
                        "deployment_presentation.yml")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workspace", required=True, help="directory that holds the sibling clones")
    args = parser.parse_args()
    repos = repositories()
    errors = validate_repositories(repos)
    refs = []
    for name in MODELS_WITH_EVIDENCE:
        path = ROOT / "model" / name
        if path.exists():
            refs.extend(collect(yaml.safe_load(path.read_text(encoding="utf-8"))))
    errors.extend(error for value in refs for error in validate_refs([value], repos, "evidence"))
    if not errors:
        errors.extend(check_workspace(sorted(set(refs)), repos, args.workspace))
    if errors:
        print("EVIDENCE CHECK FAILED")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print(f"EVIDENCE CHECK PASSED ({len(set(refs))} references)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
