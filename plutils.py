#!/usr/bin/env python3
"""
AWS Prefix List Utilities CLI

This tool allows you to search and audit AWS Managed Prefix Lists using subcommands.
Use the 'search' subcommand to look up prefix list entries by name or IP.
Use the 'audit' subcommand to filter prefix list entries by CIDR size.

General options like --profile, --region, --plfilter, --plexclude, and --maxcidr can be used with either subcommand.
"""

import argparse
import boto3
import logging
import sys
from datetime import datetime

from modules.aws_helpers import get_managed_prefix_lists, get_prefix_list_entries
from modules.search import search_entries_by_field
from modules.audit import filter_large_cidr_entries
from modules.utils import setup_logging, write_csv_report

def search_command(args):
    # Setup logging
    setup_logging(quiet=args.quiet, filename_prefix="plutils_search")
    
    # Create boto3 session
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
    
    # Retrieve customer-managed prefix lists by filtering using the account ID.
    try:
        sts_client = session.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
    except Exception as e:
        logging.error(f"Failed to get AWS account ID: {e}")
        sys.exit(1)
    
    prefix_lists = get_managed_prefix_lists(ec2_client, account_id)
    
    # Further filter prefix lists by --plfilter and --plexclude options.
    filtered_pls = {}
    for pl in prefix_lists:
        pl_id = pl.get("PrefixListId")
        pl_name = pl.get("PrefixListName", "N/A")
        if args.plfilter and args.plfilter.lower() not in pl_name.lower():
            continue
        if args.plexclude and args.plexclude.lower() in pl_name.lower():
            continue
        filtered_pls[pl_id] = pl_name
    
    if not filtered_pls:
        logging.error("No prefix lists found after filtering.")
        sys.exit(1)
    
    # Process each filtered prefix list.
    results = []
    for pl_id, pl_name in filtered_pls.items():
        entries = get_prefix_list_entries(ec2_client, pl_id)
        if args.name:
            entries = search_entries_by_field(entries, args.name, "Description")
        elif args.ip:
            entries = search_entries_by_field(entries, args.ip, "Cidr")
        if entries:
            results.append((pl_id, pl_name, entries))
    
    # Print report.
    for pl_id, pl_name, entries in results:
        logging.info(f"{pl_id} | {pl_name} | {len(entries)} matching entries")
        for entry in entries:
            logging.info(f"  {entry.get('Cidr', 'N/A')} | {entry.get('Description', 'N/A')}")
    
    # CSV export if requested.
    if args.csv is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = args.csv if args.csv is not True else f"search_report-{timestamp}.csv"
        header = ["PLID", "PLName", "Cidr", "Description"]
        data_rows = []
        for pl_id, pl_name, entries in results:
            for entry in entries:
                data_rows.append([pl_id, pl_name, entry.get("Cidr", "N/A"), entry.get("Description", "N/A")])
        write_csv_report(csv_filename, header, data_rows)

def audit_command(args):
    # Setup logging
    setup_logging(quiet=args.quiet, filename_prefix="plutils_audit")
    
    # Convert --maxcidr to an integer (strip any leading '/')
    try:
        maxcidr_value = int(args.maxcidr.replace("/", ""))
    except Exception as e:
        logging.error("Invalid --maxcidr value. Please specify a number like 29 or /29.")
        sys.exit(1)
    
    # Create boto3 session
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
    
    # Retrieve customer-managed prefix lists.
    try:
        sts_client = session.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
    except Exception as e:
        logging.error(f"Failed to get AWS account ID: {e}")
        sys.exit(1)
    
    prefix_lists = get_managed_prefix_lists(ec2_client, account_id)
    
    # Further filter by --plfilter and --plexclude.
    filtered_pls = {}
    for pl in prefix_lists:
        pl_id = pl.get("PrefixListId")
        pl_name = pl.get("PrefixListName", "N/A")
        if args.plfilter and args.plfilter.lower() not in pl_name.lower():
            continue
        if args.plexclude and args.plexclude.lower() in pl_name.lower():
            continue
        filtered_pls[pl_id] = pl_name
    
    if not filtered_pls:
        logging.error("No prefix lists found after filtering.")
        sys.exit(1)
    
    # Process each filtered prefix list.
    results = []
    for pl_id, pl_name in filtered_pls.items():
        entries = get_prefix_list_entries(ec2_client, pl_id)
        large_entries = filter_large_cidr_entries(entries, maxcidr_value)
        if large_entries:
            results.append((pl_id, pl_name, large_entries))
    
    # Print report.
    for pl_id, pl_name, entries in results:
        logging.info(f"{pl_id} | {pl_name} | {len(entries)} matching entries")
        for entry in entries:
            logging.info(f"  {entry.get('Cidr', 'N/A')} | {entry.get('Description', 'N/A')}")
    
    # CSV export if requested.
    if args.csv is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = args.csv if args.csv is not True else f"audit_report-{timestamp}.csv"
        header = ["PLID", "PLName", "Cidr", "Description"]
        data_rows = []
        for pl_id, pl_name, entries in results:
            for entry in entries:
                data_rows.append([pl_id, pl_name, entry.get("Cidr", "N/A"), entry.get("Description", "N/A")])
        write_csv_report(csv_filename, header, data_rows)

def main():
    parser = argparse.ArgumentParser(
        description="AWS Prefix List Utilities - Search and Audit AWS Managed Prefix Lists using subcommands."
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommands: search or audit")
    subparsers.required = True

    # Subcommand: search
    search_parser = subparsers.add_parser("search", help="Search prefix list entries by name or IP")
    search_parser.add_argument("--name", help="Search term for prefix list entries in Description (case-insensitive)")
    search_parser.add_argument("--ip", help="Search term for prefix list entries in Cidr (supports partial match)")
    search_parser.add_argument("--plfilter", help="Only include prefix lists whose name contains this string (case-insensitive)")
    search_parser.add_argument("--plexclude", help="Exclude prefix lists whose name contains this string (case-insensitive)")
    search_parser.add_argument("--profile", help="AWS CLI profile to use")
    search_parser.add_argument("--region", help="AWS region to use")
    search_parser.add_argument("--quiet", action="store_true", help="Suppress intermediate output")
    search_parser.add_argument("--csv", nargs="?", const=True, help="Output CSV report. Optionally specify a filename.")

    # Subcommand: audit
    audit_parser = subparsers.add_parser("audit", help="Audit prefix lists by CIDR size")
    audit_parser.add_argument("--maxcidr", default="29", help="Maximum CIDR prefix (e.g., /29 or 29). Any IP block with a prefix length smaller than this value is considered a match. Default is 29.")
    audit_parser.add_argument("--plfilter", help="Only include prefix lists whose name contains this string (case-insensitive)")
    audit_parser.add_argument("--plexclude", help="Exclude prefix lists whose name contains this string (case-insensitive)")
    audit_parser.add_argument("--profile", help="AWS CLI profile to use")
    audit_parser.add_argument("--region", help="AWS region to use")
    audit_parser.add_argument("--quiet", action="store_true", help="Suppress intermediate output")
    audit_parser.add_argument("--csv", nargs="?", const=True, help="Output CSV report. Optionally specify a filename.")

    args = parser.parse_args()

    if args.command == "search":
        search_command(args)
    elif args.command == "audit":
        audit_command(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

