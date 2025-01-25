# piifinder/scanner.py

import os
from presidio_analyzer import AnalyzerEngine

def scan_directory(root_path):
    """
    Recursively scan all files under `root_path` for PII using Presidio.
    Only scans files with certain extensions by default.
    """
    analyzer = AnalyzerEngine()
    valid_extensions = {'.py', '.txt', '.md', '.log'}

    for root, dirs, files in os.walk(root_path):
        for file_name in files:
            # Skip hidden files or those that start with '.'
            if file_name.startswith('.'):
                continue

            _, ext = os.path.splitext(file_name)
            if ext.lower() in valid_extensions:
                full_path = os.path.join(root, file_name)
                analyze_file(full_path, analyzer)

def analyze_file(file_path, analyzer):
    """Analyze a single file with Presidio for PII."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    except Exception as e:
        print(f"Could not read {file_path}: {e}")
        return

    # Analyze text
    results = analyzer.analyze(text=text, entities=[], language="en")
    if results:
        print(f"\n[PII FOUND] in: {file_path}")
        for r in results:
            snippet = text[r.start:r.end]
            print(f" - Entity: {r.entity_type}, Text: {snippet}, Score: {r.score:.2f}")
    else:
        print(f"No PII found in: {file_path}")
