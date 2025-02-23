"""
Module: test_logging.py
Unit tests for verifying logging setup functionality in modules/utils.py.
"""

import unittest
import logging
from modules.utils import setup_logging


class TestLoggingSetup(unittest.TestCase):
    """
    Unit tests for the setup_logging function in utils.py.
    """

    def setUp(self):
        """
        Remove existing logging handlers before each test to avoid collisions.
        """
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception as ex:
                logging.warning("Error closing handler: %s", ex)

    def tearDown(self):
        """
        Ensure all logging handlers are removed after each test.
        """
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception as ex:
                logging.warning("Error closing handler: %s", ex)

    def test_setup_logging_verbose(self):
        """
        Test that verbose logging sets console handler to INFO level.
        """
        _ = setup_logging(verbose=True, filename_prefix="test_verbose")
        stream_handlers = [
            h for h in logging.getLogger().handlers
            if hasattr(h, "stream") and not isinstance(h, logging.FileHandler)
        ]
        self.assertTrue(stream_handlers, "No console stream handler found.")
        for handler in stream_handlers:
            self.assertEqual(
                handler.level, logging.INFO,
                "Console handler level should be INFO when verbose=True."
            )

    def test_setup_logging_non_verbose(self):
        """
        Test that non-verbose logging sets console handler to CRITICAL level.
        """
        _ = setup_logging(verbose=False, filename_prefix="test_nonverbose")
        stream_handlers = [
            h for h in logging.getLogger().handlers
            if hasattr(h, "stream") and not isinstance(h, logging.FileHandler)
        ]
        self.assertTrue(stream_handlers, "No console stream handler found.")
        for handler in stream_handlers:
            self.assertEqual(
                handler.level, logging.CRITICAL,
                "Console handler level should be CRITICAL when verbose=False."
            )


if __name__ == '__main__':
    unittest.main()