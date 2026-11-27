#!/usr/bin/env python3
"""Validate class design against the unchanged architecture and domain SSOTs.

Two kinds of class coexist in model/design.yml:

* ``status: proposed`` classes of recommendation_service (CD-1..CD-3). They keep every
  proposal rule (layers, packages, CQRS, persistence, prohibited capabilities) and record in
  ``implementation`` how far the code realizes them.
* ``status: implemented`` classes transcribed from a service's code for the bounded-context
  diagrams (CD-4 onward). Their ``implementation`` block cites the code with
  ``repo:path:line`` references from model/implementation_status.yml; they are not proposals
  and are not checked against the proposal's layering rules.

``--workspace <dir>`` additionally verifies, against the sibling clones at their pinned
revisions, that the first reference of every implemented class declares that class.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

import yaml

from domain_validation import validate_domain

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "generators"))
import evidence  # noqa: E402

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PACKAGE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
CODE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?$")
STEREOTYPES = {
    "Controller", "CommandService", "QueryService", "Aggregate", "Entity",
    "ValueObject", "DomainService", "Port", "Adapter", "Translator",
    "Repository", "Command", "Query", "Enum", "External",
}
# Code-derived classes add application records and persistence models (JPA/SQLAlchemy rows).
IMPLEMENTED_STEREOTYPES = STEREOTYPES - {"External"} | {"Record", "PersistenceModel"}
# Data holders of implemented classes must state how they persist (or that they do not).
DATA_STEREOTYPES = {"Aggregate", "Entity", "ValueObject", "Record", "Command", "Query", "PersistenceModel"}
STORAGE_FORMS = {"mapped", "json_column", "flattened", "not_persisted"}
DESIGN_STATUSES = ("proposed", "implemented")
CODE_STATUSES = {"implemented", "partial", "divergent"}
RELATIONS = {"dispatches", "implements", "uses", "injects", "calls_http",
             "translates", "persists"}
# realizes: implemented code -> the proposed class it (partly) realizes. Only in bounded-context diagrams.
CODE_RELATIONS = RELATIONS - {"dispatches", "calls_http"} | {"realizes"}
DEPENDENCIES = {
    "interfaces": {"interfaces", "application"},
    "application": {"application", "domain"},
    "domain": {"domain"},
    "infrastructure": {"infrastructure", "application", "domain", "external"},
    "external": set(),
}
# Layer of an implemented class: the first package segment naming one; "unlayered" otherwise.
CODE_LAYERS = ("interfaces", "application", "domain", "infrastructure")
PACKAGES = {
    "interfaces": {"interfaces.rest"},
    "application": {"application.internal.commandservices",
                    "application.internal.queryservices",
                    "application.internal.outboundservices"},
    "domain": {"domain.model.aggregates", "domain.model.entities",
               "domain.model.valueobjects", "domain.model.commands",
               "domain.model.queries", "domain.model.events", "domain.services",
               "domain.exceptions"},
    "infrastructure": {"infrastructure.persistence.jpa", "infrastructure.clients",
                       "infrastructure.acl"},
}
ZOOMS = {"CD-1": "diagnostic_api_component",
         "CD-2": "diagnostic_orchestrator_component",
         "CD-3": "human_review_component"}
DIAGRAM_ID = re.compile(r"^CD-([1-9][0-9]*)$")
OPEN_QUESTIONS = {
    "DQ-002": "model/domain.yml#open_questions",
    "DCQ-001": "model/architecture.yml#human_review_component",
    "DCQ-002": "model/architecture.yml#rel_correlation_diagnostic_api",
    "DCQ-003": "model/architecture.yml#recommendation_service.diagnostic_output",
}
PERSISTED = {"Diagnosis": ("Aggregate", "diagnosis.diagnoses"),
             "Recommendation": ("Entity", "diagnosis.recommendations"),
             "HumanReview": ("Aggregate", "diagnosis.human_reviews")}
PRIMITIVES = {"UUID", "Instant", "String", "Object", "int", "long", "boolean",
              "void", "List", "Map", "Optional"}
JAVA_TYPES = {"uuid": "UUID", "uuid[]": "List<UUID>", "text": "String",
              "integer": "int", "bigint": "long", "boolean": "boolean",
              "timestamptz": "Instant", "jsonb": "Object"}
# Types code may legitimately use for a column (implemented classes only; proposals keep JAVA_TYPES).
CODE_TYPES = {
    "Java": {"uuid": {"UUID"}, "uuid[]": {"List<UUID>", "UUID[]"}, "text": {"String"},
             "integer": {"int", "Integer"}, "bigint": {"long", "Long"}, "boolean": {"boolean", "Boolean"},
             "timestamptz": {"Instant", "OffsetDateTime"}, "jsonb": {"Object", "String"},
             "bytea": {"byte[]"}, "varchar": {"String"}},
    "Python": {"uuid": {"UUID"}, "uuid[]": {"list[UUID]"}, "text": {"str"}, "integer": {"int"},
               "bigint": {"int"}, "boolean": {"bool"}, "timestamptz": {"datetime"}, "jsonb": {"dict"},
               "bytea": {"bytes"}, "varchar": {"str"}, "vector(1536)": {"list[float]"}},
}
LANGUAGES = {
    # Evidence path of a class, attribute naming and the type syntax of each backend language.
    "Java": {"path": lambda package, outer: f"src/main/java/{package.replace('.', '/')}/{outer}.java",
             "attribute": re.compile(r"^[a-z][A-Za-z0-9]*$"),
             "foreign_type": re.compile(r"\||\bNone\b|\b(?:list|dict|tuple|frozenset)\["),
             "declaration": r"\b(?:class|record|interface|enum)\s+{name}\b"},
    "Python": {"path": lambda package, outer: f"src/{package.replace('.', '/')}.py",
               "attribute": re.compile(r"^[a-z_][a-z0-9_]*$"),
               "foreign_type": re.compile(r"[<>]|\b(?:String|Instant|boolean)\b"),
               "declaration": r"^\s*class\s+{name}\b"},
}
MINIMAL_RESULTS = {"void", "UUID", "String", "boolean", "int", "long"}
FORBIDDEN = re.compile(
    r"rootcause|eventsourc|eventstore|readdatabase|writedatabase|"
    r"auditservice|auditmicroservice|artifactpublisher|autonomousremediat|"
    r"autoremediat|applyfix|executefix|rollback|deploy", re.I)
FRAMEWORKS = re.compile(r"spring|jpa|hibernate|http|azure|fastapi|github|"
                        r"jackson|jsonnode|org\.|com\.azure", re.I)
UNSAFE_CONTENT = re.compile(r"rawlog|rawevidence|secret|credential|token|"
                            r"sensitivepayload", re.I)
RECOMMENDATION_RULES = {
    "language": "Java", "framework": "Spring Boot", "repository": "recommendation",
    "cqrs": "logical", "persistence": "postgresql_operational_store",
    "event_sourcing": False, "separate_read_write_databases": False,
    "autonomous_remediation": False, "github_access": "read_only",
    "artifact_publisher": "github_actions",
    "navigation_views": ["c4_context", "c4_container_processing", "c4_component_diagnostic"],
}


def camel_case(value):
    first, *rest = value.split("_")
    return first + "".join(part[:1].upper() + part[1:] for part in rest)


def normalized(value):
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


def code_layer(package):
    return next((part for part in package.split(".") if part in CODE_LAYERS), "unlayered")


def column_type(column):
    return "varchar" if column["type"].startswith("varchar(") else column["type"]


def load_models(paths):
    """Missing domain is a fatal precondition, including for direct invocation."""
    return tuple(yaml.safe_load(Path(path).read_text(encoding="utf-8"))
                 for path in paths)


def class_container(item, elements):
    """Container a class belongs to: declared for implemented code, derived for proposals."""
    if item.get("status") == "implemented":
        return item.get("container")
    element = elements.get(item.get("component_realized"), {})
    return element.get("parent") if element.get("kind") == "component" else item.get("component_realized")


def _validate(design, architecture, domain, root, repos):
    errors = []
    if not isinstance(design, dict):
        return ["design.yml must contain a mapping"]
    domain_errors = validate_domain(domain, architecture)
    if domain_errors:
        return [f"domain precondition: {error}" for error in domain_errors]
    for field in ("model_version", "class_diagrams", "classes", "relationships",
                  "design_rules", "assumptions", "open_questions"):
        if field not in design:
            errors.append(f"design: missing {field}")
    for field in ("class_diagrams", "classes", "relationships", "assumptions",
                  "open_questions"):
        if not isinstance(design.get(field), list):
            errors.append(f"design.{field} must be a list")
        elif any(not isinstance(item, dict) for item in design[field]):
            errors.append(f"design.{field} must contain mappings")
    errors.extend(evidence.validate_repositories(repos))
    if errors:
        return errors
    questions = design["open_questions"]
    ids = [q.get("id") for q in questions]
    if len(ids) != len(set(ids)):
        errors.append("design.open_questions: duplicate IDs")
    for ident, source in OPEN_QUESTIONS.items():
        matches = [q for q in questions if q.get("id") == ident]
        if not matches:
            errors.append(f"design.open_questions: missing {ident}")
        elif any(q.get("source") != source or q.get("status", "open_question") != "open_question"
                 or not isinstance(q.get("description"), str)
                 or not q["description"].strip() for q in matches):
            errors.append(f"design.open_questions: {ident} requires its source, open status and description")
    if not isinstance(design["model_version"], str) or not design["model_version"].strip():
        errors.append("model_version must be a nonempty string")

    elements = {item["id"]: item for item in architecture["elements"]}
    views = {item["id"]: item for item in architecture["views"]}
    arch_relations = {item["id"]: item for item in architecture["relationships"]}
    tables = {f"{item['schema']}.{item['table']}": item for item in domain["entities"]}
    enums = {item["id"]: item for item in domain["enums"]}

    # Rules: common limits plus one entry per container whose classes the design describes.
    rules = design["design_rules"]
    if not isinstance(rules, dict):
        return errors + ["design_rules must be a mapping"]
    if rules.get("max_nodes_per_diagram") != 15 or type(rules.get("max_nodes_per_diagram")) is not int:
        errors.append("design_rules.max_nodes_per_diagram: expected 15")
    containers = rules.get("containers")
    if not isinstance(containers, dict) or not containers:
        return errors + ["design_rules.containers must map each described container to its rules"]
    for cid, crules in containers.items():
        where = f"design_rules.containers.{cid}"
        element = elements.get(cid)
        if not isinstance(crules, dict):
            errors.append(f"{where}: rules must be a mapping")
            continue
        if not element or element.get("kind") != "container":
            errors.append(f"{where}: not a container of architecture.yml")
            continue
        backend = element.get("backend")
        if not isinstance(backend, dict) or not backend.get("language") or not backend.get("framework"):
            errors.append(f"{where}: architecture.yml declares no backend language/framework for this container")
        if not crules.get("language") or not crules.get("framework"):
            errors.append(f"{where}: language and framework are required")
        elif crules["language"] not in LANGUAGES:
            errors.append(f"{where}: unsupported language {crules['language']!r}")
        elif isinstance(backend, dict) and (crules["language"], crules["framework"]) != (
                backend.get("language"), backend.get("framework")):
            errors.append(f"{where}: {crules['language']} / {crules['framework']} must match architecture.yml backend")
        if crules.get("repository") not in repos:
            errors.append(f"{where}: repository must be a key of implementation_status.yml repositories")
        store = crules.get("persistence")
        if store != "none" and elements.get(store, {}).get("kind") != "datastore":
            errors.append(f"{where}: persistence must be an architecture datastore or 'none'")
        base = crules.get("base_package")
        if base is not None and (not isinstance(base, str) or not re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*", base)):
            errors.append(f"{where}: base_package must be a dotted package")
        nav = crules.get("navigation_views")
        if not isinstance(nav, list) or len(nav) < 2:
            errors.append(f"{where}: navigation_views must list the C4 zoom path")
            continue
        for index, vid in enumerate(nav):
            if vid not in views:
                errors.append(f"{where}: unknown architecture view {vid}")
            elif index and views[vid].get("zoom_from") != nav[index - 1]:
                errors.append(f"{where}: navigation {vid} must zoom from {nav[index - 1]}")
    recommendation = containers.get("recommendation_service", {})
    for key, expected in RECOMMENDATION_RULES.items():
        if recommendation.get(key) != expected or type(recommendation.get(key)) is not type(expected):
            errors.append(f"design_rules.containers.recommendation_service.{key}: expected {expected!r}")
    rec_nav = RECOMMENDATION_RULES["navigation_views"]
    if views.get(rec_nav[-1], {}).get("zoom_target") != "recommendation_service":
        errors.append("navigation: component view must target recommendation_service")
    if errors:
        return errors

    classes = {}
    for item in design["classes"]:
        cid = item.get("id")
        if not isinstance(cid, str) or not IDENTIFIER.fullmatch(cid) or cid in classes:
            errors.append(f"invalid/duplicate class id: {cid!r}")
            continue
        classes[cid] = item
    names = [(class_container(item, elements), item.get("name")) for item in classes.values()]
    if len(set(names)) != len(names):
        errors.append("class names must be unique within each container")
    for cid, item in classes.items():
        required = ("name", "package", "layer", "stereotype", "status", "attributes", "methods", "implementation")
        required += ("container",) if item.get("status") == "implemented" else ("component_realized",)
        for field in required:
            if field not in item:
                errors.append(f"{cid}: missing {field}")
    if errors:
        return errors
    proposed = {cid for cid, item in classes.items() if item["status"] == "proposed"}

    def owner(component):
        element = elements.get(component, {})
        return element.get("parent") if element.get("kind") == "component" else component

    def dependency(source, target, location):
        if target.get("layer") not in DEPENDENCIES.get(source.get("layer"), set()):
            errors.append(f"{location}: forbidden layer dependency "
                          f"{source.get('layer')} -> {target.get('layer')}")

    def check_types(item, type_name, location):
        if not isinstance(type_name, str) or not type_name.strip():
            errors.append(f"{location}: nonempty type required")
            return
        if item["status"] == "implemented":
            language = containers.get(item["container"], {}).get("language")
            if language in LANGUAGES and LANGUAGES[language]["foreign_type"].search(type_name):
                errors.append(f"{location}: type syntax does not match container language {language}")
            return
        if item["layer"] == "domain" and FRAMEWORKS.search(type_name):
            errors.append(f"{location}: domain cannot import frameworks/provider types")
        for word in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", type_name):
            if word in classes and word in proposed:
                dependency(item, classes[word], location)
            elif word not in PRIMITIVES and word not in enums:
                errors.append(f"{location}: unknown type {word}")

    def protocol(reference, component, direction, location, target=None):
        canonical = arch_relations.get(reference.get("architecture_relationship"))
        if not canonical:
            errors.append(f"{location}: existing architecture_relationship required")
            return
        if reference.get("protocol") != canonical["protocol"]:
            errors.append(f"{location}: protocol must match architecture.yml ({canonical['protocol']})")
        endpoint = "to" if direction == "in" else "from"
        if canonical[endpoint] not in {component, owner(component)}:
            errors.append(f"{location}: architecture relationship endpoint differs from realized component")
        if target and canonical["to"] not in {target, owner(target)}:
            errors.append(f"{location}: architecture relationship target differs")

    def refs(values, where):
        found = evidence.validate_refs(values, repos, where)
        errors.extend(found)
        return [] if found else [evidence.parse(value) for value in values]

    def check_implementation(cid, item):
        block = item["implementation"]
        where = f"{cid}.implementation"
        if not isinstance(block, dict):
            errors.append(f"{where}: must be a mapping")
            return []
        status = block.get("status")
        if status not in evidence.STATUSES:
            errors.append(f"{where}: status must be one of {', '.join(evidence.STATUSES)}")
            return []
        if item["status"] == "implemented" and status not in CODE_STATUSES:
            errors.append(f"{where}: a class transcribed from code must be implemented, partial or divergent")
        if status == "external" and item["stereotype"] != "External":
            errors.append(f"{where}: external status is reserved for External proxies")
        note = block.get("note")
        if note is not None and (not isinstance(note, str) or not note.strip()):
            errors.append(f"{where}: note must be nonempty text")
        if status in {"partial", "divergent"} and not note:
            errors.append(f"{where}: {status} requires a note explaining the difference")
        if status == "not_implemented":
            if not isinstance(block.get("reason"), str) or not block["reason"].strip():
                errors.append(f"{where}: not_implemented requires a reason")
            return refs(block["evidence"], where) if "evidence" in block else []
        if "reason" in block:
            errors.append(f"{where}: reason is only for not_implemented")
        found = refs(block.get("evidence"), where)
        container = class_container(item, elements)
        expected = containers.get(container, {}).get("repository")
        if found and status != "external" and expected and found[0].repo != expected:
            errors.append(f"{where}: first evidence must cite the {container} repository ({expected})")
        return found

    def check_proposed_class(cid, item):
        layer, package = item.get("layer"), item.get("package", "")
        stereotype, component = item.get("stereotype"), item.get("component_realized")
        attributes = item["attributes"]
        if layer not in DEPENDENCIES:
            errors.append(f"{cid}: invalid layer {layer!r}")
        if not isinstance(package, str) or not PACKAGE.fullmatch(package):
            errors.append(f"{cid}: package is required and must be a Java-style namespace")
        elif layer != "external" and package not in PACKAGES.get(layer, set()):
            errors.append(f"{cid}: package {package!r} does not match layer/convention")
        if stereotype not in STEREOTYPES:
            errors.append(f"{cid}: invalid/missing stereotype {stereotype!r}")
        if stereotype != "External" and item.get("name") != cid:
            errors.append(f"{cid}: Java class name must match its identifier")
        if item.get("kind", "class") not in {"class", "interface", "enum"}:
            errors.append(f"{cid}: unsupported class kind")
        if component not in elements:
            errors.append(f"{cid}: component_realized must exist in architecture.yml")
        elif stereotype == "External":
            if layer != "external" or not package.startswith("external.") or item["attributes"] or item["methods"]:
                errors.append(f"{cid}: external proxy must have no internals")
            if component not in {"rag_retrieval", "pretrained_llm_diagnostic_service"}:
                errors.append(f"{cid}: undeclared external proxy")
        elif elements[component].get("kind") != "component" or owner(component) != "recommendation_service":
            errors.append(f"{cid}: internal classes must realize components of recommendation_service")
        if layer == "external" and stereotype != "External":
            errors.append(f"{cid}: external layer is only for graphical proxies")
        if stereotype in {"Port", "Repository"} and item.get("kind") != "interface":
            errors.append(f"{cid}: ports/repositories must be interfaces")
        if stereotype == "Enum" and item.get("kind") != "enum":
            errors.append(f"{cid}: Enum requires kind enum")
        if stereotype in {"Aggregate", "Entity", "DomainService", "Command", "Query", "Enum"} and layer != "domain":
            errors.append(f"{cid}: domain stereotype must live in domain")
        if stereotype in {"CommandService", "QueryService"} and layer != "application":
            errors.append(f"{cid}: application service must live in application")
        if stereotype == "Controller" and layer != "interfaces":
            errors.append(f"{cid}: controller must live in interfaces")
        if stereotype in {"Adapter", "Translator"} and layer != "infrastructure":
            errors.append(f"{cid}: adapters/translators must live in infrastructure")
        if cid.startswith("Jpa") and package != "infrastructure.persistence.jpa":
            errors.append(f"{cid}: JPA implementations must live in infrastructure.persistence.jpa")
        if "storage" in item:
            errors.append(f"{cid}: storage is for implemented classes; proposals use persisted_as")
        operational = {key: item.get(key) for key in
                       ("id", "name", "package", "attributes", "methods", "imports",
                        "values", "persisted_as", "persistence")}
        content = normalized(operational)
        if FORBIDDEN.search(content):
            errors.append(f"{cid}: prohibited design capability/name")
        if "github" in content and re.search(r"write|publish|upload|modify|push|delete|update|create", content):
            errors.append(f"{cid}: GitHub write adapter/operation prohibited")
        if layer == "domain" and FRAMEWORKS.search(" ".join(item.get("imports", []))):
            errors.append(f"{cid}: domain cannot import external frameworks")
        for imported in item.get("imports", []):
            imported_layer = imported.split(".")[0]
            if imported_layer in DEPENDENCIES:
                dependency(item, {"layer": imported_layer}, f"{cid}/import {imported}")
            elif layer == "domain" and not imported.startswith(("java.lang.", "java.util.", "java.time.")):
                errors.append(f"{cid}: domain cannot import external dependency {imported}")
        if layer != "external" and UNSAFE_CONTENT.search(content):
            errors.append(f"{cid}: raw/sensitive content prohibited in diagnostic design")
        if item.get("ingress"):
            protocol(item["ingress"], component, "in", f"{cid}/ingress")
        if item.get("persistence"):
            persistence = item["persistence"]
            protocol(persistence, component, "out", f"{cid}/persistence", persistence.get("store"))
            if layer != "infrastructure" or persistence.get("store") != recommendation["persistence"]:
                errors.append(f"{cid}: persistence must use common PostgreSQL in infrastructure")
            if not persistence.get("tables"):
                errors.append(f"{cid}: persistence.tables required")
            for table_name in persistence.get("tables", []):
                if table_name not in tables:
                    errors.append(f"{cid}: persistence target {table_name} absent from domain.yml")
                elif tables[table_name]["owner_container"] != "recommendation_service" and not (
                        cid == "PostgresAuditTrailAdapter" and table_name == "audit.audit_events"):
                    errors.append(f"{cid}: forbidden cross-context persistence")

    def check_code_class(cid, item, found):
        container = item["container"]
        crules = containers.get(container)
        if not crules:
            errors.append(f"{cid}: container {container!r} has no design_rules.containers entry")
            return
        language = LANGUAGES[crules["language"]]
        package, name, stereotype = item.get("package"), item.get("name"), item.get("stereotype")
        if not isinstance(package, str) or not PACKAGE.fullmatch(package):
            errors.append(f"{cid}: package must be the code's dotted package/module")
            return
        if crules.get("base_package") and not package.startswith(crules["base_package"] + "."):
            errors.append(f"{cid}: package outside the container base_package {crules['base_package']}")
        if not isinstance(name, str) or not CODE_NAME.fullmatch(name):
            errors.append(f"{cid}: name must be the code type name (Type or Outer.Type)")
            return
        if found and found[0].path != language["path"](package, name.split(".")[0]):
            errors.append(f"{cid}: first evidence path does not match package {package} and type {name}")
        if item.get("layer") != code_layer(package):
            errors.append(f"{cid}: layer must be {code_layer(package)!r}, derived from the package")
        if stereotype not in IMPLEMENTED_STEREOTYPES:
            errors.append(f"{cid}: invalid stereotype {stereotype!r} for implemented code")
        kind = item.get("kind", "class")
        if kind not in {"class", "interface", "enum"}:
            errors.append(f"{cid}: unsupported class kind")
        if stereotype == "Port" and kind != "interface":
            errors.append(f"{cid}: ports must be interfaces")
        if (stereotype == "Enum") != (kind == "enum"):
            errors.append(f"{cid}: Enum stereotype and kind enum go together")
        if kind == "enum":
            values = item.get("values")
            if not isinstance(values, list) or not values or any(not isinstance(v, str) for v in values):
                errors.append(f"{cid}: enum values required")
            elif item.get("domain_enum"):
                domain_enum = enums.get(item["domain_enum"])
                if not domain_enum or (item.get("wire_values") or values) != domain_enum["values"]:
                    errors.append(f"{cid}: values must equal domain.yml enum {item['domain_enum']}")
        for attribute in item["attributes"]:
            if not language["attribute"].fullmatch(str(attribute.get("name", ""))):
                errors.append(f"{cid}.{attribute.get('name')}: attribute naming does not follow {crules['language']}")
        for key in ("ingress", "component_realized"):
            if key in item:
                errors.append(f"{cid}: {key} belongs to proposals, not to implemented code")
        if stereotype in DATA_STEREOTYPES and ("persisted_as" in item) == ("storage" in item):
            errors.append(f"{cid}: declare exactly one of persisted_as or storage (form not_persisted if none)")
        if stereotype == "PersistenceModel" and "persisted_as" not in item:
            errors.append(f"{cid}: a persistence model must declare persisted_as")
        if "storage" in item:
            check_storage(cid, item, container)
        if item.get("persistence"):
            persistence = item["persistence"]
            protocol(persistence, container, "out", f"{cid}/persistence", persistence.get("store"))
            if persistence.get("store") != crules.get("persistence"):
                errors.append(f"{cid}: persistence store must be the container's {crules.get('persistence')}")
            if not persistence.get("tables"):
                errors.append(f"{cid}: persistence.tables required")
            for table_name in persistence.get("tables", []):
                if tables.get(table_name, {}).get("owner_container") != container:
                    errors.append(f"{cid}: persistence target {table_name} is not a {container} table")

    def check_storage(cid, item, container):
        storage = item["storage"]
        where = f"{cid}.storage"
        if not isinstance(storage, dict) or storage.get("form") not in STORAGE_FORMS:
            errors.append(f"{where}: form must be one of {', '.join(sorted(STORAGE_FORMS))}")
            return
        listed = storage.get("tables", [])
        if storage["form"] == "not_persisted":
            if listed or storage.get("columns") or storage.get("via"):
                errors.append(f"{where}: not_persisted lists no tables, columns or adapter")
            if not isinstance(storage.get("note"), str) or not storage["note"].strip():
                errors.append(f"{where}: not_persisted requires a note")
            return
        if not isinstance(listed, list) or not listed:
            errors.append(f"{where}: {storage['form']} requires the domain.yml tables")
            return
        known = set()
        for table_name in listed:
            table = tables.get(table_name)
            if not table:
                errors.append(f"{where}: table {table_name} absent from domain.yml")
            elif table["owner_container"] != container:
                errors.append(f"{where}: table {table_name} belongs to {table['owner_container']}, not {container}")
            else:
                known.update(a["name"] for a in table["attributes"])
        for column in storage.get("columns", []):
            if column not in known:
                errors.append(f"{where}: column {column} absent from the listed tables")
        if storage["form"] in {"json_column", "flattened"} and not storage.get("columns"):
            errors.append(f"{where}: {storage['form']} requires the columns it uses")
        via = storage.get("via")
        if via is not None and not set(listed) <= set(classes.get(via, {}).get("persistence", {}).get("tables", [])):
            errors.append(f"{where}: via must be an adapter whose persistence covers the tables")
        if "evidence" in storage:
            refs(storage["evidence"], where)

    def check_persisted_as(cid, item):
        attributes = item["attributes"]
        table = tables.get(item["persisted_as"])
        if not table:
            errors.append(f"{cid}: persisted_as must exist in domain.yml")
            return
        expected = {a["name"]: a for a in table["attributes"]}
        actual = {a.get("domain_attribute") for a in attributes}
        if actual != set(expected) or len(attributes) != len(expected):
            errors.append(f"{cid}: persisted attributes must exactly match domain.yml")
        implemented = item["status"] == "implemented"
        language = containers.get(item.get("container"), {}).get("language", "Java")
        for attr in attributes:
            column = expected.get(attr.get("domain_attribute"))
            if not column:
                errors.append(f"{cid}: persisted attribute absent from domain.yml: {attr.get('name')}")
                continue
            if implemented:
                allowed = set(CODE_TYPES[language].get(column_type(column), set()))
                if column.get("enum"):
                    allowed |= {column["enum"], "String" if language == "Java" else "str"}
                base = re.sub(r"\s*\|\s*None$", "", str(attr.get("type", "")))
                named = attr["name"] == column["name"] if language == "Python" else True
                optional_syntax = language != "Python" or (base != attr.get("type")) == column["nullable"]
                if (base not in allowed or not named or not optional_syntax
                        or attr.get("nullable") != column["nullable"]):
                    errors.append(f"{cid}.{attr['name']}: mapping/type/nullability differs from domain.yml")
                continue
            java_type = column.get("enum") or JAVA_TYPES.get(column["type"])
            if cid == "Diagnosis" and column["name"] == "probable_cause":
                java_type = "ProbableCause"
            if (attr["name"] != camel_case(column["name"])
                    or attr["type"] != java_type or attr.get("nullable") != column["nullable"]):
                errors.append(f"{cid}.{attr['name']}: mapping/type/nullability differs from domain.yml")
        owner_container = item["container"] if implemented else "recommendation_service"
        if table["owner_container"] != owner_container:
            errors.append(f"{cid}: aggregate/entity cannot own another context's table")

    references = {}
    for cid, item in classes.items():
        references[cid] = check_implementation(cid, item)
        attributes, methods = item.get("attributes"), item.get("methods")
        if not isinstance(attributes, list) or not isinstance(methods, list):
            errors.append(f"{cid}: attributes/methods must be lists")
            continue
        if item["status"] not in DESIGN_STATUSES:
            errors.append(f"{cid}: design status must be proposed or implemented (not inferred)")
            continue
        if len({a.get("name") for a in attributes}) != len(attributes):
            errors.append(f"{cid}: duplicate attributes")
        if item["status"] == "implemented":
            check_code_class(cid, item, references[cid])
        else:
            check_proposed_class(cid, item)
        for attribute in attributes:
            location = f"{cid}.{attribute.get('name')}"
            if not IDENTIFIER.fullmatch(attribute.get("name", "")):
                errors.append(f"{location}: invalid attribute name")
            check_types(item, attribute.get("type"), location)
        for method in methods:
            location = f"{cid}.{method.get('name')}"
            if not IDENTIFIER.fullmatch(method.get("name", "")):
                errors.append(f"{location}: invalid method name")
            check_types(item, method.get("returns"), location)
            if item["status"] == "proposed" or "effect" in method:
                if method.get("effect") not in {"read", "write", "pure"}:
                    errors.append(f"{location}: explicit read/write/pure effect required")
            for param in method.get("parameters", []):
                check_types(item, param.get("type"), f"{location}/{param.get('name')}")
            if item["stereotype"] == "QueryService" and method.get("effect") == "write":
                errors.append(f"{location}: query service cannot modify state")
            if (item["status"] == "proposed" and item["stereotype"] == "CommandService"
                    and method.get("returns") not in MINIMAL_RESULTS):
                errors.append(f"{location}: command service must return void/minimal result")
        if "persisted_as" in item:
            check_persisted_as(cid, item)

    for cid, (stereotype, table_name) in PERSISTED.items():
        item = classes.get(cid, {})
        if (item.get("stereotype"), item.get("persisted_as")) != (stereotype, table_name):
            errors.append(f"{cid}: required {stereotype} persisted_as {table_name}")
    decision = classes.get("HumanReviewDecision", {})
    if (decision.get("stereotype") != "Enum"
            or decision.get("values") != enums["HumanReviewDecision"]["values"]):
        errors.append("HumanReviewDecision must be CONFIRMED|CORRECTED|REJECTED; PENDING is derived")
    view = classes.get("DiagnosticView", {})
    expected_view = elements["recommendation_service"]["diagnostic_output"]["includes"]
    if (view.get("role") != "read_model" or view.get("stereotype") != "ValueObject"
            or "persisted_as" in view
            or [a["name"] for a in view.get("attributes", [])] != [camel_case(a) for a in expected_view]):
        errors.append("DiagnosticView must be the nonpersisted application read model of diagnostic_output")
    context = classes.get("SanitizedDiagnosticContext", {})
    contract = elements["pretrained_llm_diagnostic_service"]["input_contract"]
    if ([a.get("contract_field") for a in context.get("attributes", [])] != contract
            or [a.get("name") for a in context.get("attributes", [])] != [camel_case(a) for a in contract]):
        errors.append("SanitizedDiagnosticContext must exactly represent the architecture LLM input_contract")
    gateway = classes.get("DiagnosticLlmGateway", {})
    if not gateway.get("methods") or any(
            [p.get("type") for p in m.get("parameters", [])] != ["SanitizedDiagnosticContext"]
            for m in gateway.get("methods", [])):
        errors.append("DiagnosticLlmGateway must accept only SanitizedDiagnosticContext")

    errors.extend(check_diagrams(design, classes, elements, views, containers, architecture))
    if errors:
        return errors
    check_code_relationship = _code_relationship_checker(classes, containers, references, errors)

    seen = set()
    for rel in design["relationships"]:
        src, dst, kind = rel.get("from"), rel.get("to"), rel.get("type")
        location = f"{src} -> {dst} ({kind})"
        if (src, dst, kind) in seen:
            errors.append(f"{location}: duplicate relationship")
        seen.add((src, dst, kind))
        if src not in classes or dst not in classes or kind not in RELATIONS | CODE_RELATIONS:
            errors.append(f"{location}: unknown endpoint/type")
            continue
        source, target = classes[src], classes[dst]
        if source["status"] == "implemented" or target["status"] == "implemented":
            check_code_relationship(rel, source, target, location)
            continue
        if kind not in RELATIONS:
            errors.append(f"{location}: {kind} links implemented code to a proposal")
            continue
        dependency(source, target, location)
        cross_context = owner(source["component_realized"]) != owner(target["component_realized"])
        if kind == "calls_http" or cross_context:
            protocol(rel, source["component_realized"], "out", location, target["component_realized"])
            if source["layer"] != "infrastructure" or target["stereotype"] != "External":
                errors.append(f"{location}: external HTTP calls belong to infrastructure adapters")
        if kind == "implements" and target.get("kind") != "interface":
            errors.append(f"{location}: implements target must be an interface")
        if kind == "persists" and (source["layer"] != "infrastructure"
                or target.get("persisted_as") not in source.get("persistence", {}).get("tables", [])):
            errors.append(f"{location}: persists must target a declared domain table from infrastructure")
        if kind == "dispatches" and (source["stereotype"] != "Controller"
                or target["stereotype"] not in {"CommandService", "QueryService"}):
            errors.append(f"{location}: controllers must dispatch to application services")
        method_map = {m["name"]: m for m in target["methods"]}
        for name in rel.get("methods", []):
            if name not in method_map:
                errors.append(f"{location}: unknown called method {name}")
        if source["stereotype"] == "QueryService" and kind != "implements":
            if target["stereotype"] in {"CommandService", "Port", "Adapter"} or kind == "persists":
                errors.append(f"{location}: query dependency may modify state")
            if target["stereotype"] == "Repository":
                if not rel.get("methods") or any(method_map.get(m, {}).get("effect") != "read"
                                                 for m in rel.get("methods", [])):
                    errors.append(f"{location}: query must select only read repository methods")
            elif any(method.get("effect") == "write" for name, method in method_map.items()
                     if not rel.get("methods") or name in rel["methods"]):
                errors.append(f"{location}: query cannot invoke mutating methods")
    for cid, item in classes.items():
        if item.get("kind") == "interface" and not any(
                r.get("type") == "implements" and r.get("to") == cid for r in design["relationships"]):
            errors.append(f"{cid}: interface has no proposed implementation")
    return errors


def _code_relationship_checker(classes, containers, references, errors):
    def check(rel, source, target, location):
        kind = rel["type"]
        if kind not in CODE_RELATIONS:
            errors.append(f"{location}: {kind} is not a code relationship")
            return
        if kind == "realizes":
            impl = target.get("implementation", {})
            if source["status"] != "implemented" or target["status"] != "proposed":
                errors.append(f"{location}: realizes goes from implemented code to a proposed class")
            elif impl.get("status") not in CODE_STATUSES:
                errors.append(f"{location}: realizes requires an implemented, partial or divergent proposal")
            elif not rel.get("label"):
                errors.append(f"{location}: realizes requires a label")
            else:
                cited = {(r.repo, r.path) for r in references.get(target["id"], [])}
                own = references.get(source["id"], [])
                if not own or (own[0].repo, own[0].path) not in cited:
                    errors.append(f"{location}: the proposal's evidence must cite the realizing code")
            return
        if source["status"] != "implemented" or target["status"] != "implemented":
            errors.append(f"{location}: only realizes links implemented code to a proposal")
            return
        if source["container"] != target["container"]:
            errors.append(f"{location}: code relationships stay within one container")
        if kind == "implements" and target.get("kind") != "interface":
            errors.append(f"{location}: implements target must be an interface")
        if kind == "persists":
            covered = set(source.get("persistence", {}).get("tables", []))
            stored = ([target["persisted_as"]] if target.get("persisted_as")
                      else target.get("storage", {}).get("tables", []))
            if not covered or not stored or not set(stored) <= covered:
                errors.append(f"{location}: persists must target tables declared by the source's persistence")
        method_map = {m["name"] for m in target["methods"]}
        for name in rel.get("methods", []):
            if name not in method_map:
                errors.append(f"{location}: unknown called method {name}")
    return check


def check_diagrams(design, classes, elements, views, containers, architecture):
    errors = []
    diagrams = design["class_diagrams"]
    limit = min(design["design_rules"]["max_nodes_per_diagram"],
                architecture["architecture"]["view_constraints"]["max_nodes_per_view"])
    diagram_ids = [item.get("id") for item in diagrams]
    if diagram_ids[:3] != list(ZOOMS):
        errors.append("CD-1, CD-2, CD-3 are required first, in order")
    if len(diagram_ids) != len(set(diagram_ids)):
        errors.append("diagram IDs must be unique")
    component_view = RECOMMENDATION_RULES["navigation_views"][-1]
    container_views = [v for v in views.values() if v.get("kind") == "c4_container"]
    relationships = [r for r in design["relationships"] if isinstance(r, dict)]
    used, detailed = set(), set()
    for diagram in diagrams:
        did, zoom = diagram.get("id"), diagram.get("zoom_target")
        members = diagram.get("elements", [])
        if not isinstance(members, list) or any(not isinstance(m, str) for m in members):
            errors.append(f"{did}: elements must be a list of class ids")
            continue
        used.update(members)
        if not isinstance(did, str) or not DIAGRAM_ID.fullmatch(did):
            errors.append(f"{did}: diagram id must be CD-<n>")
        if len(members) != len(set(members)):
            errors.append(f"{did}: duplicate members")
        if len(members) > limit:
            errors.append(f"{did}: {len(members)} nodes exceeds maximum {limit} (including proxies)")
        if not members or not diagram.get("title"):
            errors.append(f"{did}: title and members are required")
        unknown = [cid for cid in members if cid not in classes]
        for cid in unknown:
            errors.append(f"{did}: unknown member {cid}")
        if unknown:
            continue
        container = diagram.get("container")
        if did in ZOOMS:
            if diagram.get("kind") != "component_design" or container != "recommendation_service":
                errors.append(f"{did}: must be a component_design diagram of recommendation_service")
            if zoom not in elements or zoom != ZOOMS.get(did):
                errors.append(f"{did}: zoom_target must exist and match {ZOOMS.get(did)}")
            if zoom not in views.get(component_view, {}).get("elements", []):
                errors.append(f"{did}: zoom_target is not a declared C4 component view member")
            if any(classes[cid]["status"] != "proposed" for cid in members):
                errors.append(f"{did}: component design diagrams contain proposed classes only")
            detailed.update(members)
        else:
            if diagram.get("kind") != "bounded_context":
                errors.append(f"{did}: diagrams after CD-3 must be bounded_context diagrams")
            if container not in containers:
                errors.append(f"{did}: container must have design_rules.containers rules")
            if zoom != container or not any(zoom in v.get("elements", []) for v in container_views):
                errors.append(f"{did}: zoom_target must be its container, a member of a C4 container view")
            for cid in members:
                if class_container(classes[cid], elements) != container:
                    errors.append(f"{did}: member {cid} belongs to another container")
            if not any(classes[cid]["status"] == "implemented" for cid in members):
                errors.append(f"{did}: a bounded-context diagram shows implemented code")
        summary = diagram.get("summary_members", [])
        if not isinstance(summary, list) or not set(summary) <= set(members) or any(
                classes[cid]["status"] != "proposed" for cid in summary):
            errors.append(f"{did}: summary_members must be proposed members shown without compartments")
        notes = diagram.get("notes", [])
        if not isinstance(notes, list) or any(not isinstance(n, str) or not n.strip() for n in notes):
            errors.append(f"{did}: notes must be nonempty strings")
        errors.extend(check_print_parts(diagram, relationships))
    for diagram in diagrams:
        missing = set(diagram.get("summary_members", [])) - detailed
        if missing:
            errors.append(f"{diagram.get('id')}: summary members {sorted(missing)} need a detailed figure")
    if used != set(classes):
        errors.append(f"unrendered/unknown classes: {sorted(used ^ set(classes))}")
    return errors


def check_print_parts(diagram, relationships):
    """Print parts split a figure for A4; together they keep every member and relationship."""
    did, members = diagram["id"], diagram["elements"]
    parts = diagram.get("print_parts")
    if parts is None:
        return []
    errors = []
    if not isinstance(parts, list) or len(parts) < 2 or any(not isinstance(p, dict) for p in parts):
        return [f"{did}: print_parts must list at least two parts"]
    suffixes = [p.get("suffix") for p in parts]
    if suffixes != [chr(ord("a") + i) for i in range(len(parts))]:
        errors.append(f"{did}: print part suffixes must be a, b, c... in order")
    covered = set()
    for part in parts:
        where = f"{did}{part.get('suffix')}"
        elements = part.get("elements")
        if not isinstance(part.get("title"), str) or not part["title"].strip():
            errors.append(f"{where}: print part title required")
        if not isinstance(elements, list) or not elements or not set(elements) <= set(members):
            errors.append(f"{where}: print part elements must be members of {did}")
            continue
        covered.update(elements)
    if covered != set(members):
        errors.append(f"{did}: print parts omit members {sorted(set(members) - covered)}")
    for rel in relationships:
        if rel.get("from") in members and rel.get("to") in members and not any(
                {rel["from"], rel["to"]} <= set(p.get("elements") or []) for p in parts):
            errors.append(f"{did}: print parts omit relationship {rel['from']} -> {rel['to']}")
    return errors


def check_declarations(design, repos, workspace):
    """Workspace check: the first reference of each implemented class declares that class."""
    errors, cache = [], {}
    languages = {cid: rules["language"] for cid, rules in design["design_rules"]["containers"].items()}
    for item in design["classes"]:
        if item.get("status") != "implemented":
            continue
        ref = evidence.parse(item["implementation"]["evidence"][0])
        entry = repos[ref.repo]
        key = (ref.repo, ref.path)
        if key not in cache:
            result = subprocess.run(["git", "-C", str(Path(workspace) / entry["path"]), "show",
                                     f"{entry['revision']}:{ref.path}"], capture_output=True, text=True)
            cache[key] = result.stdout.splitlines() if result.returncode == 0 else None
        lines = cache[key]
        if lines is None:
            errors.append(f"{item['id']}: {ref} not found at {ref.repo}@{entry['revision']}")
            continue
        simple = item["name"].split(".")[-1]
        pattern = re.compile(LANGUAGES[languages[item["container"]]]["declaration"].format(name=re.escape(simple)))
        if not any(pattern.search(line) for line in lines[ref.start - 1:ref.end]):
            errors.append(f"{item['id']}: {ref} does not declare {simple}")
    return errors


def validate_design(design, architecture, domain, root=ROOT, repos=None):
    try:
        repos = evidence.repositories() if repos is None else repos
        return _validate(design, architecture, domain, Path(root), repos)
    except (KeyError, TypeError, AttributeError, ValueError, OSError) as exc:
        return [f"invalid design/source structure: {exc}"]


def main(argv=None):
    defaults = [ROOT / "model/design.yml", ROOT / "model/architecture.yml", ROOT / "model/domain.yml"]
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path, help="design, architecture and domain models")
    parser.add_argument("--workspace", help="directory with the sibling clones (optional declaration check)")
    args = parser.parse_args(argv)
    paths = [*args.paths, *defaults[len(args.paths):]][:3]
    try:
        design, architecture, domain = load_models(paths)
        errors = validate_design(design, architecture, domain)
        if not errors and args.workspace:
            errors = check_declarations(design, evidence.repositories(), args.workspace)
    except (OSError, yaml.YAMLError) as exc:
        errors = [f"cannot load required SSOT: {exc}"]
    if errors:
        print("DESIGN VALIDATION FAILED\n" + "\n".join(f"- {e}" for e in errors))
        return 1
    suffix = " (declarations checked in the workspace)" if args.workspace else ""
    print(f"DESIGN VALIDATION PASSED{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
