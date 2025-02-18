import logging
import csv
from datetime import datetime

def setup_logging(quiet=False, filename_prefix="plutils"):
    """
    Set up logging to file and console. Returns the log file name.
    
    :param quiet: If True, suppress console output.
    :param filename_prefix: Prefix for the log file name.
    :return: The generated log file name.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = f"{filename_prefix}-{timestamp}.log"
    
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
    
    :param csv_filename: Output CSV file name.
    :param header: List of column headers.
    :param data_rows: List of data rows (each row is a list).
    """
    try:
        with open(csv_filename, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)
            for row in data_rows:
                writer.writerow(row)
        logging.info(f"CSV report written to {csv_filename}")
    except Exception as e:
        logging.error(f"Failed to write CSV report: {e}")

