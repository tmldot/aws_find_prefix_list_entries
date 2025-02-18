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
  ```

## Usage

Run the script using Python. Below are some usage examples:

### Search by Name

Search for entries where the description contains the term "ExampleVendor":
```bash
./find_prefix_entries.py --name "ExampleVendor"
```

### Search by IP

Search for entries matching a partial IP, e.g., "192.168.1":
```bash
./find_prefix_entries.py --ip "192.168.1"
```

### Specify AWS Profile and Region

Use a specific AWS CLI profile and region:
```bash
./find_prefix_entries.py --name "ExampleVendor" --profile myprofile --region us-east-1
```

### Quiet Mode

Suppress intermediate console output (only critical messages are shown, with full logging in the log file):
```bash
./find_prefix_entries.py --name "ExampleVendor" --quiet
```

### CSV Output

Export the results to a CSV file. If no filename is provided, a default one is generated:
```bash
./find_prefix_entries.py --name "ExampleVendor" --csv
```
Or, specify a filename:
```bash
./find_prefix_entries.py --ip "192.168.1" --csv myreport.csv
```

## Logging

The script generates a timestamped log file (e.g., `prefixlist_search-examplevendor-20250218_123456.log`) in the working directory. This file contains detailed logging information of the execution.

## Contributing

Feel free to open issues or submit pull requests if you have improvements or encounter any bugs.

## License

This project is open-sourced under the MIT License.
