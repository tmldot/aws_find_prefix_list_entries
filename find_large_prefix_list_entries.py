#!/usr/bin/env python3
"""
Description:
    Searches all customer-managed AWS Managed Prefix List entries for any IP block larger than a /29.
    A block is considered larger than /29 if its prefix length is less than 29 (e.g., /28, /27, etc.).

    The script only processes prefix lists owned by the current AWS account.
    Optionally, you can include only those prefix lists whose name contains a specific string using the --plfilter parameter,
    and/or exclude those whose name contains a specific string using the --plexclude parameter.

    The report is printed to the console and can optionally be saved as a CSV file.

Usage:
    python find_large_prefix_list_entries.py [--csv [filename]] [--profile PROFILE]
        [--region REGION] [--quiet] [--plfilter FILTER] [--plexclude EXCLUDE]

    --csv: Optionally output the report to a CSV file. If no filename is provided, a default one is generated.
    --profile: AWS CLI profile to use.
    --region: AWS region to use.
    --quiet: Suppress intermediate console output (only critical messages are shown).
    --plfilter: Only include prefix lists whose name contains this string (case-insensitive).
    --plexclude: Exclude prefix lists whose name contains this string (case-insensitive).

Requirements:
    - Python 3.6+
    - boto3 (install via `pip install boto3`)
    - ipaddress (built-in for Python 3.3+)
"""

import boto3
import argparse
import logging
import sys
import csv
from datetime import datetime
import ipaddress

