"""
Module: audit.py
Provides functionality to filter AWS Prefix List entries based on CIDR block size.
"""

import logging

def filter_large_cidr_entries(entries, maxcidr):
    """
    Filters prefix list entries to return only those with a CIDR block larger than the given maxcidr.

    :param entries: List of prefix list entry dictionaries.
    :param maxcidr: Maximum allowed CIDR prefix length (e.g., 29 for /29).
    :return: Filtered list of entries.
    """
    filtered_entries = []
    for entry in entries:
        cidr = entry.get("Cidr", "")
        try:
            prefix_length = int(cidr.split("/")[-1])
            if prefix_length < maxcidr:
                filtered_entries.append(entry)
        except (ValueError, IndexError):
            logging.warning("Invalid CIDR format: %s", cidr)
    logging.info("Filtered %d entries with CIDR larger than /%d", len(filtered_entries), maxcidr)
    return filtered_entries