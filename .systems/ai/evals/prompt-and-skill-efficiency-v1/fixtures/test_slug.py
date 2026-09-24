import unittest

from slug import slugify


class SlugifyTests(unittest.TestCase):
    def test_normalizes_words_and_punctuation(self):
        self.assertEqual(slugify("  Alpha, Beta!!  "), "alpha-beta")

    def test_collapses_separators(self):
        self.assertEqual(slugify("Alpha___ Beta"), "alpha-beta")


if __name__ == "__main__":
    unittest.main()
