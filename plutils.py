#!/usr/bin/env python3
"""
AWS Prefix List Utilities CLI

This tool allows you to search, audit, and list customer-managed AWS
Managed Prefix Lists using subcommands. Use 'search' to look up prefix
list entries by name or IP, 'audit' to filter prefix list entries by
CIDR size, and 'list' to list customer-managed prefix lists.
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import NoReturn, List, Dict

import botocore.exceptions
# If you need other specific Boto3 exceptions, you can import them here
# from botocore.exceptions import ClientError, NoCredentialsError, etc.

# Local module imports
from modules.aws_helpers import (
    get_ec2_client_and_account,
    get_managed_prefix_lists,
    filter_prefix_lists,
    get_prefix_list_entries
)
from modules.search_pl import search_entries_by_field
from modules.audit_pl import filter_large_cidr_entries
from modules.list_pl import list_prefix_lists
from modules.utils import setup_logging, write_csv_report


def _get_filtered_prefix_lists(args: argparse.Namespace) -> List[Dict]:
    """
    Helper function to:
      1. Create or retrieve an AWS session (ec2_client, account_id).
      2. Retrieve all managed prefix lists.
      3. Filter prefix lists according to plfilter and plexclude.

    :param args: Parsed command-line arguments.
    :return: A list of prefix list dictionaries matching filters.
    :raises: Any exceptions from AWS session creation or retrieval.
    """
    ec2_client, account_id = get_ec2_client_and_account(
        profile=args.profile,
        region=args.region
    )
    prefix_lists = get_managed_prefix_lists(ec2_client, account_id)
    return filter_prefix_lists(prefix_lists, args.plfilter, args.plexclude)


def _handle_csv_output(
    csv_arg: str,
    default_prefix: str,
    header: List[str],
    data_rows: List[List[str]]
) -> None:
    """
    Helper function to handle optional CSV output for any subcommand.

    :param csv_arg: The --csv argument; if None, don't output CSV. If True, generate
                    a filename. Otherwise, treat as a user-specified filename.
    :param default_prefix: A string like "search_report" or "audit_report", used if
                           csv_arg is True.
    :param header: List of column headers for the CSV.
    :param data_rows: Data rows to write into the CSV.
    """
    if csv_arg is not None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = csv_arg if csv_arg is not True else f"{default_prefix}-{timestamp}.csv"
        write_csv_report(csv_filename, header, data_rows)


def search_command(args: argparse.Namespace) -> None:
    """
    Handles the 'search' subcommand.

    - Retrieves prefix lists (optionally filtered).
    - Searches for entries by either name (Description) or IP (Cidr).
    - Prints results to console; optionally writes to CSV.
    """
    try:
        filtered_pls = _get_filtered_prefix_lists(args)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as err:
        logging.error("Unable to initialize AWS session or retrieve prefix lists: %s", err)
        sys.exit(1)

    if not filtered_pls:
        logging.error("No prefix lists found after filtering.")
        sys.exit(1)

    results = []
    for pl in filtered_pls:
        pl_id = pl.get("PrefixListId")
        pl_name = pl.get("PrefixListName", "N/A")
        ec2_client, _ = get_ec2_client_and_account(
            profile=args.profile,
            region=args.region
        )
        entries = get_prefix_list_entries(ec2_client, pl_id)

        # Search either by name (Description) or IP (Cidr)
        if args.name:
            entries = search_entries_by_field(entries, args.name, "Description")
        elif args.ip:
            entries = search_entries_by_field(entries, args.ip, "Cidr")

        if entries:
            results.append((pl_id, pl_name, entries))

    print("\nFINAL REPORT")
    print("=" * 60)
    for pl_id, pl_name, entries in results:
        print(f"{pl_id} | {pl_name} | {len(entries)} matching entries")
        for entry in entries:
            cidr = entry.get("Cidr", "N/A")
            desc = entry.get("Description", "N/A")
            print(f"  {cidr} | {desc}")
        print("-" * 60)

    # CSV output
    data_rows = []
    for pl_id, pl_name, entries in results:
        for entry in entries:
            data_rows.append([
                pl_id,
                pl_name,
                entry.get("Cidr", "N/A"),
                entry.get("Description", "N/A"),
            ])
    _handle_csv_output(
        csv_arg=args.csv,
        default_prefix="search_report",
        header=["PLID", "PLName", "Cidr", "Description"],
        data_rows=data_rows
    )


def audit_command(args: argparse.Namespace) -> None:
    """
    Handles the 'audit' subcommand.

    - Retrieves prefix lists (optionally filtered).
    - Filters each list for entries with CIDR size bigger than --maxcidr.
    - Prints results to console; optionally writes to CSV.
    """
    try:
        maxcidr_value = int(args.maxcidr.replace("/", ""))
    except ValueError as exc:
        logging.error("Invalid --maxcidr value (%s). Use e.g. 29 or /29.", exc)
        sys.exit(1)

    try:
        filtered_pls = _get_filtered_prefix_lists(args)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as err:
        logging.error("Unable to initialize AWS session or retrieve prefix lists: %s", err)
        sys.exit(1)

    if not filtered_pls:
        logging.error("No prefix lists found after filtering.")
        sys.exit(1)

    results = []
    for pl in filtered_pls:
        pl_id = pl.get("PrefixListId")
        pl_name = pl.get("PrefixListName", "N/A")

        ec2_client, _ = get_ec2_client_and_account(
            profile=args.profile,
            region=args.region
        )
        entries = get_prefix_list_entries(ec2_client, pl_id)

        large_entries = filter_large_cidr_entries(entries, maxcidr_value)
        if large_entries:
            results.append((pl_id, pl_name, large_entries))

    print("\nFINAL REPORT")
    print("=" * 60)
    for pl_id, pl_name, entries in results:
        print(f"{pl_id} | {pl_name} | {len(entries)} matching entries")
        for entry in entries:
            cidr = entry.get("Cidr", "N/A")
            desc = entry.get("Description", "N/A")
            print(f"  {cidr} | {desc}")
        print("-" * 60)

    # CSV output
    data_rows = []
    for pl_id, pl_name, entries in results:
        for entry in entries:
            data_rows.append([
                pl_id,
                pl_name,
                entry.get("Cidr", "N/A"),
                entry.get("Description", "N/A"),
            ])
    _handle_csv_output(
        csv_arg=args.csv,
        default_prefix="audit_report",
        header=["PLID", "PLName", "Cidr", "Description"],
        data_rows=data_rows
    )


def list_command(args: argparse.Namespace) -> None:
    """
    Handles the 'list' subcommand.

    - Lists customer-managed prefix lists matching optional filters.
    - Prints results to console; optionally writes to CSV.
    """
    try:
        ec2_client, account_id = get_ec2_client_and_account(
            profile=args.profile,
            region=args.region
        )
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as err:
        logging.error("Unable to initialize AWS session: %s", err)
        sys.exit(1)

    # The list_prefix_lists function calls get_managed_prefix_lists internally
    # and applies the same filter logic, so we don't need filter_prefix_lists here.
    prefix_lists = list_prefix_lists(
        ec2_client,
        account_id,
        pl_filter=args.plfilter,
        pl_exclude=args.plexclude
    )
    if not prefix_lists:
        logging.error("No prefix lists found matching the criteria.")
        sys.exit(1)

    print("\nCustomer-managed Prefix Lists:")
    print("=" * 60)
    for pl_id, pl_name in prefix_lists.items():
        print(f"{pl_id}: {pl_name}")
        logging.info("%s: %s", pl_id, pl_name)

    # CSV output
    data_rows = [[pl_id, pl_name] for pl_id, pl_name in prefix_lists.items()]
    _handle_csv_output(
        csv_arg=args.csv,
        default_prefix="list_report",
        header=["PLID", "PLName"],
        data_rows=data_rows
    )


def main() -> NoReturn:
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(
        description=(
            "AWS Prefix List Utilities - Search, Audit, and List "
            "customer-managed AWS Managed Prefix Lists using subcommands."
        )
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Subcommands: search, audit, or list"
    )
    subparsers.required = True

    # Common arguments for all subcommands
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose console logging"
    )

    # Subcommand: search
    search_parser = subparsers.add_parser("search", help="Search prefix list entries by name or IP")
    search_parser.add_argument(
        "--name",
        help="Search term for prefix list entries in Description (case-insensitive)"
    )
    search_parser.add_argument(
        "--ip",
        help="Search term for prefix list entries in Cidr (supports partial match)"
    )
    search_parser.add_argument(
        "--plfilter",
        help="Include prefix lists whose name contains this string (case-insensitive)"
    )
    search_parser.add_argument(
        "--plexclude",
        help="Exclude prefix lists whose name contains this string (case-insensitive)"
    )
    search_parser.add_argument("--profile", help="AWS CLI profile to use")
    search_parser.add_argument("--region", help="AWS region to use")
    search_parser.add_argument(
        "--csv",
        nargs="?",
        const=True,
        help="Output CSV report. Optionally specify a filename."
    )
    search_parser.set_defaults(func=search_command)

    # Subcommand: audit
    audit_parser = subparsers.add_parser("audit", help="Audit prefix lists by CIDR size")
    audit_parser.add_argument(
        "--maxcidr",
        default="29",
        help=(
            "Maximum CIDR prefix (e.g., /29 or 29). Any IP block with a prefix "
            "length smaller than this value is considered a match. Default is 29."
        )
    )
    audit_parser.add_argument(
        "--plfilter",
        help="Include prefix lists whose name contains this string (case-insensitive)"
    )
    audit_parser.add_argument(
        "--plexclude",
        help="Exclude prefix lists whose name contains this string (case-insensitive)"
    )
    audit_parser.add_argument("--profile", help="AWS CLI profile to use")
    audit_parser.add_argument("--region", help="AWS region to use")
    audit_parser.add_argument(
        "--csv",
        nargs="?",
        const=True,
        help="Output CSV report. Optionally specify a filename."
    )
    audit_parser.set_defaults(func=audit_command)

    # Subcommand: list
    list_parser = subparsers.add_parser("list", help="List customer-managed prefix lists")
    list_parser.add_argument(
        "--plfilter",
        help="Include prefix lists whose name contains this string (case-insensitive)"
    )
    list_parser.add_argument(
        "--plexclude",
        help="Exclude prefix lists whose name contains this string (case-insensitive)"
    )
    list_parser.add_argument("--profile", help="AWS CLI profile to use")
    list_parser.add_argument("--region", help="AWS region to use")
    list_parser.add_argument(
        "--csv",
        nargs="?",
        const=True,
        help="Output CSV report. Optionally specify a filename."
    )
    list_parser.set_defaults(func=list_command)

    args = parser.parse_args()

    # Set up logging once, so each command shares the same log.
    setup_logging(verbose=args.verbose, filename_prefix=f"plutils_{args.command}")

    # Dispatch to subcommand
    args.func(args)  # type: ignore


if __name__ == "__main__":
    main()
