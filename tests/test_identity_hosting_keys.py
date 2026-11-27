"""ADR-022/029/030 and Key Vault facts the figures must not lose."""

from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class IdentityHostingAndKeysTests(unittest.TestCase):
    def setUp(self):
        self.model = yaml.safe_load((ROOT / "model/architecture.yml").read_text(encoding="utf-8"))
        self.elements = {e["id"]: e for e in self.model["elements"]}
        self.relations = {r["id"]: r for r in self.model["relationships"]}

    def test_humans_sign_in_with_github_not_entra(self):
        # ADR-022: no Entra app registrations; Entra stays only for Azure resource access.
        self.assertNotIn("entra_id", self.elements)
        self.assertFalse([r for r in self.relations.values() if "entra_id" in (r["from"], r["to"])])
        sign_in = self.relations["rel_dashboard_github_sign_in"]
        self.assertEqual((sign_in["from"], sign_in["to"]), ("web_dashboard", "github"))
        self.assertIn("PKCE S256", sign_in["protocol"])
        self.assertTrue({"SRC_ADR_022", "SRC_ADR_029"} <= set(sign_in["source"]))
        perimeter = self.model["deployment"]["identity_and_api_perimeter"]
        self.assertTrue(perimeter["identity_provider"].startswith("GitHub"))
        self.assertEqual(perimeter["azure_resource_identity"], "Microsoft Entra ID managed identities")

    def test_dashboard_is_served_from_container_apps(self):
        dashboard = self.elements["web_dashboard"]
        self.assertEqual(dashboard["host"]["concrete_service"], "Azure Container Apps")
        self.assertIn("SRC_ADR_030", dashboard["source"])

    def test_key_vault_signs_for_each_issuing_workload_only(self):
        vault = self.elements["azure_key_vault"]
        self.assertEqual(vault["key_custody"]["operations"], ["sign", "verify"])
        self.assertFalse(vault["key_custody"]["exportable"])
        # Component relationships (C4 Level 3) are lifted to their container.
        signers = {self.elements[r["from"]].get("parent", r["from"])
                   for r in self.relations.values() if r["to"] == "azure_key_vault"}
        # RAG verifies tokens through JWKS and signs none, so it does not reach Key Vault.
        self.assertEqual(signers, {"ingestion_normalization_service", "pipeline_service", "log_event_service",
                                   "nlp_log_processor", "evidence_correlation_engine", "recommendation_service"})

    def test_diagnosis_model_is_limited_to_the_adr_026_scope(self):
        llm = self.elements["pretrained_llm_diagnostic_service"]
        self.assertEqual((llm["model"], llm["model_version"]), ("gpt-6-luna", "2026-09-22"))
        self.assertEqual(llm["model_scope"], "dev_and_oe3_i2_evaluation")
        self.assertIsNone(llm["model_family"])
        self.assertIn("SRC_ADR_026", llm["source"])


if __name__ == "__main__":
    unittest.main()
