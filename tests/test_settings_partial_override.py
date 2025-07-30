"""
Test settings module for testing fallback mechanism.

This module only overrides some settings to test that the rest
fallback to wbweb defaults properly.
"""

# Only override some settings - test fallback for the rest
DEBUG = True
CUSTOM_SETTING = 'from_test_child_project'
APP_NAME = 'Test Fallback Application'