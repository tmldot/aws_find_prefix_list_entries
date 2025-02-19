import logging
from collections import OrderedDict
from modules.aws_helpers import get_managed_prefix_lists

def list_prefix_lists(ec2_client, account_id, pl_filter=None, pl_exclude=None):
    """
    Retrieves and filters customer-managed prefix lists based on inclusion and exclusion filters,
    and returns them sorted by prefix list name (case-insensitive).

    :param ec2_client: A boto3 EC2 client.
    :param account_id: The AWS account ID. Only prefix lists with OwnerId equal to this value will be returned.
    :param pl_filter: Optional inclusion filter. Only include PLs whose name contains this substring (case-insensitive).
    :param pl_exclude: Optional exclusion filter. Exclude PLs whose name contains this substring (case-insensitive).
    :return: An OrderedDict mapping PrefixListId to PrefixListName, sorted by PLName.
    """
    logging.info("Retrieving all managed prefix lists...")
    response = ec2_client.describe_managed_prefix_lists()
    prefix_lists = response.get("PrefixLists", [])
    pl_details = {}
    for pl in prefix_lists:
        pl_id = pl.get("PrefixListId")
        pl_name = pl.get("PrefixListName", "N/A")
        # Only include if prefix list exists and is customer-managed
        if not pl_id:
            continue
        if account_id and pl.get("OwnerId") != account_id:
            continue
        if pl_filter and pl_filter.lower() not in pl_name.lower():
            continue
        if pl_exclude and pl_exclude.lower() in pl_name.lower():
            continue
        pl_details[pl_id] = pl_name

    if not pl_details:
        logging.error("No customer-managed prefix lists found matching criteria.")
        return {}
    
    # Sort the prefix lists by prefix list name (case-insensitive)
    sorted_pls = OrderedDict(sorted(pl_details.items(), key=lambda x: x[1].lower()))
    return sorted_pls

