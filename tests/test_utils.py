"""
Module: test_utils.py
Unit tests for utility functions in the utils module.
"""

import unittest
import os
import tempfile
from modules.utils import write_csv_report


class TestUtils(unittest.TestCase):
    """Unit tests for the CSV report writing functionality in utils.py."""

    def setUp(self):
        """
        Create a temporary directory for reports and ensure
        the 'reports' directory exists.
        """
        self.reports_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def tearDown(self):
        """
        Remove temporary CSV files created during tests.
        """
        for filename in os.listdir(self.reports_dir):
            if filename.startswith("test_report"):
                file_path = os.path.join(self.reports_dir, filename)
                try:
                    os.remove(file_path)
                except OSError:
                    pass

    def test_write_csv_report(self):
        """
        Test that the CSV report is correctly written with
        the specified header and data rows.
        """
        header = ["A", "B", "C"]
        data_rows = [
            [1, 2, 3],
            [4, 5, 6],
        ]
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".csv",
            dir=self.reports_dir, mode="w", encoding="utf-8"
        ) as tmp_file:
            tmp_filename = os.path.basename(tmp_file.name)

        write_csv_report(tmp_filename, header, data_rows)
        csv_filepath = os.path.join(self.reports_dir, tmp_filename)

        self.assertTrue(
            os.path.exists(csv_filepath),
            "CSV file was not created."
        )

        with open(csv_filepath, "r", encoding="utf-8") as csv_file:
            content = csv_file.read()

        self.assertIn("A,B,C", content, "CSV header is missing or incorrect.")
        self.assertIn("1,2,3", content, "CSV content is missing or incorrect.")

        # Cleanup
        os.remove(csv_filepath)


if __name__ == '__main__':
    unittest.main()