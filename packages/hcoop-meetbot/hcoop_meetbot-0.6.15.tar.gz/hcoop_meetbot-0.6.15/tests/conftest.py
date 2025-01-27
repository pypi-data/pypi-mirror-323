import os
import time


# pylint: disable=unused-argument:
def pytest_sessionstart(session):
    """Explicitly set the UTC timezone for all tests."""
    os.environ["TZ"] = "UTC"
    time.tzset()
