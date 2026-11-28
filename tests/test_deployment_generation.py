"""Deployment views: validation of the presentation model and deterministic DOT."""

import copy
from pathlib import Path
import tempfile
import unittest

from tools.generators import deployment as dep

ROOT = Path(__file__).resolve().parents[1]


def figure(model, fid):
    return next(f for f in model["figures"] if f["id"] == fid)


def node(model, fid, nid):
    return next(n for n in figure(model, fid)["nodes"] if n["id"] == nid)


def edge(model, fid, eid):
    return next(e for e in figure(model, fid)["edges"] if e["id"] == eid)


class DeploymentValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.presentation, cls.architecture, cls.overlay = dep.load()

    def setUp(self):
        self.model = copy.deepcopy(self.presentation)

    def errors(self, model=None, architecture=None):
        return dep.validate(model or self.model, architecture or self.architecture, self.overlay)

    def assertRejected(self, fragment, model=None, architecture=None):
        errors = self.errors(model, architecture)
        self.assertTrue(any(fragment in e for e in errors), f"{fragment!r} not in {errors}")

    def test_committed_model_is_valid(self):
        self.assertEqual(self.errors(self.presentation), [])

    def test_rejects_an_element_missing_from_the_architecture(self):
        node(self.model, "deploy_dev_runtime", "n_service_bus")["element"] = "azure_event_hubs"
        self.assertRejected("element 'azure_event_hubs' does not exist")

    def test_rejects_an_invalid_state(self):
        node(self.model, "deploy_dev_runtime", "n_log_analytics")["state"] = "running"
        self.assertRejected("invalid state 'running'")

    def test_rejects_malformed_evidence(self):
        node(self.model, "deploy_dev_runtime", "n_log_analytics")["evidence"] = ["iac:modules/container-platform/main.tf"]
        self.assertRejected("invalid evidence reference")
        node(self.model, "deploy_dev_runtime", "n_log_analytics")["evidence"] = ["azure:portal/workspace:1"]
        self.assertRejected("unknown repository 'azure'")
        node(self.model, "deploy_dev_runtime", "n_log_analytics")["evidence"] = []
        self.assertRejected("evidence must be a non-empty list")

    def test_rejects_malformed_documentary_sources(self):
        node(self.model, "deploy_environments_delivery", "t_order")["sources"] = ["docs/architecture/missing.md:3"]
        self.assertRejected("does not exist")

    def test_rejects_tbd_without_reason(self):
        del node(self.model, "deploy_environments_delivery", "t_gates")["reason"]
        self.assertRejected("tbd requires a non-empty reason")

    def test_rejects_an_edge_with_an_unknown_endpoint(self):
        edge(self.model, "deploy_dev_runtime", "r_ingestion_bus")["to"] = "n_event_grid"
        self.assertRejected("unknown endpoint 'n_event_grid'")

    def test_rejects_a_relationship_that_does_not_join_the_endpoints(self):
        edge(self.model, "deploy_dev_runtime", "r_rag_embeddings")["relationships"] = ["rel_recommendation_llm"]
        self.assertRejected("does not join the elements")

    def test_rejects_deployed_without_observation_and_observation_without_deployed(self):
        del node(self.model, "deploy_dev_runtime", "n_jobs")["observation"]
        self.assertRejected("deployed requires an observation")
        self.model = copy.deepcopy(self.presentation)
        node(self.model, "deploy_dev_runtime", "n_log_analytics")["observation"] = "container_apps"
        self.assertRejected("observation is only allowed on deployed items")

    def test_requires_exactly_one_of_element_or_implementation_only(self):
        node(self.model, "deploy_dev_runtime", "n_ghcr")["element"] = "github"
        self.assertRejected("exactly one of element or implementation_only")

    def test_rejects_duplicate_ids(self):
        nodes = figure(self.model, "deploy_dev_runtime")["nodes"]
        nodes.append(copy.deepcopy(nodes[0]))
        self.assertRejected("duplicate id 'n_browser'")

    def test_rejects_edges_to_tbd_points(self):
        edge(self.model, "deploy_environments_delivery", "d_dev_qa")["to"] = "t_gates"
        self.assertRejected("tbd nodes are listed in the TBD panel")

    def test_divergence_note_tracks_the_model(self):
        architecture = copy.deepcopy(self.architecture)
        architecture["deployment"]["mvp_preparation"]["deployment_authorized"] = True
        self.assertRejected("the note expects False", architecture=architecture)

    def test_respects_the_model_node_limit(self):
        architecture = copy.deepcopy(self.architecture)
        architecture["architecture"]["view_constraints"]["max_nodes_per_view"] = 10
        self.assertRejected("model elements exceed max_nodes_per_view 10", architecture=architecture)

    def test_states_are_the_authorized_vocabulary(self):
        self.assertEqual(tuple(self.presentation["states"]), ("deployed", "implemented", "proposed", "tbd"))
        self.model["states"] = {"deployed": "x", "implemented": "y"}
        self.assertRejected("states must declare exactly")

    def test_every_drawn_item_cites_the_model_or_is_marked_as_unmodeled(self):
        for fig in self.presentation["figures"]:
            for item in fig["nodes"]:
                if item["state"] == "tbd":
                    self.assertTrue(item["reason"].strip(), item["id"])
                else:
                    self.assertTrue(bool(item.get("element")) != bool(item.get("implementation_only")), item["id"])
                    self.assertTrue(item["evidence"], item["id"])
            for item in fig["edges"]:
                self.assertTrue(item["evidence"], item["id"])


class DeploymentRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.presentation, cls.architecture, cls.overlay = dep.load()
        cls.figures = dep.check(cls.presentation, cls.architecture, cls.overlay)

    def test_dot_is_deterministic(self):
        for fig in self.figures:
            first = dep.generate_dot(fig, self.architecture)
            again = dep.generate_dot(copy.deepcopy(fig), self.architecture)
            self.assertEqual(first, again, fig["id"])

    def test_dot_draws_states_numbers_and_the_tbd_panel(self):
        runtime = figure(self.presentation, "deploy_dev_runtime")
        source = dep.generate_dot(runtime, self.architecture)
        self.assertIn('id=r_bus_pipeline', source)
        self.assertRegex(source, r"id=r_bus_pipeline[^\]]*style=solid")
        self.assertRegex(source, r"id=r_app_insights_workspace[^\]]*style=dashed")
        self.assertIn("<B>19</B>", source)
        self.assertNotIn("<B>20</B>", source)
        delivery = figure(self.presentation, "deploy_environments_delivery")
        source = dep.generate_dot(delivery, self.architecture)
        self.assertIn("No definido (TBD)", source)
        self.assertNotIn("\tt_gates [", source)
        self.assertIn("deployment_authorized: false (ADR-019)", source)
        self.assertRegex(source, r"id=d_dev_qa[^\]]*style=dotted")

    def test_view_and_guide_are_written_where_asked(self):
        with tempfile.TemporaryDirectory() as directory:
            out, build = Path(directory) / "out", Path(directory) / "build"
            for fig in self.figures:
                dep.render_view(fig, self.architecture, build, out)
            self.assertEqual(sorted(p.name for p in out.iterdir()),
                             ["deploy_dev_runtime.svg", "deploy_environments_delivery.svg"])
        guide = dep.guide(self.presentation, self.architecture, self.overlay)
        for fig in self.figures:
            for item in fig["nodes"]:
                self.assertIn(item["name"].split("\n")[0], guide)
        self.assertIn("«implementación no modelada»", guide)
        self.assertIn("observación 27/11", guide)
        self.assertIn("deployment_authorized", guide)


if __name__ == "__main__":
    unittest.main()
