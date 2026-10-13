import unittest

from export import export_orders


class ExportOrdersTests(unittest.TestCase):
    def test_header_only_without_orders(self):
        self.assertEqual(export_orders([]), "id,customer,note\n")

    def test_one_row_per_order(self):
        orders = [
            {"id": 1, "customer": "Ada", "note": "gift"},
            {"id": 2, "customer": "Lin", "note": "rush"},
        ]
        self.assertEqual(
            export_orders(orders),
            "id,customer,note\n1,Ada,gift\n2,Lin,rush\n",
        )


if __name__ == "__main__":
    unittest.main()
