"""
Module: aws_helpers.py
Provides helper functions to interact with AWS Managed Prefix Lists.
"""

import logging
from botocore.exceptions import ClientError

def get_managed_prefix_lists(ec2_client, account_id=None):
    """
    Retrieve all managed prefix lists. If account_id is provided,
    only return prefix lists whose OwnerId matches the given account_id.

    :param ec2_client: A boto3 EC2 client.
    :param account_id: (Optional) AWS account ID to filter for customer-managed PLs.
    :return: List of prefix list dictionaries.
    """
    logging.info("Retrieving all managed prefix lists...")
    response = ec2_client.describe_managed_prefix_lists()
    prefix_lists = response.get("PrefixLists", [])
    if account_id:
        prefix_lists = [pl for pl in prefix_lists if pl.get("OwnerId") == account_id]
    return prefix_lists

def get_prefix_list_entries(ec2_client, prefix_list_id):
    """
    Retrieve entries for the specified prefix list.

    :param ec2_client: A boto3 EC2 client.
    :param prefix_list_id: The prefix list ID.
    :return: List of prefix list entry dictionaries.
    """
    try:
        response = ec2_client.get_managed_prefix_list_entries(PrefixListId=prefix_list_id)
        return response.get("Entries", [])
    except ClientError as e:
        logging.error("Error retrieving entries for %s: %s", prefix_list_id, e)
        return []