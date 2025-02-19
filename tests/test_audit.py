"""
Module: test_audit.py
Unit tests for the audit module.
"""

import unittest
from modules.audit import filter_large_cidr_entries

class TestAudit(unittest.TestCase):
    """Unit tests for the filter_large_cidr_entries function."""

    def test_filter_large_cidr_entries_default(self):
        """Test filtering with maxcidr set to 29 (should return /24 and /28 blocks)."""
        entries = [
            {'Cidr': '192.168.1.0/24'},
            {'Cidr': '10.0.0.0/29'},
            {'Cidr': '172.16.0.0/28'},
            {'Cidr': '8.8.8.8/32'},
        ]
        result = filter_large_cidr_entries(entries, 29)
        self.assertEqual(len(result), 2)

    def test_filter_large_cidr_entries_with_lower_max(self):
        """Test filtering with maxcidr set to 28 (should return only the /24 block)."""
        entries = [
            {'Cidr': '192.168.1.0/24'},
            {'Cidr': '10.0.0.0/29'},
            {'Cidr': '172.16.0.0/28'},
            {'Cidr': '8.8.8.8/32'},
        ]
        result = filter_large_cidr_entries(entries, 28)
        self.assertEqual(len(result), 1)

if __name__ == '__main__':
    unittest.main()