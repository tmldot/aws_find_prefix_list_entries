import unittest
from modules.list import list_prefix_lists

class DummyEC2Client:
    def describe_managed_prefix_lists(self):
        return {
            "PrefixLists": [
                {"PrefixListId": "pl-001", "PrefixListName": "AlphaPL", "OwnerId": "111111111111"},
                {"PrefixListId": "pl-002", "PrefixListName": "BetaPL", "OwnerId": "111111111111"},
                {"PrefixListId": "pl-003", "PrefixListName": "DeprecatedPL", "OwnerId": "111111111111"},
                {"PrefixListId": "pl-004", "PrefixListName": "GammaPL", "OwnerId": "222222222222"},
            ]
        }

class TestListModule(unittest.TestCase):
    def test_list_prefix_lists_with_filters(self):
        dummy_client = DummyEC2Client()
        account_id = "111111111111"
        # No filters: should return 3 PLs (pl-001, pl-002, pl-003) owned by the account.
        result = list_prefix_lists(dummy_client, account_id)
        self.assertEqual(len(result), 3)
        # Ensure the results are sorted by PL name (AlphaPL, BetaPL, DeprecatedPL)
        sorted_names = list(result.values())
        self.assertEqual(sorted_names, sorted(sorted_names, key=lambda x: x.lower()))
        
        # Include filter "Alpha"
        result2 = list_prefix_lists(dummy_client, account_id, pl_filter="Alpha")
        self.assertEqual(len(result2), 1)
        self.assertIn("pl-001", result2)
        
        # Exclude filter "Deprecated"
        result3 = list_prefix_lists(dummy_client, account_id, pl_exclude="Deprecated")
        self.assertEqual(len(result3), 2)
        self.assertNotIn("pl-003", result3)
        
        # Both filters: include "PL" and exclude "Beta"
        result4 = list_prefix_lists(dummy_client, account_id, pl_filter="PL", pl_exclude="Beta")
        self.assertEqual(len(result4), 2)
        self.assertNotIn("pl-002", result4)

if __name__ == '__main__':
    unittest.main()

