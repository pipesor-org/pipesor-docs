"""Sequence presentation model: validation and deterministic PlantUML."""

from copy import deepcopy
import re
import unittest

import yaml

from tools.generators import evidence
from tools.generators import sequences as seq

REPOS = {"svc": {"path": "services/svc", "revision": "abc1234"}}
REF = "svc:src/Main.java:10-12"


def architecture():
    """Minimal architecture: two containers, a component of the first and one relationship."""
    return {"elements": [{"id": "alpha", "name": "Alpha", "kind": "container", "status": "confirmed"},
                         {"id": "alpha_api", "name": "Alpha API", "kind": "component", "parent": "alpha",
                          "status": "confirmed"},
                         {"id": "beta", "name": "Beta", "kind": "container", "status": "confirmed"},
                         {"id": "store", "name": "Store", "kind": "datastore", "status": "confirmed"}],
            "relationships": [{"id": "rel_alpha_beta", "from": "alpha", "to": "beta", "label": "Calls Beta",
                               "status": "confirmed"},
                              {"id": "rel_beta_store", "from": "beta", "to": "store", "label": "Persists",
                               "status": "confirmed"}]}


def message(**overrides):
    value = {"from": "a", "to": "b", "style": "sync", "text": "POST /things", "relationship": "rel_alpha_beta",
             "state": "implemented", "evidence": [REF]}
    value.update(overrides)
    return {"message": value}


def presentation(*steps):
    return {"model_version": "1.0.0", "architecture_source": "model/architecture.yml",
            "sequences": [{"id": "seq_test", "title": "Test sequence", "purpose": "Prueba.",
                           "participants": [{"id": "a", "name": "Alpha", "element": "alpha"},
                                            {"id": "b", "name": "Beta", "element": "beta"}],
                           "steps": list(steps) or [message()]}]}


def errors(model):
    return seq.validate(model, architecture(), REPOS)


class SequenceValidationTests(unittest.TestCase):
    def test_repository_model_is_valid_and_cites_only_existing_relationships(self):
        model, arch = seq.load_models()
        self.assertEqual(seq.validate(model, arch), [])
        relationships = {r["id"] for r in arch["relationships"]}
        for sequence in model["sequences"]:
            for m in seq.messages(sequence["steps"]):
                if not m.get("implementation_only"):
                    self.assertIn(m["relationship"], relationships)
                self.assertIn(m["state"], evidence.STATUSES)
                self.assertTrue(m["evidence"])

    def test_minimal_model_is_valid(self):
        self.assertEqual(errors(presentation()), [])

    def test_rejects_unknown_relationship(self):
        found = errors(presentation(message(relationship="rel_missing")))
        self.assertTrue(any("unknown relationship 'rel_missing'" in e for e in found), found)

    def test_rejects_relationship_whose_ends_do_not_match(self):
        found = errors(presentation(message(relationship="rel_beta_store")))
        self.assertTrue(any("does not match a -> b" in e for e in found), found)
        found = errors(presentation(message(**{"from": "b", "to": "a"})))
        self.assertTrue(any("does not match b -> a" in e for e in found), found)

    def test_reply_runs_the_relationship_backwards(self):
        self.assertEqual(errors(presentation(message(), message(**{"from": "b", "to": "a", "style": "reply"}))), [])
        found = errors(presentation(message(style="reply")))
        self.assertTrue(any("reply runs it backwards" in e for e in found), found)

    def test_component_matches_its_container_relationship_and_back(self):
        model = presentation()
        model["sequences"][0]["participants"][0]["element"] = "alpha_api"
        self.assertEqual(errors(model), [])
        arch = architecture()
        arch["relationships"].append({"id": "rel_api_beta", "from": "alpha_api", "to": "beta", "status": "confirmed"})
        model = presentation(message(relationship="rel_api_beta"))
        self.assertEqual(seq.validate(model, arch, REPOS), [])

    def test_implementation_only_participant_matches_through_its_parent_only(self):
        model = presentation(message(**{"from": "w", "to": "b"}), message())
        worker = {"id": "w", "name": "Worker", "implementation_only": True, "kind": "worker", "evidence": [REF]}
        model["sequences"][0]["participants"].append(worker)
        self.assertTrue(any("does not match w -> b" in e for e in errors(model)))
        worker["parent"] = "alpha"
        self.assertEqual(errors(model), [])
        worker["parent"] = "missing"
        self.assertTrue(any("unknown parent element" in e for e in errors(model)))

    def test_rejects_invalid_state(self):
        found = errors(presentation(message(state="done")))
        self.assertTrue(any("state must be one of" in e for e in found), found)

    def test_rejects_malformed_evidence_or_unknown_repository(self):
        for refs, expected in (([], "non-empty list"), (["svc:src/Main.java"], "invalid evidence reference"),
                               (["svc:src/Main.java:12-10"], "invalid evidence range"),
                               (["other:src/Main.java:3"], "unknown repository 'other'")):
            found = errors(presentation(message(evidence=refs)))
            self.assertTrue(any(expected in e for e in found), (refs, found))

    def test_rejects_empty_or_malformed_fragments(self):
        empty_branches = {"fragment": {"kind": "alt", "label": "x", "branches": []}}
        self.assertTrue(any("fragment has no branches" in e for e in errors(presentation(message(), empty_branches))))
        empty_steps = {"fragment": {"kind": "opt", "label": "x", "branches": [{"guard": "g", "steps": []}]}}
        self.assertTrue(any("empty fragment branch" in e for e in errors(presentation(message(), empty_steps))))
        single_alt = {"fragment": {"kind": "alt", "label": "x", "branches": [{"guard": "g", "steps": [message()]}]}}
        self.assertTrue(any("alt needs at least two branches" in e for e in errors(presentation(single_alt))))
        unknown = {"fragment": {"kind": "critical", "label": "x", "branches": [{"guard": "g", "steps": [message()]}]}}
        self.assertTrue(any("fragment kind must be one of" in e for e in errors(presentation(unknown))))
        nested_section = {"fragment": {"kind": "opt", "label": "x",
                                       "branches": [{"guard": "g", "steps": [{"section": "S"}, message()]}]}}
        self.assertTrue(any("only allowed at the top level" in e for e in errors(presentation(nested_section))))

    def test_implementation_only_messages_need_a_reason_and_self_steps_are_unmodeled(self):
        self_step = message(**{"to": "a", "style": "self"})
        self.assertTrue(any("internal (self) steps are implementation-only" in e
                            for e in errors(presentation(message(), self_step))))
        unmodeled = message(implementation_only=True)
        found = errors(presentation(unmodeled))
        self.assertTrue(any("cannot cite a relationship" in e for e in found), found)
        del unmodeled["message"]["relationship"]
        self.assertTrue(any("need a reason" in e for e in errors(presentation(unmodeled))))
        unmodeled["message"]["reason"] = "Paso no modelado."
        self.assertEqual(errors(presentation(unmodeled)), [])

    def test_ids_are_unique_and_participants_used(self):
        model = presentation()
        model["sequences"].append(deepcopy(model["sequences"][0]))
        self.assertTrue(any("duplicate sequence id" in e for e in errors(model)))
        model = presentation()
        model["sequences"][0]["participants"].append({"id": "a", "name": "Again", "element": "beta"})
        self.assertTrue(any("duplicate participant id" in e for e in errors(model)))
        model = presentation()
        model["sequences"][0]["participants"].append({"id": "s", "name": "Store", "element": "store"})
        self.assertTrue(any("participant 's' is never used" in e for e in errors(model)))
        model = presentation()
        model["sequences"][0]["participants"][1]["element"] = "gamma"
        self.assertTrue(any("unknown architecture element 'gamma'" in e for e in errors(model)))


