import unittest
import os
import tempfile
from modules.utils import write_csv_report

class TestUtils(unittest.TestCase):
    def test_write_csv_report(self):
        header = ["A", "B", "C"]
        data_rows = [
            [1, 2, 3],
            [4, 5, 6]
        ]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp_filename = tmp.name
        try:
            write_csv_report(tmp_filename, header, data_rows)
            with open(tmp_filename, "r") as f:
                content = f.read()
            self.assertIn("A,B,C", content)
            self.assertIn("1,2,3", content)
            self.assertIn("4,5,6", content)
        finally:
            os.remove(tmp_filename)

if __name__ == '__main__':
    unittest.main()

