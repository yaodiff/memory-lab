import hashlib
import json
import unittest
from collections import Counter

from fixture import cases
from retrieval import CONFIG, assemble_panel, diffuse, find_anchor, grounded_edges, legacy, rrf


class FrozenMechanics(unittest.TestCase):
    def test_fixture_matches_frozen_hash(self):
        fixture = cases()
        payload = json.dumps(fixture, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        self.assertTrue(hashlib.sha256(payload.encode()).hexdigest().startswith(CONFIG["fixture_sha256"]))
        self.assertEqual(set(Counter(c["stratum"] for c in fixture).values()), {30})
        self.assertEqual(len({c["id"] for c in fixture}), 120)

    def test_every_traversed_edge_requires_exact_source(self):
        case = cases()[0]
        self.assertTrue(all(link["source"] for link in case["edges"][:-1]))
        self.assertEqual(len(list(grounded_edges(case))), len(case["edges"]) - 1)
        first = case["edges"][0]
        case["sources"][first["source"]] = [first["b"], first["kind"], first["a"]]
        self.assertEqual(len(list(grounded_edges(case))), len(case["edges"]) - 2)

    def test_seeds_and_inverses_obey_legacy_types(self):
        case = {"pages": {uid: {"kind": kind} for uid, kind in
                          (("a", "entity"), ("b", "entity"), ("c", "note"), ("d", "note"))}}
        edges = [("b", "part-of", "a"), ("a", "attachment", "c"), ("a", "implements", "d")]
        added, boost, seeds = legacy(case, ["a"], {"a": 1}, edges, set())
        self.assertEqual((added, boost, seeds), (["a", "b"], ["a", "b"], ["a"]))
        self.assertEqual(legacy(case, ["a"], {"a": 1}, edges, {"a"})[0], ["a"])

    def test_fusion_and_second_hop(self):
        self.assertGreater(rrf(["a", "b"], ["b"])["b"], rrf(["a", "b"], ["b"])["a"])
        self.assertIn("c", diffuse(["a"], [("a", "attachment", "b"), ("b", "semantic", "c")]))

    def test_panel_preserves_global_and_abstains_on_ambiguous_context(self):
        baseline = list("abcdefg")
        self.assertEqual(assemble_panel(baseline, ["b", "x"], 6), list("abcxde"))
        self.assertEqual(baseline, list("abcdefg"))
        self.assertIsNone(find_anchor(cases()[3]))
        case = cases()[0]
        owner = case["target_entity"]
        self.assertEqual(find_anchor(case), owner)
        another = next(page for uid, page in case["pages"].items()
                       if uid != owner and page["kind"] == "entity")
        another["aliases"] = case["pages"][owner]["aliases"].copy()
        self.assertIsNone(find_anchor(case))


if __name__ == "__main__":
    unittest.main()
