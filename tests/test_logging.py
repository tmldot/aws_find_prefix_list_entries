import unittest
import logging
import sys
from modules.utils import setup_logging

class TestLoggingSetup(unittest.TestCase):
    def setUp(self):
        # Clear all existing handlers before each test
        logger = logging.getLogger()
        logger.handlers = []

    def test_setup_logging_verbose(self):
        # When verbose is True, console logging should be enabled (INFO level)
        logfile = setup_logging(verbose=True, filename_prefix="test_verbose")
        # Filter for console handlers (exclude FileHandlers)
        stream_handlers = [
            h for h in logging.getLogger().handlers 
            if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        ]
        self.assertTrue(stream_handlers, "No console stream handler found")
        for handler in stream_handlers:
            self.assertEqual(handler.level, logging.INFO, "Console handler level should be INFO when verbose is True")

    def test_setup_logging_non_verbose(self):
        # When verbose is False, console logging should be suppressed (CRITICAL level)
        logfile = setup_logging(verbose=False, filename_prefix="test_nonverbose")
        # Filter for console handlers (exclude FileHandlers)
        stream_handlers = [
            h for h in logging.getLogger().handlers 
            if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        ]
        self.assertTrue(stream_handlers, "No console stream handler found")
        for handler in stream_handlers:
            self.assertEqual(handler.level, logging.CRITICAL, "Console handler level should be CRITICAL when verbose is False")

if __name__ == '__main__':
    unittest.main()

