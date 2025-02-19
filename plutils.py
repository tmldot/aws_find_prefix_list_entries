#!/usr/bin/env python3
"""
AWS Prefix List Utilities CLI

This tool allows you to search, audit, and list customer-managed AWS Managed Prefix Lists
using subcommands. Use 'search' to look up prefix list entries by name or IP, 'audit' to filter
prefix list entries by CIDR size, and 'list' to list customer-managed prefix lists.

Common options such as --profile, --region, --plfilter, and --plexclude apply to all subcommands.
The default behavior suppresses console logging; use the -v/--verbose flag to enable screen logging.
"""

# Standard library imports
import argparse
import logging
import sys
from datetime import datetime

# Third-party imports
import boto3

# Local module imports
from modules.aws_helpers import get_managed_prefix_lists, get_prefix_list_entries
from modules.search import search_entries_by_field
from modules.audit import filter_large_cidr_entries
from modules.utils import setup_logging, write_csv_report
from modules.list import list_prefix_lists

def search_command(args):
    """Handles the 'search' subcommand."""
    setup_logging(verbose=args.verbose, filename_prefix="plutils_search")
    
    session_kwargs = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile
    if args.region:
        session_kwargs["region_name"] = args.region
    session = boto3.Session(**session_kwargs)
    
    try:
        ec2_client = session.client("ec2")
    except Exception as err:
        logging.error("Failed to create EC2 client: %s", err)
        sys.exit(1)
    
    try:
        sts_client = session.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
    except Exception as err:
        logging.error("Failed to get AWS account ID: %s", err)
        sys.exit(1)
    
    prefix_lists = get_managed_prefix_lists(ec2_client, account_id)
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
    
    results = []
    for pl_id, pl_name in filtered_pls.items():
        entries = get_prefix_list_entries(ec2_client, pl_id)
        if args.name:
            entries = search_entries_by_field(entries, args.name, "Description")
        elif args.ip:
            entries = search_entries_by_field(entries, args.ip, "Cidr")
        if entries:
            results.append((pl_id, pl_name, entries))
    
    # Print the final report.
    print("\nFINAL REPORT")
    print("=" * 60)
    for pl_id, pl_name, entries in results:
        print("{} | {} | {} matching entries".format(pl_id, pl_name, len(entries)))
        for entry in entries:
            print("  {} | {}".format(
                entry.get("Cidr", "N/A"), entry.get("Description", "N/A")
            ))
        print("-" * 60)
    
    if args.csv is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = args.csv if args.csv is not True else \
            "search_report-{}.csv".format(timestamp)
        header = ["PLID", "PLName", "Cidr", "Description"]
        data_rows = []
        for pl_id, pl_name, entries in results:
            for entry in entries:
                data_rows.append([
                    pl_id,
                    pl_name,
                    entry.get("Cidr", "N/A"),
                    entry.get("Description", "N/A")
                ])
        write_csv_report(csv_filename, header, data_rows)

def audit_command(args):
    """Handles the 'audit' subcommand."""
    setup_logging(verbose=args.verbose, filename_prefix="plutils_audit")
    
    try:
        maxcidr_value = int(args.maxcidr.replace("/", ""))
    except Exception as err:
        logging.error("Invalid --maxcidr value. Please specify a number like 29 or /29: %s", err)
        sys.exit(1)
    
    session_kwargs = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile
    if args.region:
        session_kwargs["region_name"] = args.region
    session = boto3.Session(**session_kwargs)
    
    try:
        ec2_client = session.client("ec2")
    except Exception as err:
        logging.error("Failed to create EC2 client: %s", err)
        sys.exit(1)
    
    try:
        sts_client = session.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
    except Exception as err:
        logging.error("Failed to get AWS account ID: %s", err)
        sys.exit(1)
    
    prefix_lists = get_managed_prefix_lists(ec2_client, account_id)
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
    
    results = []
    for pl_id, pl_name in filtered_pls.items():
        entries = get_prefix_list_entries(ec2_client, pl_id)
        large_entries = filter_large_cidr_entries(entries, maxcidr_value)
        if large_entries:
            results.append((pl_id, pl_name, large_entries))
    
    print("\nFINAL REPORT")
    print("=" * 60)
    for pl_id, pl_name, entries in results:
        print("{} | {} | {} matching entries".format(pl_id, pl_name, len(entries)))
        for entry in entries:
            print("  {} | {}".format(
                entry.get("Cidr", "N/A"), entry.get("Description", "N/A")
            ))
        print("-" * 60)
    
    if args.csv is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = args.csv if args.csv is not True else \
            "audit_report-{}.csv".format(timestamp)
        header = ["PLID", "PLName", "Cidr", "Description"]
        data_rows = []
        for pl_id, pl_name, entries in results:
            for entry in entries:
                data_rows.append([
                    pl_id,
                    pl_name,
                    entry.get("Cidr", "N/A"),
                    entry.get("Description", "N/A")
                ])
        write_csv_report(csv_filename, header, data_rows)

