import unittest
import logging
from modules.utils import setup_logging

class TestLoggingSetup(unittest.TestCase):
    def setUp(self):
        # Reset logging handlers before each test.
        logger = logging.getLogger()
        logger.handlers = []

    def test_setup_logging_verbose(self):
        # When verbose is True, the console handler should be set to INFO level.
        logfile = setup_logging(verbose=True, filename_prefix="test_verbose")
        # Find all StreamHandlers in the logger
        stream_handlers = [h for h in logging.getLogger().handlers if isinstance(h, logging.StreamHandler)]
        self.assertTrue(stream_handlers, "No stream handler found")
        for handler in stream_handlers:
            self.assertEqual(handler.level, logging.INFO, "Console handler level should be INFO when verbose is True")

    def test_setup_logging_non_verbose(self):
        # When verbose is False, the console handler should be set to CRITICAL level.
        logfile = setup_logging(verbose=False, filename_prefix="test_nonverbose")
        # Find all StreamHandlers in the logger
        stream_handlers = [h for h in logging.getLogger().handlers if isinstance(h, logging.StreamHandler)]
        self.assertTrue(stream_handlers, "No stream handler found")
        for handler in stream_handlers:
            self.assertEqual(handler.level, logging.CRITICAL, "Console handler level should be CRITICAL when verbose is False")

if __name__ == '__main__':
    unittest.main()

