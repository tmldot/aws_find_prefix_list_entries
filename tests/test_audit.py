import unittest
from modules.audit import filter_large_cidr_entries

class TestAudit(unittest.TestCase):
    def test_filter_large_cidr_entries(self):
        entries = [
            {'Cidr': '192.168.1.0/24'},
            {'Cidr': '10.0.0.0/29'},
            {'Cidr': '172.16.0.0/28'},
            {'Cidr': '8.8.8.8/32'},
        ]
        # For maxcidr of 29, entries with prefix lengths less than 29 should be returned.
        result = filter_large_cidr_entries(entries, 29)
        self.assertEqual(len(result), 2)
        # For maxcidr of 28, only the /24 block qualifies.
        result2 = filter_large_cidr_entries(entries, 28)
        self.assertEqual(len(result2), 1)

if __name__ == '__main__':
    unittest.main()

