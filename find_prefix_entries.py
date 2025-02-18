#!/usr/bin/env python3
"""
Description:
    Retrieves all managed prefix list entries across all prefix lists whose either 'Description'
    (when using --name) or 'Cidr' (when using --ip) contains the provided search term.
    The search is case-insensitive for names and supports partial matching for IP addresses.
    
    The final report is structured as follows:
      PLID,PLName,Cidr,Description
      
Usage:
    Search by name (Description):
        python find_prefix_entries.py --name "ExampleVendor" [--profile myprofile] [--region us-east-1] [--csv [filename.csv]]
        
    Search by IP (Cidr):
        python find_prefix_entries.py --ip "192.168.1" [--profile myprofile] [--region us-east-1] [--csv [filename.csv]]
        
    To run in quiet mode (suppress intermediate output):
        python find_prefix_entries.py --name "ExampleVendor" --quiet [--profile myprofile] [--region us-east-1] [--csv [filename.csv]]
    
    (If no profile/region is provided, the default is used)

Requirements:
    - Python 3.6+
    - boto3 (`pip install boto3`)
"""

import boto3
import argparse
import logging
import sys
import csv
from datetime import datetime

def setup_logging(quiet=False, search_value=None):
    """
    Set up logging to file and console.
    The log file is named 'prefixlist_search-<search_value>-YYYYMMDD_HHmmss.log'
    
    :param quiet: If True, suppresses console logging of intermediate steps.
    :param search_value: Normalized search parameter to include in the log file name.
    :return: The logfile name.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    normalized_search = "all"
    if search_value:
        normalized_search = search_value.replace(" ", "_")
    logfile = f"prefixlist_search-{normalized_search}-{timestamp}.log"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler (always log to file)
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO)
    
    # Console handler: if quiet, suppress intermediate messages.
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

def get_prefix_list_details(ec2_client):
    """
    Retrieves all managed prefix lists and returns a dictionary mapping
    prefix list ID to its name.
    
    :param ec2_client: A boto3 EC2 client.
    :return: Dictionary with key as PrefixListId and value as PrefixListName.
    """
    logging.info("Retrieving all managed prefix lists...")
    response = ec2_client.describe_managed_prefix_lists()
    prefix_lists = response.get('PrefixLists', [])
    pl_details = {}
    for pl in prefix_lists:
        pl_id = pl.get('PrefixListId')
        pl_name = pl.get('PrefixListName', 'N/A')
        if pl_id:
            pl_details[pl_id] = pl_name
    if not pl_details:
        logging.error("No managed prefix lists found.")
    else:
        logging.info(f"Found {len(pl_details)} managed prefix list(s).")
    return pl_details

def search_prefix_list_entries(ec2_client, prefix_list_id, search_value, search_field):
    """
    Fetches and filters prefix list entries for a specific prefix list based on the search value.
    
    :param ec2_client: A boto3 EC2 client.
    :param prefix_list_id: The ID of the managed prefix list.
    :param search_value: The search term (lowercase for names) to match.
    :param search_field: Field to search against ('Description' or 'Cidr').
    :return: A list of filtered entries.
    """
    logging.info(f"Processing prefix list: {prefix_list_id}")
    try:
        response = ec2_client.get_managed_prefix_list_entries(PrefixListId=prefix_list_id)
    except Exception as e:
        logging.error(f"Error retrieving entries for prefix list {prefix_list_id}: {e}")
        return []
    
    entries = response.get('Entries', [])
    filtered_entries = []
    
    for entry in entries:
        if search_field == "Description":
            if 'Description' in entry and search_value in entry['Description'].lower():
                filtered_entries.append(entry)
        elif search_field == "Cidr":
            if 'Cidr' in entry and search_value in entry['Cidr']:
                filtered_entries.append(entry)
    
    if filtered_entries:
        logging.info(f"Found {len(filtered_entries)} matching entry(ies) in {prefix_list_id}")
    else:
        logging.info(f"No matching entries found in {prefix_list_id}")
    
    return filtered_entries

def print_report(results_summary, pl_details):
    """
    Prints a summary report to the console.
    
    Format:
      PLID | PLName | # Entries
      Cidr | Description
      ...
      
    :param results_summary: Dictionary with key as PrefixListId and value as list of entries.
    :param pl_details: Dictionary mapping PrefixListId to PrefixListName.
    """
    report_lines = []
    report_lines.append("\nFINAL REPORT")
    report_lines.append("=" * 60)
    
    if not results_summary:
        report_lines.append("No matching entries found in any managed prefix lists.")
    else:
        for pl_id, entries in results_summary.items():
            pl_name = pl_details.get(pl_id, "N/A")
            header = f"{pl_id} | {pl_name} | {len(entries)} matching entr{'y' if len(entries)==1 else 'ies'}"
            report_lines.append(header)
            for entry in entries:
                cidr = entry.get('Cidr', 'N/A')
                description = entry.get('Description', 'N/A')
                report_lines.append(f"  {cidr} | {description}")
            report_lines.append("-" * 60)
    
    for line in report_lines:
        logging.info(line)
    print("\n".join(report_lines))

def write_csv_report(results_summary, pl_details, csv_filename):
    """
    Writes the final report to a CSV file.
    
    CSV Format:
      PLID,PLName,Cidr,Description
      
    :param results_summary: Dictionary with key as PrefixListId and value as list of entries.
    :param pl_details: Dictionary mapping PrefixListId to PrefixListName.
    :param csv_filename: Output CSV filename.
    """
    header = ['PLID', 'PLName', 'Cidr', 'Description']
    try:
        with open(csv_filename, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            # Write each matching entry as a row.
            for pl_id, entries in results_summary.items():
                pl_name = pl_details.get(pl_id, "N/A")
                for entry in entries:
                    cidr = entry.get('Cidr', 'N/A')
                    description = entry.get('Description', 'N/A')
                    writer.writerow([pl_id, pl_name, cidr, description])
        logging.info(f"CSV report written to {csv_filename}")
    except Exception as e:
        logging.error(f"Failed to write CSV report: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Search managed prefix list entries by Description or IP and produce a report."
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--name", help="Search term for prefix list description (case-insensitive)")
    group.add_argument("--ip", help="Search term for IP address; supports partial match up to full CIDR notation")
    
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress intermediate screen output (final report will still be printed)")
    parser.add_argument("--profile", help="AWS CLI profile to use")
    parser.add_argument("--region", help="AWS region to use")
    parser.add_argument("--csv", nargs="?", const=True, help="Output CSV report. Optionally specify a filename.")
    
    args = parser.parse_args()
    
    # Determine search field and process search term accordingly.
    if args.name:
        search_field = "Description"
        search_value = args.name.lower()
    else:
        search_field = "Cidr"
        search_value = args.ip
    
    # Set up logging with the normalized search parameter.
    setup_logging(quiet=args.quiet, search_value=search_value)
    
    # Create a boto3 session with optional profile and region.
    session_kwargs = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile
    if args.region:
        session_kwargs["region_name"] = args.region
    session = boto3.Session(**session_kwargs)
    
    try:
        ec2_client = session.client('ec2')
    except Exception as e:
        logging.error(f"Failed to create EC2 client: {e}")
        sys.exit(1)
    
    pl_details = get_prefix_list_details(ec2_client)
    if not pl_details:
        sys.exit(1)
    
    results_summary = {}
    
    for pl_id in pl_details:
        filtered_entries = search_prefix_list_entries(ec2_client, pl_id, search_value, search_field)
        if filtered_entries:
            results_summary[pl_id] = filtered_entries
        logging.info("-" * 60)
    
    print_report(results_summary, pl_details)
    
    # If CSV output is requested.
    if args.csv is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        normalized_search = search_value.replace(" ", "_")
        # If a filename was provided, use it; otherwise, generate one.
        if args.csv is True:
            csv_filename = f"prefixlist_search-{normalized_search}-{timestamp}.csv"
        else:
            csv_filename = args.csv
        write_csv_report(results_summary, pl_details, csv_filename)
    
    logging.info("Processing complete.")

if __name__ == "__main__":
    main()

