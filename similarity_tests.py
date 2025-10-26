import unittest
import pandas as pd
from similarity_functions import process, compute_similarity

DEVELOPER_NAME = "John Smith"
DEVELOPER_EMAIL = "john@example.com"

class TestProcess(unittest.TestCase):
    def test_basic_name(self):
        _, first, last, i_first, i_last, _, prefix = process((DEVELOPER_NAME, DEVELOPER_EMAIL))
        self.assertEqual(first, "john")
        self.assertEqual(last, "smith")
        self.assertEqual(i_first, "j")
        self.assertEqual(i_last, "s")
        self.assertEqual(prefix, "john")

    def test_name_with_accents(self):
        _, first, last, *_ = process(("Tomás Arribas", "tomas.arribas@buenostalleres.com")) 
        self.assertEqual(first, "tomas")
        self.assertEqual(last, "arribas")

    def test_single_word_name(self):
        _, first, last, *_ = process(("john", DEVELOPER_EMAIL)) 
        self.assertEqual(first, "john")
        self.assertEqual(last, "")

    def test_remove_punctuation(self):
        name, *_ = process(("al //", "@idest,cmdoptesc@users.noreply.github.com"))
        self.assertEqual(name, "al")

    def test_many_spaces(self):
        _, first, last, *_ = process(("john tomas arribas", "tomas.arribas@buenostalleres.com")) 
        self.assertEqual(first, "john")
        self.assertEqual(last, "tomas arribas")


class TestComputeSimilarity(unittest.TestCase):
    def test_detects_similar_names(self):
        devs = [
            (DEVELOPER_NAME, DEVELOPER_EMAIL),
            ("Jon Smith", "j@example.com")
        ]
        df = compute_similarity(devs, t=0.9)
        self.assertFalse(df.empty)
        self.assertIn("c1", df.columns)
        self.assertGreater(df.iloc[0]["c1"], 0.9)

    def test_identical_emails(self):
        devs = [
            (DEVELOPER_NAME, DEVELOPER_EMAIL),
            (DEVELOPER_NAME, DEVELOPER_EMAIL)  # identical email
        ]
        df = compute_similarity(devs)
        self.assertTrue(df.empty)

    def test_not_common_prefix_allows_email_rules(self):
        devs = [
            (DEVELOPER_NAME, DEVELOPER_EMAIL),
            (DEVELOPER_NAME, "jsmith@example.com")
        ]
        df = compute_similarity(devs, t=0.9)
        self.assertFalse(df.empty)
        self.assertIn("c4", df.columns)
        self.assertIn("c5", df.columns)

    def test_common_prefix_blocks_email_rules(self):
        devs = [
            (DEVELOPER_NAME, "me@example.com"),
            ("John S.", DEVELOPER_EMAIL)
        ]
        df = compute_similarity(devs, t=0.9)
        self.assertTrue(df.empty)


if __name__ == "__main__":
    unittest.main()
