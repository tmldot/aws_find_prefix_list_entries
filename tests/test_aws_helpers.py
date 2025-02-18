import unittest
from modules.aws_helpers import get_managed_prefix_lists

class DummyEC2Client:
    def describe_managed_prefix_lists(self):
        return {
            "PrefixLists": [
                {"PrefixListId": "pl-123", "PrefixListName": "TestPL"},
                {"PrefixListId": "pl-456", "PrefixListName": "AnotherPL"},
            ]
        }

class TestAWSHelpers(unittest.TestCase):
    def test_get_managed_prefix_lists(self):
        dummy_client = DummyEC2Client()
        result = get_managed_prefix_lists(dummy_client)
        self.assertEqual(len(result), 2)

if __name__ == '__main__':
    unittest.main()

