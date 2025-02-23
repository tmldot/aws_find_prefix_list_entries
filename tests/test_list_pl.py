"""
Module: test_list_pl.py
Unit tests for the list_pl module.
"""

import unittest
from modules.list_pl import list_prefix_lists


class DummyEC2Client:  # pylint: disable=too-few-public-methods
    """
    Dummy EC2 client to simulate AWS responses for managed prefix lists.
    """

    def describe_managed_prefix_lists(self):
        """
        Simulate a call to describe_managed_prefix_lists.
        """
        return {
            "PrefixLists": [
                {
                    "PrefixListId": "pl-001",
                    "PrefixListName": "AlphaPL",
                    "OwnerId": "111111111111"
                },
                {
                    "PrefixListId": "pl-002",
                    "PrefixListName": "BetaPL",
                    "OwnerId": "111111111111"
                },
                {
                    "PrefixListId": "pl-003",
                    "PrefixListName": "DeprecatedPL",
                    "OwnerId": "111111111111"
                },
                {
                    "PrefixListId": "pl-004",
                    "PrefixListName": "GammaPL",
                    "OwnerId": "222222222222"
                },
            ]
        }


class TestListPL(unittest.TestCase):
    """
    Unit tests for the list_prefix_lists function in the list_pl module.
    """

    def test_list_prefix_lists_with_filters(self):
        """
        Test listing of prefix lists with inclusion and exclusion filters.
        """
        dummy_client = DummyEC2Client()
        account_id = "111111111111"

        # No filters => should return 3 PLs (pl-001, pl-002, pl-003).
        result = list_prefix_lists(dummy_client, account_id)
        self.assertEqual(
            len(result),
            3,
            "Should find 3 prefix lists for this account."
        )
        # Ensure results are sorted by PL name (case-insensitive).
        sorted_names = list(result.values())
        self.assertEqual(
            sorted_names,
            sorted(sorted_names, key=lambda x: x.lower()),
            "Prefix list names should be sorted alphabetically (case-insensitive)."
        )

        # Include filter "Alpha"
        result_alpha = list_prefix_lists(dummy_client, account_id, pl_filter="Alpha")
        self.assertEqual(
            len(result_alpha),
            1,
            "Should only find 1 prefix list containing 'Alpha'."
        )
        self.assertIn("pl-001", result_alpha)

        # Exclude filter "Deprecated"
        result_exclude = list_prefix_lists(dummy_client, account_id, pl_exclude="Deprecated")
        self.assertEqual(
            len(result_exclude),
            2,
            "Should exclude 'pl-003' from results."
        )
        self.assertNotIn("pl-003", result_exclude)

        # Both filters: include "PL" and exclude "Beta"
        result_both = list_prefix_lists(
            dummy_client,
            account_id,
            pl_filter="PL",
            pl_exclude="Beta"
        )
        self.assertEqual(len(result_both), 2, "Should match AlphaPL and DeprecatedPL.")
        self.assertNotIn("pl-002", result_both)

# Ensure the file ends with a newline

if __name__ == '__main__':
    unittest.main()
