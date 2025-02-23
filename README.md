# AWS Prefix List Utilities

## Overview
`plutils.py` is a modular, extensible Python CLI tool for interacting with **AWS Managed Prefix Lists** (PLs). It provides three primary subcommands:

- **search**: Look up prefix list entries by IP or description.  
- **audit**: Identify large CIDR blocks in customer-managed PLs.  
- **list**: Retrieve a list of customer-managed PLs, with flexible filtering.  

This tool uses **boto3** and **botocore** under the hood and supports AWS CLI profiles for multi-account environments.

---

## Features

- **Modular Architecture**  
  Code is organized into separate modules under `modules/`:  
  - `aws_helpers.py`: AWS session helpers and prefix list retrieval/filtering.  
  - `search_pl.py`: Functions for searching PL entries.  
  - `audit_pl.py`: Functions to filter PL entries by CIDR size.  
  - `list_pl.py`: Functions to list and filter prefix lists.  
  - `utils.py`: Logging setup and CSV export utilities.

- **Customer-Managed PL Focus**  
  Restricts operations to prefix lists owned by the AWS account (though you can tweak to include vendor or shared lists if needed).

- **Filtering Options**  
  - `--plfilter` to include only PLs whose names contain a specific substring.  
  - `--plexclude` to exclude any PLs whose names contain a specified substring.

- **CSV Output**  
  Most subcommands support `--csv [filename]` to export results in a structured CSV format.

- **Robust Logging**  
  - Always writes logs to `logs/` (unique file per run).  
  - Console logging can be toggled with `-v/--verbose`.

- **PEP 8 Compliant**  
  Code is kept tidy and consistent with Python best practices.

---

## Installation & Requirements

1. **Python 3.6+**  
2. **AWS CLI** configured with valid credentials or environment variables.  
3. Install dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional) **Virtual Environment**:  
   If you prefer isolation, create a venv:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Usage

Run the CLI entry point:
```bash
python plutils.py <subcommand> [options]
```

### Subcommands

#### 1. **search**
Search for entries by description or CIDR:
```bash
python plutils.py search     --name "internal"     --plfilter "Prod"     --csv
```
**Options**:  
- `--name` (searches `Description` field)  
- `--ip` (searches `Cidr` field)  
- `--plfilter`, `--plexclude`  
- `--profile`, `--region` (AWS settings)  
- `--csv [optional_filename]`  

#### 2. **audit**
Identify CIDR blocks larger than the specified prefix:
```bash
python plutils.py audit     --maxcidr /28     --plfilter "Corp"
```
**Options**:  
- `--maxcidr`: e.g., `/29` or `29`  
- Common filters: `--plfilter`, `--plexclude`  
- AWS config: `--profile`, `--region`  
- `--csv [filename]`

#### 3. **list**
List customer-managed prefix lists, optionally filtered by name:
```bash
python plutils.py list --plexclude "Old"
```
**Options**:  
- `--plfilter`, `--plexclude`  
- AWS config: `--profile`, `--region`  
- `--csv [filename]`

---

## Logging
- **File Logging**: Always logs to `logs/plutils_<subcommand>-<timestamp>.log`.  
- **Console Logging**: Set `-v/--verbose` to see INFO messages; otherwise only CRITICAL logs appear.  

---

## Testing
We use the standard `unittest` framework. All test files are located under `tests/`. Run them with:
```bash
python -m unittest discover -s tests
```
Tests cover:
- **AWS Helpers** (`test_aws_helpers.py`)  
- **Search Logic** (`test_search_pl.py`)  
- **Audit Logic** (`test_audit_pl.py`)  
- **List Logic** (`test_list_pl.py`)  
- **Utilities & Logging** (`test_utils.py`, `test_logging.py`)

Before committing, verify tests pass and lint with `pylint` or similar to maintain code quality.

---

## Contributing
1. Fork or clone this repository.  
2. Create a feature branch.  
3. Update and add tests where appropriate.  
4. Submit a pull request with a clear description of changes.

---

## License
This project is licensed under the [MIT License](LICENSE) — see the `LICENSE` file for details.
