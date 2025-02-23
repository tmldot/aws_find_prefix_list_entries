"""
Module: test_audit_pl.py
Unit tests for the audit_pl module.
"""

import unittest
from modules.audit_pl import filter_large_cidr_entries


class TestAuditPL(unittest.TestCase):
    """Unit tests for the filter_large_cidr_entries function in audit_pl.py."""

    def test_filter_large_cidr_entries_default(self):
        """
        Test filtering with maxcidr=29 (should return entries with /28 or /24).
        """
        entries = [
            {'Cidr': '192.168.1.0/24'},
            {'Cidr': '10.0.0.0/29'},
            {'Cidr': '172.16.0.0/28'},
            {'Cidr': '8.8.8.8/32'},
        ]
        result = filter_large_cidr_entries(entries, 29)
        self.assertEqual(len(result), 2, "Should match /24 and /28 only.")

    def test_filter_large_cidr_entries_with_lower_max(self):
        """
        Test filtering with maxcidr=28 (should return only /24 block).
        """
        entries = [
            {'Cidr': '192.168.1.0/24'},
            {'Cidr': '10.0.0.0/29'},
            {'Cidr': '172.16.0.0/28'},
            {'Cidr': '8.8.8.8/32'},
        ]
        result = filter_large_cidr_entries(entries, 28)
        self.assertEqual(len(result), 1, "Should only match the /24 block.")


if __name__ == '__main__':
    unittest.main()