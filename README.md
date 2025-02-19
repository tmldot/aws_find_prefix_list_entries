# AWS Prefix List Utilities

## Overview

`plutils.py` is a modular and extensible Python CLI tool for managing AWS Managed Prefix Lists (PLs).  
It provides three key functionalities:
- **Search**: Look up prefix list entries by IP or name.
- **Audit**: Identify large CIDR blocks in customer-managed PLs.
- **List**: Retrieve all customer-managed prefix lists, filtered by name or description.

This tool is designed to work across AWS environments using AWS CLI profiles.

---

## Features

- **Fully Modular**: Uses distinct modules (`search`, `audit`, `list`) for each function.
- **Customer-Managed Prefix Lists**: Restricts operations to PLs managed within the AWS account.
- **Flexible Filtering**:  
  - `--plfilter` to include specific PLs based on name.
  - `--plexclude` to exclude PLs from results.
- **IP & Name Searches**: Perform case-insensitive searches within PL descriptions or CIDR entries.
- **CIDR Auditing**: Identify any CIDR blocks larger than a specified subnet mask.
- **CSV Output**: Export results in structured CSV format for further analysis.
- **Profile & Region Selection**: Works with AWS CLI profiles for multiple account support.
- **Logging Improvements**:  
  - Logs are always written to `logs/`.
  - Console output is minimal by default; use `-v/--verbose` for detailed output.

---

## Installation & Requirements

- Python 3.6+
- AWS CLI configured with appropriate credentials
- Install dependencies:
  ```bash
  pip install -r requirements.txt
