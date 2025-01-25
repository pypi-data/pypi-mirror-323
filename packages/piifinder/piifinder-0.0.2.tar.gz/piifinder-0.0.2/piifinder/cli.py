# piifinder/cli.py

import argparse
from .scanner import scan_and_anonymize_directory

def main():
    parser = argparse.ArgumentParser(
        prog="piifinder",
        description="Scan directories/files for PII (optionally anonymize) using Presidio."
    )
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Scan a directory for PII.")
    scan_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to scan (defaults to current directory)"
    )
    scan_parser.add_argument(
        "--anonymize",
        action="store_true",
        help="If set, anonymize PII in the scanned files"
    )

    args = parser.parse_args()

    if args.command == "scan":
        scan_and_anonymize_directory(args.path, anonymize=args.anonymize)
    else:
        parser.print_help()