def setup_logging(quiet=False):
    """
    Set up logging to file and console.
    The log file is named 'large_prefix_entries-YYYYMMDD_HHmmss.log'
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = f"large_prefix_entries-{timestamp}.log"
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO)
    
    ch = logging.StreamHandler(sys.stdout)
    if quiet:
        ch.setLevel(logging.CRITICAL)
    else:
        ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    logging.info(f"Logging initiated. Output log file: {logfile}")
    return logfile

def get_prefix_list_details(ec2_client, account_id, pl_filter=None, pl_exclude=None):
    """
    Retrieves all managed prefix lists and returns a dictionary mapping
    PrefixListId to PrefixListName for customer-managed lists only.
    Optionally includes only those prefix lists whose name contains the provided filter string (pl_filter)
    and/or excludes those whose name contains the provided exclusion string (pl_exclude). Both comparisons
    are case-insensitive.
    
    :param ec2_client: A boto3 EC2 client.
    :param account_id: The current AWS account ID.
    :param pl_filter: Optional filter string to include only prefix lists whose name contains this substring.
    :param pl_exclude: Optional exclusion string to omit prefix lists whose name contains this substring.
    :return: Dictionary with key as PrefixListId and value as PrefixListName.
    """
    logging.info("Retrieving all managed prefix lists...")
    response = ec2_client.describe_managed_prefix_lists()
    prefix_lists = response.get("PrefixLists", [])
    pl_details = {}
    for pl in prefix_lists:
        pl_id = pl.get("PrefixListId")
        pl_name = pl.get("PrefixListName", "N/A")
        owner_id = pl.get("OwnerId", "")
        if not pl_id:
            continue
        # Only include customer-managed lists (OwnerId equals our account id)
        if owner_id != account_id:
            continue
        # If a filter is provided, only include PLs whose name contains the filter string.
        if pl_filter and pl_filter.lower() not in pl_name.lower():
            continue
        # If an exclusion term is provided, skip PLs whose name contains that string.
        if pl_exclude and pl_exclude.lower() in pl_name.lower():
            continue
        pl_details[pl_id] = pl_name

    if not pl_details:
        logging.error("No customer-managed prefix lists found matching criteria.")
    else:
        logging.info(f"Found {len(pl_details)} customer-managed prefix list(s) matching criteria.")
    return pl_details

def search_large_prefix_entries(ec2_client, prefix_list_id):
    """
    For a given prefix list, retrieves entries and filters those with an IP block larger than /29.
    Returns a list of matching entries.
    """
    logging.info(f"Processing prefix list: {prefix_list_id}")
    try:
        response = ec2_client.get_managed_prefix_list_entries(PrefixListId=prefix_list_id)
    except Exception as e:
        logging.error(f"Error retrieving entries for {prefix_list_id}: {e}")
        return []
    
    entries = response.get("Entries", [])
    matching_entries = []
    for entry in entries:
        cidr = entry.get("Cidr")
        if cidr:
            try:
                network = ipaddress.ip_network(cidr, strict=False)
                if network.prefixlen < 29:
                    matching_entries.append(entry)
            except ValueError as ve:
                logging.error(f"Invalid CIDR '{cidr}' in prefix list {prefix_list_id}: {ve}")
    
    if matching_entries:
        logging.info(f"Found {len(matching_entries)} matching entry(ies) in {prefix_list_id}")
    else:
        logging.info(f"No matching entries in {prefix_list_id}")
    return matching_entries

def print_report(results_summary, pl_details):
    """
    Prints a summary report to the console.
    """
    report_lines = []
    report_lines.append("\nFINAL REPORT: IP blocks larger than /29")
    report_lines.append("=" * 60)
    
    if not results_summary:
        report_lines.append("No matching entries found in any customer-managed prefix lists.")
    else:
        for pl_id, entries in results_summary.items():
            pl_name = pl_details.get(pl_id, "N/A")
            header = f"{pl_id} | {pl_name} | {len(entries)} matching entr{'y' if len(entries)==1 else 'ies'}"
            report_lines.append(header)
            for entry in entries:
                cidr = entry.get("Cidr", "N/A")
                description = entry.get("Description", "N/A")
                report_lines.append(f"  {cidr} | {description}")
            report_lines.append("-" * 60)
    
    for line in report_lines:
        logging.info(line)
    print("\n".join(report_lines))

def write_csv_report(results_summary, pl_details, csv_filename):
    """
    Writes the final report to a CSV file with columns:
      PLID, PLName, Cidr, Description
    """
    header = ["PLID", "PLName", "Cidr", "Description"]
    try:
        with open(csv_filename, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            for pl_id, entries in results_summary.items():
                pl_name = pl_details.get(pl_id, "N/A")
                for entry in entries:
                    cidr = entry.get("Cidr", "N/A")
                    description = entry.get("Description", "N/A")
                    writer.writerow([pl_id, pl_name, cidr, description])
        logging.info(f"CSV report written to {csv_filename}")
    except Exception as e:
        logging.error(f"Failed to write CSV report: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Search customer-managed AWS Managed Prefix Lists for IP blocks larger than /29."
    )
    parser.add_argument("--csv", nargs="?", const=True, help="Output CSV report. Optionally specify a filename.")
    parser.add_argument("--profile", help="AWS CLI profile to use")
    parser.add_argument("--region", help="AWS region to use")
    parser.add_argument("--quiet", action="store_true", help="Suppress intermediate console output")
    parser.add_argument("--plfilter", help="Only include prefix lists whose name contains this string (case-insensitive)")
    parser.add_argument("--plexclude", help="Exclude prefix lists whose name contains this string (case-insensitive)")
    
    args = parser.parse_args()
    
    setup_logging(quiet=args.quiet)
    
    session_kwargs = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile
    if args.region:
        session_kwargs["region_name"] = args.region
    session = boto3.Session(**session_kwargs)
    
    try:
        ec2_client = session.client("ec2")
    except Exception as e:
        logging.error(f"Failed to create EC2 client: {e}")
        sys.exit(1)
    
    try:
        sts_client = session.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
    except Exception as e:
        logging.error(f"Failed to get AWS account ID: {e}")
        sys.exit(1)
    
    pl_details = get_prefix_list_details(ec2_client, account_id, pl_filter=args.plfilter, pl_exclude=args.plexclude)
    if not pl_details:
        sys.exit(1)
    
    results_summary = {}
    for pl_id in pl_details:
        matching_entries = search_large_prefix_entries(ec2_client, pl_id)
        if matching_entries:
            results_summary[pl_id] = matching_entries
        logging.info("-" * 60)
    
    print_report(results_summary, pl_details)
    
    if args.csv is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.csv is True:
            csv_filename = f"large_prefix_entries-{timestamp}.csv"
        else:
            csv_filename = args.csv
        write_csv_report(results_summary, pl_details, csv_filename)
    
    logging.info("Processing complete.")

if __name__ == "__main__":
    main()

