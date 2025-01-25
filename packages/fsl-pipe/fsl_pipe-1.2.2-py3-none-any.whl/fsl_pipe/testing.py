"""Helper functions for testing."""
import os
from .job import JobList
from rich.console import Console
import io


def touch(path):
    """Create a new dummy file at path."""
    with open(path, 'a'):
        os.utime(path, None)


def rich_report(jobs: JobList):
    """Get the rich jobs report as a string."""
    console = Console(file=io.StringIO(), width=800)
    jobs.report(console)
    return console.file.getvalue()
