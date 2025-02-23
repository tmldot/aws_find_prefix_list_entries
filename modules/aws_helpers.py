"""
Module: aws_helpers.py

Provides helper functions to interact with AWS Managed Prefix Lists and
handle AWS session setup and prefix list filtering.
"""

import logging
import boto3
from botocore.exceptions import ClientError
from typing import Any, Dict, List, Optional

# A dict type for storing AWS prefix list data
PrefixListDict = Dict[str, Any]


def get_ec2_client_and_account(
    profile: Optional[str] = None,
    region: Optional[str] = None
):
    """
    Create a boto3 Session, then return the EC2 client and the AWS
    account ID for the caller.

    :param profile: (Optional) AWS CLI profile name.
    :param region: (Optional) AWS region name.
    :return: (ec2_client, account_id) tuple.
    :raises Exception: if unable to create clients or retrieve account info.
    """
    session_kwargs = {}
    if profile:
        session_kwargs["profile_name"] = profile
    if region:
        session_kwargs["region_name"] = region

    try:
        session = boto3.Session(**session_kwargs)
        ec2_client = session.client("ec2")
        sts_client = session.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
        return ec2_client, account_id
    except Exception as exc:
        logging.error("Failed to set up AWS clients or retrieve account ID: %s", exc)
        raise


def get_managed_prefix_lists(
    ec2_client,
    account_id: Optional[str] = None
) -> List[PrefixListDict]:
    """
    Retrieve all managed prefix lists. If account_id is provided,
    only return prefix lists whose OwnerId matches the given account_id.

    :param ec2_client: A boto3 EC2 client.
    :param account_id: (Optional) AWS account ID to filter for customer-managed PLs.
    :return: A list of prefix list dictionaries.
    """
    logging.info("Retrieving all managed prefix lists...")
    try:
        response = ec2_client.describe_managed_prefix_lists()
    except ClientError as c_err:
        logging.error("Error calling describe_managed_prefix_lists: %s", c_err)
        return []

    prefix_lists = response.get("PrefixLists", [])
    if account_id:
        prefix_lists = [
            pl for pl in prefix_lists if pl.get("OwnerId") == account_id
        ]
    return prefix_lists


def filter_prefix_lists(
    prefix_lists: List[PrefixListDict],
    pl_filter: Optional[str] = None,
    pl_exclude: Optional[str] = None
) -> List[PrefixListDict]:
    """
    Filters a list of prefix-list dictionaries based on optional inclusion
    and exclusion criteria.

    :param prefix_lists: List of prefix list dictionaries from AWS.
    :param pl_filter: Optional string; only include PLs whose name contains this.
    :param pl_exclude: Optional string; exclude PLs whose name contains this.
    :return: Filtered list of prefix list dictionaries.
    """
    filtered = []
    for pl in prefix_lists:
        pl_name = pl.get("PrefixListName", "N/A")
        if pl_filter and pl_filter.lower() not in pl_name.lower():
            continue
        if pl_exclude and pl_exclude.lower() in pl_name.lower():
            continue
        filtered.append(pl)
    return filtered


def get_prefix_list_entries(
    ec2_client,
    prefix_list_id: str
) -> List[PrefixListDict]:
    """
    Retrieve entries for the specified prefix list.

    :param ec2_client: A boto3 EC2 client.
    :param prefix_list_id: The prefix list ID.
    :return: A list of prefix list entry dictionaries.
    """
    try:
        response = ec2_client.get_managed_prefix_list_entries(
            PrefixListId=prefix_list_id
        )
        return response.get("Entries", [])
    except ClientError as exc:
        logging.error("Error retrieving entries for %s: %s", prefix_list_id, exc)
        return []