import unittest

from cli import parse_args


class ParseArgsTests(unittest.TestCase):
    def test_title_is_the_positional_argument(self):
        self.assertEqual(parse_args(["Hello, World!"]).title, "Hello, World!")


if __name__ == "__main__":
    unittest.main()
