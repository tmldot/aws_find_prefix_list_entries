# AWS Prefix List Utilities

## Overview

This repository provides a modular Python CLI tool for working with AWS Managed Prefix Lists (PLs). The script `plutils.py` consolidates multiple functionalities, allowing you to search, audit, and report on prefix list entries by IP address, partner name, or CIDR range.

## Structure

The tool is built with an extensible architecture:

```
plutils.py         # Main CLI entrypoint
modules/
├── aws_helpers.py # AWS API calls: describe prefix lists, get entries, etc.
├── search.py      # Implements searching/filtering by name or IP
├── audit.py       # Implements CIDR size filtering (audit functionality)
└── utils.py       # Logging, CSV report writing, and common utilities
README.md
```

## Features

- **Search AWS Prefix Lists by Name or IP**  
  Search for entries based on `Description` (case-insensitive) or `Cidr` (supports partial matches).

- **Filter Prefix Lists by Name**  
  Use `--plfilter` to restrict searches to only those PLs containing a specific term.

- **Exclude Specific Prefix Lists**  
  Use `--plexclude` to ignore PLs containing a given term.

- **Audit Prefix Lists by CIDR Size**  
  Use `--maxcidr` to specify the maximum CIDR block allowed. Any entry larger than this is reported.

- **Specify AWS Profile and Region**  
  Optionally target specific AWS accounts or regions using AWS CLI profiles.

- **Quiet Mode for Logging**  
  Suppress intermediate output while still maintaining detailed log files.

- **CSV Export**  
  Generate a CSV report with the format: `PLID, PLName, Cidr, Description`.

## Usage

### **Search by Name (in Description field)**
```bash
./plutils.py --name "ExampleVendor"
```

### **Search by IP (supports partial match)**
```bash
./plutils.py --ip "192.168.1"
```

### **Filter Prefix Lists by Name (only check PLs containing "ExampleVendor")**
```bash
./plutils.py --name "ExampleVendor" --plfilter "ExampleVendor"
```

### **Exclude Prefix Lists by Name (ignore PLs containing "Deprecated")**
```bash
./plutils.py --plexclude "Deprecated"
```

### **Find all IP blocks larger than `/29` (default)**
```bash
./plutils.py --maxcidr /29
```

### **Find all IP blocks larger than `/28`**
```bash
./plutils.py --maxcidr /28
```

### **Specify AWS Profile and Region**
```bash
./plutils.py --profile myprofile --region us-east-1
```

### **Quiet Mode (only logs critical messages to console)**
```bash
./plutils.py --quiet
```

### **Export Results to CSV**
```bash
./plutils.py --csv results.csv
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

The script generates timestamped log files in the working directory (e.g., `plutils-20250218_123456.log`). These logs provide detailed execution records.

## Extending the Tool

This tool is modular and extensible. You can add additional functionality by placing new scripts inside the `modules/` directory and updating `plutils.py` to import and integrate them.

### Example Modules:

- **`aws_helpers.py`** - Handles AWS API interactions for fetching prefix lists and their entries.
- **`search.py`** - Provides search/filtering capabilities for name/IP-based lookups.
- **`audit.py`** - Handles CIDR size filtering for security/audit use cases.
- **`utils.py`** - Manages logging, CSV generation, and common functions.

## Contributing

Feel free to open issues or submit pull requests if you have improvements or encounter any bugs.

## License

This project is open-sourced under the MIT License.
