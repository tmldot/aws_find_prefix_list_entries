def search_entries_by_field(entries, search_value, field):
    """
    Filter the provided entries by searching for 'search_value' within the specified 'field'.
    The search is case-insensitive.
    
    :param entries: List of entry dictionaries.
    :param search_value: The search term.
    :param field: The field to search in ('Description' or 'Cidr').
    :return: A list of entries matching the search term.
    """
    filtered = []
    for entry in entries:
        if field in entry and search_value.lower() in entry[field].lower():
            filtered.append(entry)
    return filtered

