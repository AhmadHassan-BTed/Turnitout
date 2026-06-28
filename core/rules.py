import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_DIR = os.path.join(BASE_DIR, "rules")

def load_rules():
    """
    Loads synonyms, phrase rewrites, and protected terms from rules/ folder.
    Fails with a clean error if rules files are missing or corrupted.
    """
    synonyms_path = os.path.join(RULES_DIR, "synonyms.json")
    phrases_path = os.path.join(RULES_DIR, "phrases.json")
    protected_path = os.path.join(RULES_DIR, "protected_terms.json")

    # Verify that files exist
    for path in [synonyms_path, phrases_path, protected_path]:
        if not os.path.exists(path):
            print(f"  ERROR: Required rules file not found: {path}")
            print("  Please make sure you have checked out the 'rules/' directory.")
            sys.exit(1)

    # 1. Academic Synonyms
    with open(synonyms_path, 'r', encoding='utf-8') as f:
        try:
            synonyms = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  ERROR: Invalid JSON format in '{synonyms_path}': {e}")
            sys.exit(1)

    # 2. Phrase Rewrites
    with open(phrases_path, 'r', encoding='utf-8') as f:
        try:
            phrases = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  ERROR: Invalid JSON format in '{phrases_path}': {e}")
            sys.exit(1)
    # Convert list of lists back to list of tuples for the regex engine
    phrases = [(item[0], item[1]) for item in phrases]

    # 3. Protected Terms
    with open(protected_path, 'r', encoding='utf-8') as f:
        try:
            protected_list = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  ERROR: Invalid JSON format in '{protected_path}': {e}")
            sys.exit(1)
    protected_terms = set(protected_list)

    return synonyms, phrases, protected_terms

# Load rules dynamically on import
ACADEMIC_SYNONYMS, PHRASE_REWRITES, PROTECTED_TERMS = load_rules()
