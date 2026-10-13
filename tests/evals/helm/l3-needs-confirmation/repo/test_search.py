import unittest

from search import search

ARTICLES = [
    {"title": "Python Packaging", "tags": ["python"], "saved": "2026-08-02"},
    {"title": "Packaging Rust crates", "tags": ["rust"], "saved": "2026-09-14"},
]


class SearchTests(unittest.TestCase):
    def test_title_match_ignores_case(self):
        self.assertEqual(len(search(ARTICLES, "packaging")), 2)

    def test_tag_narrows_results(self):
        self.assertEqual(search(ARTICLES, "packaging", tag="rust"), [ARTICLES[1]])


if __name__ == "__main__":
    unittest.main()
