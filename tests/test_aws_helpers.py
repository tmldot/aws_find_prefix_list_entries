import unittest
from modules.aws_helpers import get_managed_prefix_lists

class DummyEC2Client:
    def describe_managed_prefix_lists(self):
        return {
            "PrefixLists": [
                {"PrefixListId": "pl-123", "PrefixListName": "TestPL", "OwnerId": "111111111111"},
                {"PrefixListId": "pl-456", "PrefixListName": "VendorPL", "OwnerId": "222222222222"},
                {"PrefixListId": "pl-789", "PrefixListName": "AnotherPL", "OwnerId": "111111111111"},
            ]
        }

class TestAWSHelpers(unittest.TestCase):
    def test_get_managed_prefix_lists_with_account_id(self):
        dummy_client = DummyEC2Client()
        # Only prefix lists with OwnerId "111111111111" should be returned.
        result = get_managed_prefix_lists(dummy_client, account_id="111111111111")
        self.assertEqual(len(result), 2)
        for pl in result:
            self.assertEqual(pl.get("OwnerId"), "111111111111")

    def test_get_managed_prefix_lists_without_account_id(self):
        dummy_client = DummyEC2Client()
        result = get_managed_prefix_lists(dummy_client)
        self.assertEqual(len(result), 3)

if __name__ == '__main__':
    unittest.main()

