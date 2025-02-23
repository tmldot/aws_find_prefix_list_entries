"""
Module: search_pl.py
Provides functionality to search and filter AWS prefix list entries.
"""

from typing import List, Dict, Any


def search_entries_by_field(
    entries: List[Dict[str, Any]],
    search_value: str,
    field: str
) -> List[Dict[str, Any]]:
    """
    Filter the provided entries by searching for the given search_value
    within the specified field. The search is case-insensitive.

    :param entries: List of entry dictionaries.
    :param search_value: The search term.
    :param field: The field to search in (e.g., 'Description' or 'Cidr').
    :return: A list of entries matching the search criteria.
    """
    filtered = []
    lower_search = search_value.lower()
    for entry in entries:
        if field in entry and lower_search in entry[field].lower():
            filtered.append(entry)
    return filtered