class SequenceRenderingTests(unittest.TestCase):
    def setUp(self):
        self.model, self.architecture = seq.load_models()
        self.ctx = seq.Context(self.architecture)

    def test_plantuml_is_deterministic_and_marks_states_styles_and_participants(self):
        for sequence in self.model["sequences"]:
            first = seq.generate_puml(sequence, self.ctx)
            self.assertEqual(first, seq.generate_puml(deepcopy(sequence), seq.Context(deepcopy(self.architecture))))
            self.assertIn("autonumber 1", first)
            self.assertIn(f"title {seq.wrapped(sequence['title'], seq.TITLE_WRAP)}", first)
            self.assertIn(f"footer {seq.FOOTER}", first)
            self.assertIn("legend bottom left", first)
        login = next(s for s in self.model["sequences"] if s["id"] == "seq_b_login")
        puml = seq.generate_puml(login, self.ctx)
        self.assertIn('participant "Browser" as browser <<implementation-only>> #FFFFFF', puml)
        self.assertIn('participant "Ingestion" as ing <<container>>', puml)
        self.assertIn('participant "GitHub" as gh <<external>>', puml)
        capture = seq.generate_puml(next(s for s in self.model["sequences"] if s["id"] == "seq_a1_capture"), self.ctx)
        self.assertRegex(capture, r"\ning -\[#2E7D32\]->> sb : ")  # asynchronous: dashed, open head
        self.assertRegex(capture, r"\n *ing -\[#2E7D32\]-> gha : ")  # reply: dashed
        self.assertRegex(capture, r"\ngha -\[#2E7D32\]> ing : ")  # synchronous
        self.assertRegex(capture, r"\n *ing -\[#6D28D9\]> ing : <i>")  # divergent, implementation only
        for keyword in ("alt", "else", "opt", "loop", "par", "end"):
            self.assertRegex(capture, rf"\n *{keyword}( |\n)")
        self.assertIn("[partial]", capture)
        self.assertIn("== Fan-out to the three subscriptions ==", capture)

    def test_text_is_escaped_and_wrapped(self):
        self.assertEqual(seq.creole("a <b> -- **c**"), "a ~<b> ~-- ~**c~**")
        self.assertEqual(seq.creole("(~2 min)"), "(<U+007E>2 min)")
        source = "GET /api/v1/github-actions/repositories/{repositoryId}/runs/{runId}/report now"
        lines = seq.wrap_text(source, 22)
        self.assertGreater(len(lines), 3)
        self.assertTrue(all(len(line) <= 22 for line in lines), lines)
        self.assertEqual("".join(lines).replace(" ", ""), source.replace(" ", ""))

    def test_guide_lists_every_message_with_state_relationship_and_evidence(self):
        text = seq.guide(self.model, self.ctx, evidence.repositories())
        self.assertIn("no acredita comportamiento en runtime", text)
        for sequence in self.model["sequences"]:
            self.assertIn(f"## {sequence['id']}: {sequence['title']}", text)
            for m in seq.messages(sequence["steps"]):
                for ref in m["evidence"]:
                    self.assertIn(f"`{ref}`", text)
                if not m.get("implementation_only"):
                    self.assertIn(f"`{m['relationship']}`", text)
            for item in sequence["untested"]:
                self.assertIn(item, text)
        rows = [line for line in text.splitlines() if re.match(r"\| \d+ \|", line)]
        self.assertEqual(len(rows), sum(len(seq.messages(s["steps"])) for s in self.model["sequences"]))
        self.assertIn("implementación no modelada", text)


if __name__ == "__main__":
    unittest.main()
