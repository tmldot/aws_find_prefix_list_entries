import os
import logging
import csv
from datetime import datetime

def setup_logging(quiet=False, filename_prefix="plutils"):
    """
    Set up logging to file and console. Returns the log file name.
    Log files are stored in the "logs" subdirectory.
    """
    # Ensure the logs directory exists.
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(logs_dir, f"{filename_prefix}-{timestamp}.log")
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler()
    if quiet:
        ch.setLevel(logging.CRITICAL)
    else:
        ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    logging.info(f"Logging initiated. Output log file: {logfile}")
    return logfile

def write_csv_report(csv_filename, header, data_rows):
    """
    Write a CSV report with the given header and data rows.
    Reports are stored in the "reports" subdirectory.
    """
    # Ensure the reports directory exists.
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    csv_filepath = os.path.join(reports_dir, csv_filename)
    
    try:
        with open(csv_filepath, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            for row in data_rows:
                writer.writerow(row)
        logging.info(f"CSV report written to {csv_filepath}")
    except Exception as e:
        logging.error(f"Failed to write CSV report: {e}")

