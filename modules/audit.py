import ipaddress
import logging

def filter_large_cidr_entries(entries, maxcidr):
    """
    From the provided entries, return only those whose CIDR prefix length is less than maxcidr.
    For example, if maxcidr is 29, then any entry with a prefix length less than 29 (e.g., /28, /27, etc.) is returned.
    
    :param entries: List of entry dictionaries.
    :param maxcidr: Maximum CIDR prefix as an integer.
    :return: A list of entries with CIDR sizes larger than the specified maxcidr.
    """
    filtered = []
    for entry in entries:
        cidr = entry.get("Cidr")
        if cidr:
            try:
                network = ipaddress.ip_network(cidr, strict=False)
                if network.prefixlen < maxcidr:
                    filtered.append(entry)
            except ValueError as ve:
                logging.error(f"Invalid CIDR '{cidr}': {ve}")
    return filtered

