import copy
from pathlib import Path
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "generators"))

import c4  # noqa: E402
import evidence  # noqa: E402
import implementation_status  # noqa: E402
import traceability  # noqa: E402
from architecture_policy import validate_policy  # noqa: E402
from to_er_d2 import generate_er  # noqa: E402


def load(name):
    return yaml.safe_load((ROOT / "model" / name).read_text(encoding="utf-8"))


class EvidenceReferenceTests(unittest.TestCase):
    def test_reference_format_and_ranges(self):
        ref = evidence.parse("ingestion:src/main/java/A.java:10-12")
        self.assertEqual((ref.repo, ref.path, ref.start, ref.end, ref.short), ("ingestion", "src/main/java/A.java", 10, 12, "A.java:10-12"))
        self.assertEqual(evidence.parse("iac:modules/x.tf:4").end, 4)
        for bad in ("ingestion:A.java", "Ingestion:A.java:1", "ingestion:A.java:0", "ingestion:A.java:5-2", "x y:a:1"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                evidence.parse(bad)

    def test_unknown_repository_and_empty_lists_are_rejected(self):
        repos = {"iac": {"path": "pipesor-iac", "revision": "318af56"}}
        self.assertTrue(evidence.validate_refs(["other:a.tf:1"], repos, "x"))
        self.assertTrue(evidence.validate_refs([], repos, "x"))
        self.assertFalse(evidence.validate_refs(["iac:a.tf:1"], repos, "x"))


class OverlayValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.architecture, cls.domain = load("architecture.yml"), load("domain.yml")
        cls.overlay = implementation_status.load()

    def errors(self, mutate):
        overlay = copy.deepcopy(self.overlay)
        mutate(overlay)
        return "\n".join(implementation_status.validate(overlay, self.architecture, self.domain))

    def test_current_overlay_is_valid_and_complete(self):
        self.assertEqual(implementation_status.validate(self.overlay, self.architecture, self.domain), [])

    def test_unknown_ids_states_and_missing_basis_are_rejected(self):
        elements = lambda o: o["architecture"]["elements"]
        self.assertIn("unknown model ID", self.errors(lambda o: elements(o).update(ghost={"status": "external", "reason": "x"})))
        self.assertIn("status must be one of", self.errors(lambda o: elements(o)["github"].update(status="done")))
        self.assertIn("evidence must be a non-empty list",
                      self.errors(lambda o: elements(o)["pipeline_service"].update(evidence=[])))
        self.assertIn("requires a reason", self.errors(
            lambda o: o["architecture"]["relationships"]["rel_observability_sources_ingestion"].pop("reason")))
        self.assertIn("requires a note", self.errors(lambda o: elements(o)["log_event_service"].pop("note")))
        self.assertIn("missing implementation state", self.errors(lambda o: elements(o).pop("rag_retrieval")))
        self.assertIn("missing implementation state", self.errors(lambda o: o["domain"]["entities"].pop("incidents")))
        self.assertIn("unknown repository", self.errors(
            lambda o: elements(o)["pipeline_service"].update(evidence=["nowhere:a.java:1"])))

    def test_known_divergences_are_recorded(self):
        rels = self.overlay["architecture"]["relationships"]
        self.assertEqual(rels["rel_diagnostic_api_orchestrator"]["status"], "divergent")
        self.assertEqual(rels["rel_dashboard_log_event_service"]["status"], "not_implemented")
        entities = self.overlay["domain"]["entities"]
        self.assertEqual({k for k, v in entities.items() if v["status"] == "not_implemented"},
                         {"recommendations", "diagnosis_evidence_links", "diagnosis_source_links"})
        self.assertEqual(entities["diagnoses"]["status"], "partial")

    def test_combined_state_of_aggregated_edges(self):
        self.assertEqual(implementation_status.combined(["implemented", "not_implemented"]), "partial")
        self.assertEqual(implementation_status.combined(["not_implemented", "not_implemented"]), "not_implemented")
        self.assertIn(implementation_status.combined(["external", "implemented"]), {"external", "implemented"})
        self.assertEqual(c4.combined_state(["implemented", "divergent"]), "partial")
        self.assertIsNone(c4.combined_state([None]))


class MarkedDiagramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.architecture, cls.domain = load("architecture.yml"), load("domain.yml")
        cls.overlay = implementation_status.load()
        cls.projections = {p.view["id"]: p for p in c4.prepare(cls.architecture)[0]}

    def test_c4_marks_state_with_colour_and_text(self):
        source = c4.generate_puml(self.architecture, self.projections["c4_container_consumption"], set(),
                                  c4.load_presentation(), self.overlay)
        self.assertIn('"REST/HTTPS · not implemented", $tags="sync+not_implemented"', source)
        self.assertIn('AddRelTag("divergent"', source)
        self.assertIn("caption Implementation state", source)
        unmarked = c4.generate_puml(self.architecture, self.projections["c4_container_consumption"], set())
        self.assertNotIn("not implemented", unmarked)

    def test_containers_and_components_show_language_and_framework(self):
        elements = {e["id"]: e for e in self.architecture["elements"]}
        self.assertEqual(c4.technology(elements["pipeline_service"], set()), "Java / Spring Boot")
        self.assertEqual(c4.technology(elements["rag_retrieval"], set()), "Python / FastAPI")
        self.assertEqual(c4.technology(elements["ingestion_sign_in_component"], set(), elements=elements), "Java / Spring Boot")

    def test_ingestion_component_view(self):
        projection = self.projections["c4_component_ingestion"]
        self.assertEqual((len(projection.inside), projection.count), (7, 14))
        self.assertTrue(all(e["status"] == "inferred" for e in projection.inside))
        ids = {r["id"] for r in projection.relationships}
        self.assertIn("rel_dashboard_ingestion_sign_in", ids)
        self.assertNotIn("rel_dashboard_ingestion_github_connection", ids)
        # Derived component relationships never reappear at Level 2.
        container_ids = {r["id"] for r in self.projections["c4_container_processing"].relationships}
        self.assertFalse(container_ids & {r["id"] for r in self.architecture["relationships"] if "derived_from" in r})

    def test_gateway_components_keep_the_privacy_invariant(self):
        self.assertEqual(validate_policy(self.architecture), [])
        bypass = copy.deepcopy(self.architecture)
        bypass["relationships"].append({"id": "rel_bypass", "from": "diagnostic_api_component", "to": "nlp_log_processor",
                                        "label": "x", "protocol": "x", "style": "sync"})
        bypass["relationships"].append({"id": "rel_entry", "from": "github_actions", "to": "diagnostic_api_component",
                                        "label": "x", "protocol": "x", "style": "sync", "access": "read_only"})
        self.assertTrue(any("INV-001" in e for e in validate_policy(bypass)))

    def test_er_marks_tables_and_columns(self):
        source = generate_er(self.domain, self.overlay)
        self.assertIn('diagnoses: "diagnoses [partially implemented]"', source)
        self.assertIn('recommendations: "recommendations [modeled, not implemented]"', source)
        self.assertIn('confidence: "jsonb · modeled, not implemented"', source)
        self.assertIn("33 of 36 tables implemented", source)

    def test_traceability_lists_every_view_and_table(self):
        text = traceability.generate()
        for view in self.architecture["views"]:
            if view["kind"].startswith("c4_"):
                self.assertIn(f"(`{view['id']}`)", text)
        for entity in self.domain["entities"]:
            self.assertIn(f"`{entity['id']}`", text)
        self.assertIn("`rel_dashboard_log_event_service` |", text)


if __name__ == "__main__":
    unittest.main()
