import unittest
import os
import shutil
from modules.utils import write_csv_report

class TestUtils(unittest.TestCase):
    def setUp(self):
        # Ensure the reports directory exists and is empty for testing
        self.reports_dir = "reports"
        if os.path.exists(self.reports_dir):
            shutil.rmtree(self.reports_dir)
        os.makedirs(self.reports_dir, exist_ok=True)

    def tearDown(self):
        # Cleanup reports directory after test
        if os.path.exists(self.reports_dir):
            shutil.rmtree(self.reports_dir)

    def test_write_csv_report(self):
        header = ["A", "B", "C"]
        data_rows = [
            [1, 2, 3],
            [4, 5, 6]
        ]
        # Specify a test CSV filename (without directory)
        csv_filename = "test_report.csv"
        # Call the function, which writes the file into the "reports" directory
        write_csv_report(csv_filename, header, data_rows)
        
        # Construct the full path to the CSV file
        full_path = os.path.join(self.reports_dir, csv_filename)
        # Check that the file exists
        self.assertTrue(os.path.exists(full_path))
        
        # Read the content and check for expected values
        with open(full_path, "r") as f:
            content = f.read()
        self.assertIn("A,B,C", content)
        self.assertIn("1,2,3", content)
        self.assertIn("4,5,6", content)

if __name__ == '__main__':
    unittest.main()

