# piifinder/cli.py

import argparse
from .scanner import scan_directory

def main():
    parser = argparse.ArgumentParser(
        prog="piifinder",
        description="Scan directories/files for PII with Microsoft Presidio."
    )
    subparsers = parser.add_subparsers(dest="command")

    # "scan" subcommand
    scan_parser = subparsers.add_parser("scan", help="Scan a directory for PII.")
    scan_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to scan (defaults to current directory)."
    )

    args = parser.parse_args()

    if args.command == "scan":
        scan_directory(args.path)
    else:
        # If no subcommand was given, just show the help
        parser.print_help()
