import unittest
import pandas as pd
from similarity_functions import process, compute_similarity

class TestProcess(unittest.TestCase):
    def test_basic_name(self):
        name, first, last, i_first, i_last, email, prefix = process(("John Smith", "john@example.com"))
        self.assertEqual(first, "john")
        self.assertEqual(last, "smith")
        self.assertEqual(i_first, "j")
        self.assertEqual(i_last, "s")
        self.assertEqual(prefix, "john")

    def test_name_with_accents(self):
        name, first, last, *_ = process(("Tomás Arribas", "tomas.arribas@buenostalleres.com")) 
        self.assertEqual(first, "tomas")
        self.assertEqual(last, "arribas")

    def test_single_word_name(self):
        _, first, last, *_ = process(("john", "john@example.com")) 
        self.assertEqual(first, "john")
        self.assertEqual(last, "")

    def test_remove_punctuation(self):
        name, *_ = process(("al //", "@idest,cmdoptesc@users.noreply.github.com"))
        self.assertEqual(name, "al")

    def test_many_spaces(self):
        name, first, last, *_ = process(("john tomas arribas", "tomas.arribas@buenostalleres.com")) 
        self.assertEqual(first, "john")
        self.assertEqual(last, "tomas arribas")

class TestComputeSimilarity(unittest.TestCase):
    def test_detects_similar_names(self):
        devs = [
            ("John Smith", "john@example.com"),
            ("Jon Smith", "j@example.com")
        ]
        df = compute_similarity(devs, t=0.9)
        self.assertFalse(df.empty)
        self.assertIn("c1", df.columns)
        self.assertGreater(df.iloc[0]["c1"], 0.9)

    def test_identical_emails(self):
        devs = [
            ("John Smith", "john@example.com"),
            ("John Smith", "john@example.com")  # identical email
        ]
        df = compute_similarity(devs)
        self.assertTrue(df.empty)

   
    def test_not_common_prefix_allows_email_rules(self):
        devs = [
            ("John Smith", "john@example.com"),
            ("John Smith", "jsmith@example.com")
        ]
        df = compute_similarity(devs, t=0.9)
        # email-based match (prefix contains initial + lastname) should trigger inclusion
        self.assertFalse(df.empty)
        self.assertIn("c4", df.columns)
        self.assertIn("c5", df.columns)

    def test_common_prefix_blocks_email_rules(self):
        devs = [
            ("John Smith", "me@example.com"),       # common prefix
            ("John S.", "john@example.com")       # not common prefix
        ]
        df = compute_similarity(devs, t=0.9)
        # email/initial rules should not apply because one prefix is common
        # but name similarity is below threshold -> no pair
        self.assertTrue(df.empty)

if __name__ == "__main__":
    unittest.main()
