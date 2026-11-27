"""Bounded-context class diagrams: implementation status, code evidence, containers and A4 print."""

from collections import Counter
from copy import deepcopy
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "generators"))
from validate_design import check_declarations, load_models, validate_design  # noqa: E402
from tools.generators import classes as generator  # noqa: E402
import document_figures  # noqa: E402
import evidence  # noqa: E402

NOT_IMPLEMENTED = {
    "GenerateDiagnosisCommand", "GenerateDiagnosisCommandService", "GetDiagnosisQuery", "DiagnosisQueryService",
    "LlmResponseTranslator", "SanitizedDiagnosticContext", "DiagnosticOutputComposer", "Recommendation",
    "ProbableCause", "HumanReviewCommandService", "HumanReviewQueryService", "RiskClassificationService",
    "AuditTrailPort", "PostgresAuditTrailAdapter",
}
WORKSPACE = ROOT.parents[1]


class BoundedContextDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design, cls.architecture, cls.domain = load_models([
            ROOT / "model/design.yml", ROOT / "model/architecture.yml", ROOT / "model/domain.yml"])

    def setUp(self):
        self.model = deepcopy(self.design)
        self.arch = deepcopy(self.architecture)

    def item(self, cid):
        return next(c for c in self.model["classes"] if c["id"] == cid)

    def errors(self):
        return validate_design(self.model, self.arch, self.domain)

    def rejected(self, fragment):
        self.assertIn(fragment, "\n".join(self.errors()))

    # Implementation status -----------------------------------------------------------------
    def test_model_is_valid_and_proposals_stay_proposed(self):
        self.assertEqual(self.errors(), [])
        proposed = [c for c in self.model["classes"] if c["status"] == "proposed"]
        self.assertEqual(len(proposed), 38)
        diagrams = {d["id"]: d for d in self.model["class_diagrams"]}
        self.assertEqual({c["id"] for c in proposed},
                         set(diagrams["CD-1"]["elements"]) | set(diagrams["CD-2"]["elements"])
                         | set(diagrams["CD-3"]["elements"]))

    def test_the_fourteen_missing_classes_are_not_implemented_with_reason(self):
        proposed = [c for c in self.model["classes"] if c["status"] == "proposed"]
        missing = {c["id"] for c in proposed if c["implementation"]["status"] == "not_implemented"}
        self.assertEqual(missing, NOT_IMPLEMENTED)
        self.assertTrue(all(c["implementation"]["reason"].strip() for c in proposed if c["id"] in missing))
        counts = Counter(c["implementation"]["status"] for c in proposed)
        self.assertEqual(counts, {"implemented": 7, "partial": 5, "divergent": 11, "not_implemented": 14,
                                  "external": 1})

    def test_invalid_status_and_missing_reason_rejected(self):
        self.item("Recommendation")["implementation"]["status"] = "done"
        self.rejected("Recommendation.implementation: status must be one of")
        self.model = deepcopy(self.design)
        del self.item("Recommendation")["implementation"]["reason"]
        self.rejected("Recommendation.implementation: not_implemented requires a reason")
        self.model = deepcopy(self.design)
        del self.item("Diagnosis")["implementation"]["note"]
        self.rejected("Diagnosis.implementation: divergent requires a note")
        self.model = deepcopy(self.design)
        self.item("Incident")["implementation"]["status"] = "not_implemented"
        self.rejected("a class transcribed from code must be implemented, partial or divergent")
        self.model = deepcopy(self.design)
        self.item("Diagnosis")["implementation"]["status"] = "external"
        self.rejected("external status is reserved for External proxies")

    def test_malformed_evidence_rejected(self):
        for value, fragment in (("pipeline:Incident.java", "invalid evidence reference"),
                                ("nowhere:src/A.java:3", "unknown repository 'nowhere'"),
                                ("pipeline:src/A.java:9-3", "invalid evidence range")):
            with self.subTest(value=value):
                self.model = deepcopy(self.design)
                self.item("Incident")["implementation"]["evidence"] = [value]
                self.rejected(fragment)
        self.model = deepcopy(self.design)
        self.item("Incident")["implementation"]["evidence"] = []
        self.rejected("Incident.implementation: evidence must be a non-empty list")
        self.model = deepcopy(self.design)
        self.item("Incident")["implementation"]["evidence"][0] = self.item("Incident")["implementation"]["evidence"][0] \
            .replace("pipeline:", "ingestion:")
        self.rejected("first evidence must cite the pipeline_service repository (pipeline)")
        self.model = deepcopy(self.design)
        self.item("Incident")["package"] = "org.pipesor.pipeline.incident.domain.model"
        self.rejected("first evidence path does not match package")

    # Containers and languages --------------------------------------------------------------
    def test_container_without_language_rejected(self):
        del self.model["design_rules"]["containers"]["rag_retrieval"]["language"]
        self.rejected("design_rules.containers.rag_retrieval: language and framework are required")
        self.model = deepcopy(self.design)
        next(e for e in self.arch["elements"] if e["id"] == "rag_retrieval").pop("backend")
        self.rejected("architecture.yml declares no backend language/framework for this container")
        self.arch = deepcopy(self.architecture)
        self.model["design_rules"]["containers"]["rag_retrieval"]["language"] = "Java"
        self.rejected("Java / FastAPI must match architecture.yml backend")
        self.model = deepcopy(self.design)
        self.model["design_rules"]["containers"]["web_dashboard"] = deepcopy(
            self.model["design_rules"]["containers"]["rag_retrieval"])
        self.rejected("design_rules.containers.web_dashboard")

    def test_recommendation_keeps_the_proposal_rules(self):
        self.model["design_rules"]["containers"]["recommendation_service"]["event_sourcing"] = True
        self.rejected("recommendation_service.event_sourcing: expected False")
        self.model = deepcopy(self.design)
        self.model["design_rules"]["containers"]["recommendation_service"]["repository"] = "rag"
        self.rejected("recommendation_service.repository: expected 'recommendation'")

    def test_language_conventions(self):
        self.item("Incident")["attributes"][0]["type"] = "UUID | None"
        self.rejected("Incident.id: type syntax does not match container language Java")
        self.model = deepcopy(self.design)
        self.item("KnowledgeChunk")["attributes"][0]["name"] = "documentId"
        self.rejected("KnowledgeChunk.documentId: attribute naming does not follow Python")
        self.model = deepcopy(self.design)
        self.item("KnowledgeChunk")["attributes"][0]["type"] = "List<UUID>"
        self.rejected("type syntax does not match container language Python")
        self.model = deepcopy(self.design)
        self.item("Incident")["layer"] = "application"
        self.rejected("Incident: layer must be 'domain', derived from the package")
        self.model = deepcopy(self.design)
        self.item("ReviewRecord")["layer"] = "infrastructure"
        self.rejected("ReviewRecord: layer must be 'unlayered'")

    # Persistence ---------------------------------------------------------------------------
    def test_persistence_must_match_domain(self):
        self.item("IncidentJpaEntity")["attributes"].pop()
        self.rejected("IncidentJpaEntity: persisted attributes must exactly match domain.yml")
        self.model = deepcopy(self.design)
        self.item("KnowledgeChunkRecord")["attributes"][5]["type"] = "list[float]"
        self.rejected("KnowledgeChunkRecord.embedding: mapping/type/nullability differs from domain.yml")
        self.model = deepcopy(self.design)
        self.item("CorrelatedContextEntity")["attributes"][1]["type"] = "String"
        self.rejected("CorrelatedContextEntity.incidentId: mapping/type/nullability differs")
        self.model = deepcopy(self.design)
        self.item("Incident")["storage"]["tables"] = ["diagnosis.diagnoses"]
        self.rejected("table diagnosis.diagnoses belongs to recommendation_service, not pipeline_service")
        self.model = deepcopy(self.design)
        self.item("IncidentDetails")["storage"]["columns"].append("invented")
        self.rejected("IncidentDetails.storage: column invented absent from the listed tables")
        self.model = deepcopy(self.design)
        del self.item("OrchestratorSource")["storage"]["columns"]
        self.rejected("OrchestratorSource.storage: json_column requires the columns it uses")
        self.model = deepcopy(self.design)
        del self.item("EvidenceScope")["storage"]
        self.rejected("EvidenceScope: declare exactly one of persisted_as or storage")
        self.model = deepcopy(self.design)
        self.item("GitHubRepository")["storage"] = {"form": "not_persisted", "note": "x"}
        self.rejected("GitHubRepository: declare exactly one of persisted_as or storage")
        self.model = deepcopy(self.design)
        self.item("Incident")["storage"]["via"] = "JpaCaptureLedger"
        self.rejected("Incident.storage: via must be an adapter whose persistence covers the tables")
        self.model = deepcopy(self.design)
        self.item("LogEnvelope")["storage"] = {"form": "not_persisted", "tables": ["knowledge.knowledge_chunks"],
                                               "note": "x"}
        self.rejected("LogEnvelope.storage: not_persisted lists no tables")
        self.model = deepcopy(self.design)
        self.item("JdbcEvidenceStore")["persistence"]["store"] = "pgvector_knowledge_store"
        self.rejected("JdbcEvidenceStore: persistence store must be the container's postgresql_operational_store")

    def test_proposed_persistence_rules_unchanged(self):
        self.item("Diagnosis")["storage"] = {"form": "not_persisted", "note": "x"}
        self.rejected("Diagnosis: storage is for implemented classes; proposals use persisted_as")

    # Relationships and diagrams ------------------------------------------------------------
    def test_realizes_requires_the_proposal_to_cite_the_code(self):
        block = self.item("Diagnosis")["implementation"]
        block["evidence"] = [e for e in block["evidence"] if "DiagnosticOrchestrator.java" not in e]
        self.rejected("OrchestratorDiagnosis -> Diagnosis (realizes): the proposal's evidence must cite the realizing code")
        self.model = deepcopy(self.design)
        self.model["relationships"].append({"from": "OrchestratorHypothesis", "to": "Recommendation", "type": "realizes",
                                            "label": "x"})
        self.model["class_diagrams"][8]["print_parts"][0]["elements"].append("OrchestratorHypothesis")
        self.rejected("realizes requires an implemented, partial or divergent proposal")
        self.model = deepcopy(self.design)
        self.model["relationships"].append({"from": "OrchestratorHypothesis", "to": "Recommendation", "type": "uses"})
        self.rejected("only realizes links implemented code to a proposal")

    def test_bounded_context_diagram_rules(self):
        cd4 = next(d for d in self.model["class_diagrams"] if d["id"] == "CD-4")
        cd4["elements"].append("EvidenceInput")
        self.rejected("CD-4: member EvidenceInput belongs to another container")
        self.rejected("CD-4: 16 nodes exceeds maximum 15")
        self.model = deepcopy(self.design)
        next(d for d in self.model["class_diagrams"] if d["id"] == "CD-7")["zoom_target"] = "pipeline_service"
        self.rejected("CD-7: zoom_target must be its container")
        self.model = deepcopy(self.design)
        cd9 = next(d for d in self.model["class_diagrams"] if d["id"] == "CD-9")
        cd9["summary_members"].append("OrchestratorDiagnosis")
        self.rejected("CD-9: summary_members must be proposed members")

    def test_print_parts_keep_members_and_relationships(self):
        cd4 = next(d for d in self.model["class_diagrams"] if d["id"] == "CD-4")
        cd4["print_parts"][-1]["elements"].remove("IncidentRunRole")
        self.rejected("CD-4: print parts omit members ['IncidentRunRole']")
        self.model = deepcopy(self.design)
        cd4 = next(d for d in self.model["class_diagrams"] if d["id"] == "CD-4")
        cd4["print_parts"][0]["elements"].remove("ExecutionOutcome")
        cd4["print_parts"][2]["elements"].append("ExecutionOutcome")
        self.rejected("CD-4: print parts omit relationship Incident -> ExecutionOutcome")
        self.model = deepcopy(self.design)
        next(d for d in self.model["class_diagrams"] if d["id"] == "CD-4")["print_parts"][1]["suffix"] = "z"
        self.rejected("CD-4: print part suffixes must be a, b, c... in order")

    # Generation ----------------------------------------------------------------------------
    def test_status_marks_and_titles(self):
        sources = {d["id"]: generator.generate_puml(self.model, d) for d in self.model["class_diagrams"]}
        marked = set()
        for did in ("CD-1", "CD-2", "CD-3"):
            self.assertIn("Proposed design", sources[did])
            for line in sources[did].splitlines():
                if "<<not implemented>>" in line:
                    self.assertIn("line.dashed", line)
                    marked.add(line.split(" as ")[1].split()[0])
        self.assertEqual(marked, NOT_IMPLEMENTED)
        self.assertIn("<<divergent>> #line:B26A00;line.bold", sources["CD-2"])
        self.assertIn("<<external>> #line:6B7280;line.dotted", sources["CD-2"])
        self.assertIn("Implemented code · code at pipeline@", sources["CD-4"])
        self.assertIn("Implemented code vs proposed design", sources["CD-9"])
        self.assertIn("code: Incident.java:17-46, 50-89", sources["CD-4"])
        summary = sources["CD-9"].split('"Diagnosis" as Diagnosis', 1)[1].split("}", 1)[0]
        self.assertNotIn("-id:", summary)

    def test_member_wrapping_keeps_compartments(self):
        lines = generator.member_lines("+appendHumanReviewMetadata(UUID, UUID, String, HumanReviewDecision, Instant, "
                                       "String): void", True, "method")
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(line.startswith("  {method}") for line in lines[1:]))
        self.assertEqual(generator.member_lines("-id: UUID", True), ["  -id: UUID"])

    def test_deterministic_print_sources(self):
        script = (
            "from tools.generators.classes import *; "
            "d,a,m=load_models([ROOT/'model/design.yml',ROOT/'model/architecture.yml',ROOT/'model/domain.yml']); "
            "print(''.join(generate_puml(d,v,document=True,members=p['elements'],title=p['title'],direction=l[0],"
            "clusters=l[1],wrap=l[2],anchors=l[3]) for v in d['class_diagrams'] for p in v['print_parts'] "
            "for l in PRINT_LAYOUTS))")
        outputs = [subprocess.run([sys.executable, "-c", script], cwd=ROOT,
                                  env={**os.environ, "PYTHONHASHSEED": seed}, capture_output=True,
                                  text=True, check=True, timeout=60).stdout for seed in ("1", "42")]
        self.assertEqual(*outputs)

    def test_navigation_covers_every_diagram(self):
        navigation = generator.navigation_markdown(self.model, self.architecture)
        for diagram in self.model["class_diagrams"]:
            self.assertIn(f"({diagram['id']}.svg)", navigation)
        self.assertIn("[`c4_container_processing`](c4_container_processing.svg) → `rag_retrieval` → [CD-11]",
                      navigation)

    def test_normalized_svg_root_accepts_print_size(self):
        with tempfile.TemporaryDirectory() as folder:
            svg = Path(folder) / "x.svg"
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" style="width:300px;height:100px;background:#FFF;" '
                           'width="300px" height="100px" viewBox="0 0 300 100"><text font-size="12">a</text></svg>',
                           encoding="utf-8")
            generator.normalize_svg_root(svg)
            document_figures.set_svg_print_size(svg, 10.0, 3.33)
            text = svg.read_text(encoding="utf-8")
            self.assertTrue(text.startswith('<svg width="10.00cm" height="3.33cm" '))
            self.assertNotIn("width:300px", text)

    @unittest.skipUnless(shutil.which("java") and shutil.which("dot"), "PlantUML needs Java and Graphviz")
    def test_print_parts_reach_eight_points(self):
        model = deepcopy(self.design)
        model["class_diagrams"] = [d for d in model["class_diagrams"] if d["id"] in {"CD-7", "CD-10"}]
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as folder:
            _, measured = generator.measure_print(model, Path(folder) / "classes")
            for diagram in model["class_diagrams"]:
                for part in diagram["print_parts"]:
                    fid = diagram["id"] + part["suffix"]
                    with self.subTest(figure=fid):
                        pick = generator.best(measured[fid], document_figures.MIN_POINTS,
                                              document_figures.TARGET_POINTS)
                        self.assertIsNotNone(pick)
                        layout, page, _, width, height, smallest = pick
                        self.assertGreaterEqual(smallest, document_figures.MIN_POINTS)
                        self.assertLessEqual(width, document_figures.PAGES[page][0] + 1e-6)
                        self.assertLessEqual(height, document_figures.PAGES[page][1] + 1e-6)

    @unittest.skipUnless((WORKSPACE / "services").is_dir(), "sibling clones not available")
    def test_workspace_declarations(self):
        self.assertEqual(check_declarations(self.design, evidence.repositories(), WORKSPACE), [])


if __name__ == "__main__":
    unittest.main()
