"""
Module: audit.py
Provides functionality to filter AWS Prefix List entries based on CIDR block size.
"""

import logging
from typing import List, Dict, Any


def filter_large_cidr_entries(
    entries: List[Dict[str, Any]],
    maxcidr: int
) -> List[Dict[str, Any]]:
    """
    Filters prefix list entries to return only those with a CIDR block larger
    (i.e., a smaller prefix length number) than the given maxcidr.

    Example: If maxcidr is 29, then entries with a /28, /27, etc. are "larger"
    blocks and thus should be returned.

    :param entries: A list of prefix list entry dictionaries.
    :param maxcidr: Maximum allowed CIDR prefix length (e.g., 29 for /29).
    :return: Filtered list of entries.
    """
    filtered_entries = []
    for entry in entries:
        cidr = entry.get("Cidr", "")
        try:
            prefix_length = int(cidr.split("/")[-1])
            # If prefix_length < maxcidr => it's a larger block (e.g. /28).
            if prefix_length < maxcidr:
                filtered_entries.append(entry)
        except (ValueError, IndexError):
            logging.warning("Invalid CIDR format: %s", cidr)

    logging.info(
        "Filtered %d entries with CIDR larger than /%d",
        len(filtered_entries),
        maxcidr
    )
    return filtered_entries