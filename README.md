# aws_find_prefix_list_entries

## Overview

`aws_find_prefix_list_entries` is a Python CLI tool designed to search AWS Managed Prefix List entries based on a search term. Whether you want to find entries by a substring in the description (e.g., a vendor name) or by matching IP address segments, this tool provides a detailed report and can export results in CSV format for further processing.

## Features

- **Search by Name or IP:**  
  Choose to search by the `Description` field (case-insensitive) or by the `Cidr` field (supports partial IP matching).

- **Custom AWS Profile and Region:**  
  Optionally specify an AWS CLI profile and region to target specific accounts or regions.

- **Quiet Mode:**  
  Suppress intermediate console output while still logging detailed operations to a log file.

- **CSV Export:**  
  Export the final report to CSV with columns for PLID, PLName, Cidr, and Description.

- **Timestamped Logging:**  
  Automatically generates log files with a timestamp and normalized search term.

## Requirements

- Python 3.6+
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)  
  Install via pip:
  ```bash
  pip install boto3

