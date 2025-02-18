import logging

def get_managed_prefix_lists(ec2_client, account_id=None):
    """
    Retrieve all managed prefix lists.
    If account_id is provided, only return prefix lists whose OwnerId matches the given account_id.
    
    :param ec2_client: A boto3 EC2 client.
    :param account_id: (Optional) The AWS account ID. If provided, only customer-managed PLs are returned.
    :return: A list of managed prefix list dictionaries.
    """
    logging.info("Retrieving all managed prefix lists...")
    response = ec2_client.describe_managed_prefix_lists()
    prefix_lists = response.get("PrefixLists", [])
    if account_id:
        prefix_lists = [pl for pl in prefix_lists if pl.get("OwnerId") == account_id]
    return prefix_lists

def get_prefix_list_entries(ec2_client, prefix_list_id):
    """
    Retrieve entries for the given prefix list.
    
    :param ec2_client: A boto3 EC2 client.
    :param prefix_list_id: The ID of the prefix list.
    :return: A list of entry dictionaries for the prefix list.
    """
    try:
        response = ec2_client.get_managed_prefix_list_entries(PrefixListId=prefix_list_id)
        return response.get("Entries", [])
    except Exception as e:
        logging.error(f"Error retrieving entries for {prefix_list_id}: {e}")
        return []

