"""
Module: utils.py
Provides utility functions for logging setup and CSV report writing.
"""

import os
import logging
import csv
from datetime import datetime

def setup_logging(verbose=False, filename_prefix="plutils"):
    """
    Set up logging to file and console. Returns the log file name.
    Log files are stored in the "logs" subdirectory.
    By default, console logging is suppressed (only critical messages are shown).
    Use the verbose flag to enable screen logging.

    :param verbose: Boolean flag to enable console logging.
    :param filename_prefix: Prefix for the log file name.
    :return: The generated log file name.
    """
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(logs_dir, "{}-{}.log".format(filename_prefix, timestamp))
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # File handler always active
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO)
    # Console handler: level set based on verbose flag
    ch = logging.StreamHandler()
    if verbose:
        ch.setLevel(logging.INFO)
    else:
        ch.setLevel(logging.CRITICAL)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logging.info("Logging initiated. Output log file: %s", logfile)
    return logfile

def write_csv_report(csv_filename, header, data_rows):
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