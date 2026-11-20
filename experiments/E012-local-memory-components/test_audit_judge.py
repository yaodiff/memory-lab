import unittest

from audit_judge import is_abstention


class AbstentionTest(unittest.TestCase):
    def test_refusals(self):
        for answer in (
            "UNKNOWN", "unknown.", "**UNKNOWN**", "`UNKNOWN`",
            "UNKNOWN. There is no evidence.",
            "I don't know.", "I can’t answer that question.",
            "Based on the history, I cannot determine the date.",
            "There is insufficient information to answer.",
            "The answer is not available in the history.",
            "Sorry, I don't have enough information.",
            "It is not possible to determine the date.",
        ):
            with self.subTest(answer=answer):
                self.assertTrue(is_abstention(answer))

    def test_answers_are_not_refusals(self):
        for answer in (
            "", "She lives on Unknown Road.", "Unknown Road",
            "I know the answer: Oak.", "The answer is Oak.",
            "I cannot wait to visit Oak.", "No, she moved to Oak.",
        ):
            with self.subTest(answer=answer):
                self.assertFalse(is_abstention(answer))


if __name__ == "__main__":
    unittest.main()
