import unittest
from modules.audit import filter_large_cidr_entries

class TestAudit(unittest.TestCase):
    def test_filter_large_cidr_entries_default(self):
        # With maxcidr = 29, entries with prefix lengths less than 29 should be returned.
        entries = [
            {'Cidr': '192.168.1.0/24'},
            {'Cidr': '10.0.0.0/29'},
            {'Cidr': '172.16.0.0/28'},
            {'Cidr': '8.8.8.8/32'},
        ]
        result = filter_large_cidr_entries(entries, 29)
        self.assertEqual(len(result), 2)  # /24 and /28 should match

    def test_filter_large_cidr_entries_with_lower_max(self):
        # With maxcidr = 28, only the /24 block qualifies.
        entries = [
            {'Cidr': '192.168.1.0/24'},
            {'Cidr': '10.0.0.0/29'},
            {'Cidr': '172.16.0.0/28'},
            {'Cidr': '8.8.8.8/32'},
        ]
        result = filter_large_cidr_entries(entries, 28)
        self.assertEqual(len(result), 1)  # Only /24 qualifies

if __name__ == '__main__':
    unittest.main()

