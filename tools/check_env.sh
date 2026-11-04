#!/usr/bin/env bash
# Required generation dependencies only. Optional converters are opt-in.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
T=$(mktemp -d) || exit 1
trap 'rm -rf "$T"' EXIT
failures=0
chk(){
  if "$@" >"$T/check.log" 2>&1; then
    echo "  OK     $1"
  else
    echo "  FALLA  $1" >&2
    cat "$T/check.log" >&2
    failures=$((failures + 1))
  fi
}
resolve(){
  "${PYTHON:-.venv/bin/python}" -c 'import sys; sys.path.insert(0,"tools/generators"); from domain_model import find_tool; print(find_tool(sys.argv[1]))' "$1"
}
printf '@startuml\n!include <C4/C4_Container>\nPerson(u,"U")\nSystem(s,"S")\nRel(u,s,"Usa","HTTPS")\n@enduml\n' > "$T/t.puml"
echo 'a -> b: hola' > "$T/t.d2"
printf 'Table a {\n  id int [pk]\n}\n' > "$T/t.dbml"
cat > "$T/t.py" <<PYTHON
from diagrams import Diagram
from diagrams.azure.network import ApplicationGateway
with Diagram("smoke", filename="$T/smoke", outformat="svg", show=False):
    ApplicationGateway("ok")
PYTHON
chk dot -V
chk neato -V
chk java -version
chk java -Djava.awt.headless=true -jar tools/plantuml.jar -failfast2 -tsvg "$T/t.puml"
chk test -s "$T/t.svg"
chk "${PYTHON:-.venv/bin/python}" "$T/t.py"
chk test -s "$T/smoke.svg"
if d2_tool=$(resolve d2); then
  chk "$d2_tool" --layout=elk "$T/t.d2" "$T/t_d2.svg"
  chk test -s "$T/t_d2.svg"
else failures=$((failures + 1)); fi
if dbml_tool=$(resolve dbml2sql); then
  # Capture the producer status, even if it emits plausible SQL before failing.
  if "$dbml_tool" "$T/t.dbml" --postgres > "$T/t.sql"; then
    chk grep -qi 'create table' "$T/t.sql"
  else failures=$((failures + 1)); fi
else failures=$((failures + 1)); fi
if [[ "${CHECK_OPTIONAL_TOOLS:-0}" == 1 ]]; then
  chk dbml-renderer -i "$T/t.dbml" -o "$T/t_db.svg"
  chk test -s "$T/t_db.svg"
  chk pandoc --version
fi
if (( failures )); then
  echo "Environment checks failed: $failures" >&2
  exit 1
fi
