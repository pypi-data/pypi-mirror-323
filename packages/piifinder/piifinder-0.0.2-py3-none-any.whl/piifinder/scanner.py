# piifinder/scanner.py

import os
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

def scan_and_anonymize_directory(root_path, anonymize=False):
    """
    Recursively scan and (optionally) anonymize files under `root_path`.
    """
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    valid_extensions = {".py", ".txt", ".md", ".log"}

    for root, dirs, files in os.walk(root_path):
        for file_name in files:
            if file_name.startswith('.'):
                continue

            _, ext = os.path.splitext(file_name)
            if ext.lower() in valid_extensions:
                full_path = os.path.join(root, file_name)
                scan_and_anonymize_file(full_path, analyzer, anonymizer, anonymize)

def scan_and_anonymize_file(file_path, analyzer, anonymizer, anonymize):
    """Analyze a single file for PII. Optionally anonymize its contents."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    except Exception as e:
        print(f"Could not read {file_path}: {e}")
        return

    # 1) Analyze text for PII
    results = analyzer.analyze(text=text, entities=[], language="en")
    if not results:
        print(f"No PII found in: {file_path}")
        return

    # 2) Report PII
    print(f"\n[PII FOUND] in: {file_path}")
    for r in results:
        snippet = text[r.start : r.end]
        print(f" - Entity: {r.entity_type}, Text: '{snippet}', Score: {r.score:.2f}")

    if anonymize:
        # 3) Anonymize the text
        anonymized_text = anonymizer.anonymize(
            text=text,
            analyzer_results=results
        )
        # For demonstration, write anonymized text to a new file
        anonymized_path = file_path + ".anonymized"
        try:
            with open(anonymized_path, 'w', encoding='utf-8') as out_f:
                out_f.write(anonymized_text.text)
            print(f"Anonymized file created at: {anonymized_path}")
        except Exception as e:
            print(f"Could not write anonymized file: {e}")
