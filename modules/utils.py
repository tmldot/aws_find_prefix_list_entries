"""
Module: utils.py
Provides utility functions for logging setup and CSV report writing.
"""

import os
import logging
import csv
from datetime import datetime
from typing import List


def setup_logging(verbose: bool = False, filename_prefix: str = "plutils") -> str:
    """
    Set up logging to file and console. Returns the log file name.
    Log files are stored in the "logs" subdirectory. By default,
    console logging is suppressed (only critical messages).
    Use the verbose flag to enable console logging.

    :param verbose: Boolean flag to enable console logging.
    :param filename_prefix: Prefix for the log file name.
    :return: The generated log file name.
    """
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(logs_dir, f"{filename_prefix}-{timestamp}.log")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler always active
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler: level set based on verbose flag
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO if verbose else logging.CRITICAL)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logging.info("Logging initiated. Output log file: %s", logfile)
    return logfile


def write_csv_report(csv_filename: str, header: List[str], data_rows: List[List[str]]) -> None:
    """
    Write a CSV report with the given header and data rows.
    Reports are stored in the "reports" subdirectory.

    :param csv_filename: Output CSV file name.
    :param header: List of column headers.
    :param data_rows: List of data rows (each row is a list).
    """
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    csv_filepath = os.path.join(reports_dir, csv_filename)

    try:
        with open(csv_filepath, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            for row in data_rows:
                writer.writerow(row)
        logging.info("CSV report written to %s", csv_filepath)
    except (OSError, csv.Error) as e:
        logging.error("Failed to write CSV report: %s", e)
