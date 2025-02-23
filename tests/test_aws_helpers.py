"""
Module: test_aws_helpers.py
Unit tests for the aws_helpers module.
"""

import unittest

# Ensure that 'botocore' is installed in your environment so Pylint can see it:
#   pip install botocore
from botocore.exceptions import ClientError

from modules.aws_helpers import (
    get_managed_prefix_lists,
    filter_prefix_lists,
    get_prefix_list_entries
)


class DummyEC2Client:
    """
    Dummy EC2 client to simulate AWS responses for managed prefix lists
    and entries.
    """

    def describe_managed_prefix_lists(self):
        """
        Simulate a call to describe_managed_prefix_lists.
        """
        return {
            "PrefixLists": [
                {"PrefixListId": "pl-123", "PrefixListName": "TestPL",
                 "OwnerId": "111111111111"},
                {"PrefixListId": "pl-456", "PrefixListName": "VendorPL",
                 "OwnerId": "222222222222"},
                {"PrefixListId": "pl-789", "PrefixListName": "AnotherPL",
                 "OwnerId": "111111111111"},
            ]
        }

    def get_managed_prefix_list_entries(self, prefix_list_id):
        """
        Simulate a call to get_managed_prefix_list_entries for a given prefix_list_id.
        """
        if prefix_list_id == "pl-123":
            return {
                "Entries": [
                    {"Cidr": "192.168.0.0/16", "Description": "Test Range"},
                    {"Cidr": "10.0.0.0/8", "Description": "Corporate Range"},
                ]
            }
        if prefix_list_id == "pl-456":
            return {"Entries": []}
        # Simulate a not-found error
        raise ClientError(
            {
                "Error": {
                    "Code": "InvalidPrefixListID.NotFound",
                    "Message": "PrefixList not found"
                }
            },
            "GetManagedPrefixListEntries"
        )


class TestAWSHelpers(unittest.TestCase):
    """
    Unit tests for AWS helper functions in aws_helpers.py.
    """

    def test_get_managed_prefix_lists_with_account_id(self):
        """
        Test that only prefix lists with the matching OwnerId are returned.
        """
        dummy_client = DummyEC2Client()
        result = get_managed_prefix_lists(dummy_client, account_id="111111111111")
        self.assertEqual(len(result), 2, "Should find 2 matching prefix lists.")
        for pl_item in result:
            self.assertEqual(pl_item.get("OwnerId"), "111111111111")

    def test_get_managed_prefix_lists_without_account_id(self):
        """
        Test that all prefix lists are returned when no account_id is provided.
        """
        dummy_client = DummyEC2Client()
        result = get_managed_prefix_lists(dummy_client)
        self.assertEqual(len(result), 3, "Should find 3 total prefix lists.")

    def test_filter_prefix_lists(self):
        """
        Test the filter_prefix_lists function with inclusion and exclusion filters.
        """
        data = [
            {
                "PrefixListId": "pl-123",
                "PrefixListName": "TestPL",
                "OwnerId": "111111111111"
            },
            {
                "PrefixListId": "pl-456",
                "PrefixListName": "VendorPL",
                "OwnerId": "222222222222"
            },
            {
                "PrefixListId": "pl-789",
                "PrefixListName": "AnotherPL",
                "OwnerId": "111111111111"
            },
        ]
        included = filter_prefix_lists(data, pl_filter="Test")
        self.assertEqual(len(included), 1, "Should find 1 matching 'Test' prefix list.")
        self.assertEqual(included[0]["PrefixListId"], "pl-123")

        excluded = filter_prefix_lists(data, pl_exclude="Vendor")
        self.assertEqual(len(excluded), 2, "Should exclude the VendorPL prefix list.")
        self.assertNotIn(
            "pl-456",
            [pl_item["PrefixListId"] for pl_item in excluded],
            "VendorPL should be excluded."
        )

        both = filter_prefix_lists(data, pl_filter="PL", pl_exclude="Another")
        # 'PL' matches all (TestPL, VendorPL, AnotherPL), exclude 'Another' => 2 left
        self.assertEqual(len(both), 2, "Should match TestPL and VendorPL.")
        self.assertNotIn(
            "pl-789",
            [pl_item["PrefixListId"] for pl_item in both],
            "AnotherPL should be excluded."
        )

    def test_get_prefix_list_entries_valid(self):
        """
        Test retrieving prefix list entries for a valid prefix list ID (pl-123).
        """
        dummy_client = DummyEC2Client()
        entries = get_prefix_list_entries(dummy_client, "pl-123")
        self.assertEqual(len(entries), 2, "Should return 2 entries for pl-123.")

    def test_get_prefix_list_entries_empty(self):
        """
        Test retrieving prefix list entries for a prefix list (pl-456) with no entries.
        """
        dummy_client = DummyEC2Client()
        entries = get_prefix_list_entries(dummy_client, "pl-456")
        self.assertEqual(len(entries), 0, "Should return 0 entries for pl-456.")

    def test_get_prefix_list_entries_invalid(self):
        """
        Test retrieving prefix list entries for an invalid prefix list (pl-999).
        Should gracefully handle ClientError and return [].
        """
        dummy_client = DummyEC2Client()
        entries = get_prefix_list_entries(dummy_client, "pl-999")
        self.assertEqual(
            len(entries), 0,
            "Should return an empty list for invalid prefix list IDs."
        )


if __name__ == '__main__':
    unittest.main()