def list_command(args):
    """Handles the 'list' subcommand."""
    setup_logging(verbose=args.verbose, filename_prefix="plutils_list")
    
    session_kwargs = {}
    if args.profile:
        session_kwargs["profile_name"] = args.profile
    if args.region:
        session_kwargs["region_name"] = args.region
    session = boto3.Session(**session_kwargs)
    
    try:
        ec2_client = session.client("ec2")
    except Exception as err:
        logging.error("Failed to create EC2 client: %s", err)
        sys.exit(1)
    
    try:
        sts_client = session.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
    except Exception as err:
        logging.error("Failed to get AWS account ID: %s", err)
        sys.exit(1)
    
    prefix_lists = list_prefix_lists(
        ec2_client, account_id, pl_filter=args.plfilter,
        pl_exclude=args.plexclude
    )
    if not prefix_lists:
        logging.error("No prefix lists found matching the criteria.")
        sys.exit(1)
    
    print("\nCustomer-managed Prefix Lists:")
    print("=" * 60)
    for pl_id, pl_name in prefix_lists.items():
        print("{}: {}".format(pl_id, pl_name))
        logging.info("%s: %s", pl_id, pl_name)
    
    if args.csv is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = args.csv if args.csv is not True else \
            "list_report-{}.csv".format(timestamp)
        header = ["PLID", "PLName"]
        data_rows = [[pl_id, pl_name] for pl_id, pl_name in prefix_lists.items()]
        write_csv_report(csv_filename, header, data_rows)

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description=("AWS Prefix List Utilities - Search, Audit, and List customer-managed "
                     "AWS Managed Prefix Lists using subcommands.")
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Subcommands: search, audit, or list"
    )
    subparsers.required = True

    # Subcommand: search
    search_parser = subparsers.add_parser("search", help="Search prefix list entries by name or IP")
    search_parser.add_argument("--name", help=("Search term for prefix list entries in Description "
                                               "(case-insensitive)"))
    search_parser.add_argument("--ip", help=("Search term for prefix list entries in Cidr "
                                             "(supports partial match)"))
    search_parser.add_argument("--plfilter", help=("Only include prefix lists whose name contains "
                                                   "this string (case-insensitive)"))
    search_parser.add_argument("--plexclude", help=("Exclude prefix lists whose name contains "
                                                    "this string (case-insensitive)"))
    search_parser.add_argument("--profile", help="AWS CLI profile to use")
    search_parser.add_argument("--region", help="AWS region to use")
    search_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose console logging")
    search_parser.add_argument("--csv", nargs="?", const=True, help=("Output CSV report. Optionally specify "
                                                                     "a filename."))

    # Subcommand: audit
    audit_parser = subparsers.add_parser("audit", help="Audit prefix lists by CIDR size")
    audit_parser.add_argument("--maxcidr", default="29", help=("Maximum CIDR prefix (e.g., /29 or 29). "
                                                              "Any IP block with a prefix length smaller than "
                                                              "this value is considered a match. Default is 29."))
    audit_parser.add_argument("--plfilter", help=("Only include prefix lists whose name contains "
                                                  "this string (case-insensitive)"))
    audit_parser.add_argument("--plexclude", help=("Exclude prefix lists whose name contains "
                                                   "this string (case-insensitive)"))
    audit_parser.add_argument("--profile", help="AWS CLI profile to use")
    audit_parser.add_argument("--region", help="AWS region to use")
    audit_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose console logging")
    audit_parser.add_argument("--csv", nargs="?", const=True, help=("Output CSV report. Optionally specify "
                                                                     "a filename."))

    # Subcommand: list
    list_parser = subparsers.add_parser("list", help="List customer-managed prefix lists")
    list_parser.add_argument("--plfilter", help=("Only include prefix lists whose name contains "
                                                 "this string (case-insensitive)"))
    list_parser.add_argument("--plexclude", help=("Exclude prefix lists whose name contains "
                                                  "this string (case-insensitive)"))
    list_parser.add_argument("--profile", help="AWS CLI profile to use")
    list_parser.add_argument("--region", help="AWS region to use")
    list_parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose console logging")
    list_parser.add_argument("--csv", nargs="?", const=True, help=("Output CSV report. Optionally specify "
                                                                    "a filename."))

    args = parser.parse_args()

    if args.command == "search":
        search_command(args)
    elif args.command == "audit":
        audit_command(args)
    elif args.command == "list":
        list_command(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

