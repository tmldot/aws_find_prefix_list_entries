"""
Module: test_search_pl.py
Unit tests for the search_pl module.
"""

import unittest
from modules.search_pl import search_entries_by_field


class TestSearchPL(unittest.TestCase):
    """Unit tests for the search_entries_by_field function in search_pl.py."""

    def test_search_entries_by_field_description(self):
        """
        Test searching entries by the 'Description' field (case-insensitive).
        """
        entries = [
            {'Description': 'ExampleVendor network block', 'Cidr': '192.168.1.0/24'},
            {'Description': 'Another network block', 'Cidr': '10.0.0.0/24'},
            {'Description': 'examplevendor internal', 'Cidr': '172.16.0.0/16'},
            {'Description': 'Not related', 'Cidr': '8.8.8.0/24'},
        ]
        result = search_entries_by_field(entries, "examplevendor", "Description")
        self.assertEqual(len(result), 2, "Should find 2 matches for 'examplevendor'.")

    def test_search_entries_by_field_cidr(self):
        """
        Test searching entries by the 'Cidr' field (supports partial match).
        """
        entries = [
            {'Description': 'Network A', 'Cidr': '192.168.1.0/24'},
            {'Description': 'Network B', 'Cidr': '10.0.0.0/29'},
            {'Description': 'Network C', 'Cidr': '172.16.0.0/28'},
            {'Description': 'Network D', 'Cidr': '8.8.8.8/32'},
        ]
        result = search_entries_by_field(entries, "10.0", "Cidr")
        self.assertEqual(len(result), 1, "Should find exactly 1 match for '10.0'.")

if __name__ == '__main__':
    unittest.main()
