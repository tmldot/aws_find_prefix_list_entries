# AWS Prefix List Utilities

## Overview

This repository contains Python CLI tools for working with AWS Managed Prefix Lists (PLs). These scripts allow you to search, audit, and report on prefix list entries by IP address, partner name, or CIDR range.

## Tools Included

### 1. `find_prefix_entries.py`
Search AWS Managed Prefix Lists by IP address or partner name and generate detailed reports. Supports optional CSV output and filtering by prefix list name.

#### Features:
- **Search by Name or IP:**  
  Search for prefix list entries by `Description` (case-insensitive) or `Cidr` (supports partial matches).

- **Filter by Prefix List Name:**  
  Use the `--plfilter` option to search only PLs whose name contains a specific string (case-insensitive).

- **Custom AWS Profile and Region:**  
  Optionally specify an AWS CLI profile and region to target specific accounts or regions.

- **Quiet Mode:**  
  Suppress intermediate console output while still logging detailed operations to a log file.

- **CSV Export:**  
  Export the final report to CSV with columns for PLID, PLName, Cidr, and Description.

- **Timestamped Logging:**  
  Automatically generates log files with a timestamp and normalized search term.

#### Usage Examples

**Search by Name (in Description field):**
```bash
./find_prefix_entries.py --name "ExampleVendor"
```

**Search by IP (supports partial match):**
```bash
./find_prefix_entries.py --ip "192.168.1"
```

**Filter Prefix Lists by Name (only check PLs containing "ExampleVendor"):**
```bash
./find_prefix_entries.py --name "ExampleVendor" --plfilter "ExampleVendor"
```

**Specify AWS Profile and Region:**
```bash
./find_prefix_entries.py --name "ExampleVendor" --profile myprofile --region us-east-1
```

**Quiet Mode (only logs critical messages to console):**
```bash
./find_prefix_entries.py --name "ExampleVendor" --quiet
```

**Export Results to CSV:**
```bash
./find_prefix_entries.py --name "ExampleVendor" --csv results.csv
```

---

### 2. `find_large_customer_prefix_entries.py`
Search AWS **customer-managed** Prefix Lists for any IP block larger than a `/29` (i.e., `/28`, `/27`, etc.). Supports optional prefix list filtering by name.

#### Features:
- **Customer-Managed Lists Only:**  
  The script only checks prefix lists owned by the current AWS account.

- **Filter by Prefix List Name:**  
  Use the `--plfilter` option to search only PLs whose name contains a specific string (case-insensitive).

- **Custom AWS Profile and Region:**  
  Optionally specify an AWS CLI profile and region to target specific accounts or regions.

- **Quiet Mode:**  
  Suppress intermediate console output while still logging detailed operations to a log file.

- **CSV Export:**  
  Export the final report to CSV with columns for PLID, PLName, Cidr, and Description.

#### Usage Examples

**Find all IP blocks larger than `/29` in customer-managed prefix lists:**
```bash
./find_large_customer_prefix_entries.py
```

**Filter Prefix Lists by Name (only check PLs containing "ExampleVendor"):**
```bash
./find_large_customer_prefix_entries.py --plfilter "ExampleVendor"
```

**Specify AWS Profile and Region:**
```bash
./find_large_customer_prefix_entries.py --profile myprofile --region us-east-1
```

**Quiet Mode (only logs critical messages to console):**
```bash
./find_large_customer_prefix_entries.py --quiet
```

**Export Results to CSV:**
```bash
./find_large_customer_prefix_entries.py --csv results.csv
```

---

## Requirements

- Python 3.6+
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)  
  Install via pip:
  ```bash
  pip install boto3
  ```

## Logging

Both scripts generate timestamped log files in the working directory (e.g., `prefixlist_search-examplevendor-20250218_123456.log`). These logs provide detailed execution records.

## Contributing

Feel free to open issues or submit pull requests if you have improvements or encounter any bugs.

## License

This project is open-sourced under the MIT License.
