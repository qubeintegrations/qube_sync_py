#!/usr/bin/env python3
"""
Test runner script for QubeSync tests.
Usage: python run_tests.py [--verbose] [--specific-test TEST_NAME]
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Change to the project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Use the virtual environment python
    python_exe = "./bin/python"
    
    # Check if virtual environment python exists
    if not Path(python_exe).exists():
        print("Virtual environment not found. Please set up the virtual environment first.")
        print("Run: python3 -m venv .")
        sys.exit(1)
    
    # Set default environment variables for tests
    os.environ.setdefault("QUBE_API_KEY", "test_api_key")
    os.environ.setdefault("QUBE_WEBHOOK_SECRET", "supersecret")
    
    # Build pytest command
    cmd = [python_exe, "-m", "pytest", "tests/"]
    
    # Parse command line arguments
    if "--verbose" in sys.argv or "-v" in sys.argv:
        cmd.append("-v")
    
    if "--qubesync-only" in sys.argv:
        cmd = [python_exe, "-m", "pytest", "tests/test_qube_sync.py"]
        if "--verbose" in sys.argv or "-v" in sys.argv:
            cmd.append("-v")
    
    if "--request-builder-only" in sys.argv:
        cmd = [python_exe, "-m", "pytest", "tests/test_request_builder.py"]
        if "--verbose" in sys.argv or "-v" in sys.argv:
            cmd.append("-v")
    
    if "--specific-test" in sys.argv:
        try:
            test_index = sys.argv.index("--specific-test") + 1
            test_name = sys.argv[test_index]
            cmd.append(f"-k {test_name}")
        except (IndexError, ValueError):
            print("Error: --specific-test requires a test name")
            sys.exit(1)
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        print("\nOptions:")
        print("  --verbose, -v           Show detailed test output")
        print("  --qubesync-only         Run only QubeSync tests")
        print("  --request-builder-only  Run only RequestBuilder tests")
        print("  --specific-test TEST    Run a specific test by name")
        print("\nAvailable tests:")
        # Run pytest to list tests
        list_cmd = [python_exe, "-m", "pytest", "tests/", "--collect-only", "-q"]
        subprocess.run(list_cmd)
        return
    
    # Run the tests
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
