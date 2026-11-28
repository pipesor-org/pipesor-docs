#!/usr/bin/env python3
"""Regenerate twice in disposable copies; never repair checked-in artifacts.

Freshness compares every tracked out/* and model/db.dbml byte for byte.
Repeatability additionally compares the entire build/ and out/ inventories.
Layout checks the document figures: out/figuras holds only PNG files and README.md, every
figure passes the print checks of tools/generators/figuras.py, and the retired out/doc is gone.
No timestamp/ID normalization hides changes. A failure leaves diagnostics in stdout.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def compare(left, right, paths):
    return [p for p in sorted(paths) if not (left / p).is_file()
            or not (right / p).is_file() or (left / p).read_bytes() != (right / p).read_bytes()]


def inventory(root):
    return {str(p.relative_to(root)) for folder in ('build', 'out')
            for p in (root / folder).rglob('*') if p.is_file()} | {'model/db.dbml'}


def layout(copy, tracked):
    """Document-figure layout problems in a regenerated copy and in the tracked tree."""
    sys.path.insert(0, str(copy / 'tools' / 'generators'))
    import figuras
    sys.path.pop(0)
    out = copy / 'out' / 'figuras'
    problems = [f'out/figuras holds {p.relative_to(copy)}' for p in out.rglob('*')
                if p.is_file() and p.suffix != '.png' and p.name != 'README.md']
    problems += figuras.check_outputs(figuras.models()['figures'], out, copy / 'build' / 'figuras')
    problems += [f'retired path still tracked: {p}' for p in sorted(tracked) if p.startswith('out/doc/')]
    return problems


def main():
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    artifacts = {p for p in tracked if p.startswith('out/') or p == 'model/db.dbml'}
    with tempfile.TemporaryDirectory(prefix='pipesor-reproduce-') as directory:
        copies = [Path(directory) / name for name in ('first', 'second')]
        for copy in copies:
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '.venv', 'node_modules', '__pycache__', 'build', 'out'))
            # All generators must create fresh outputs, not reuse tracked files.
            (copy / 'out').mkdir()
            result = subprocess.run(['make', 'all', f'PYTHON={sys.executable}'], cwd=copy)
            if result.returncode:
                return result.returncode
        stale = compare(ROOT, copies[0], artifacts)
        drift = compare(*copies, inventory(copies[0]) | inventory(copies[1]))
        misplaced = layout(copies[0], tracked)
        for label, paths in [('STALE', stale), ('NONREPRODUCIBLE', drift), ('LAYOUT', misplaced)]:
            for path in paths:
                print(f'{label}: {path}')
        if stale or drift or misplaced:
            return 1
        print(f'Artifacts current: {len(artifacts)}; repeatable outputs: {len(inventory(copies[0]))}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
