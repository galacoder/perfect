#!/usr/bin/env python3
"""
Upload Kestra flows to production instance via API
Usage: python3 upload_flows.py
"""

import os
import sys
import glob
import requests
from pathlib import Path
from getpass import getpass

# Configuration
KESTRA_URL = "https://kestra.galatek.dev"
FLOWS_DIR = Path(__file__).parent / "flows"

def upload_flow(session, flow_path):
    """Upload a single flow file"""
    with open(flow_path, 'r') as f:
        flow_content = f.read()

    response = session.post(
        f"{KESTRA_URL}/api/v1/flows",
        headers={"Content-Type": "application/x-yaml"},
        data=flow_content,
        verify=True  # Verify SSL certificate
    )

    return response

def main():
    print("Kestra Flow Upload Script")
    print(f"Target: {KESTRA_URL}")
    print()

    # Get credentials
    username = os.getenv("KESTRA_USER")
    password = os.getenv("KESTRA_PASS")

    if not username:
        username = input("Kestra username (or set KESTRA_USER env var): ").strip()
        if not username:
            print("Error: Username is required")
            sys.exit(1)

    if not password:
        password = getpass("Kestra password (or set KESTRA_PASS env var): ").strip()
        if not password:
            print("Error: Password is required")
            sys.exit(1)

    # Create session with authentication
    session = requests.Session()
    session.auth = (username, password)

    # Find all flow files
    flow_files = sorted(glob.glob(str(FLOWS_DIR / "**/*.yml"), recursive=True))

    if not flow_files:
        print(f"Error: No flow files found in {FLOWS_DIR}")
        sys.exit(1)

    print(f"Found {len(flow_files)} flow files")
    print()

    # Upload each flow
    success = 0
    failed = 0

    for i, flow_path in enumerate(flow_files, 1):
        relative_path = Path(flow_path).relative_to(FLOWS_DIR)
        print(f"[{i}/{len(flow_files)}] Uploading: {relative_path}")

        try:
            response = upload_flow(session, flow_path)

            if response.status_code in [200, 201]:
                print(f"  ✓ Success (HTTP {response.status_code})")
                success += 1
            else:
                print(f"  ✗ Failed (HTTP {response.status_code})")
                print(f"  Error: {response.text[:200]}")
                failed += 1

        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            failed += 1

        print()

    # Summary
    print("=" * 50)
    print(f"Upload Summary:")
    print(f"  Total:   {len(flow_files)}")
    print(f"  Success: {success}")
    print(f"  Failed:  {failed}")
    print("=" * 50)

    if failed == 0:
        print("All flows uploaded successfully!")
        sys.exit(0)
    else:
        print("Some flows failed to upload")
        sys.exit(1)

if __name__ == "__main__":
    main()
