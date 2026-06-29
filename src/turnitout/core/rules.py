import os
import json
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RULES_DIR = os.path.join(BASE_DIR, "rules")

def load_rules():
    """
    Loads synonyms, phrase rewrites, protected terms, and helper tables from rules/ folder.
    Fails with a clean error if rules files are missing or corrupted.
    """
    synonyms_path = os.path.join(RULES_DIR, "synonyms.json")
    phrases_path = os.path.join(RULES_DIR, "phrases.json")
    protected_path = os.path.join(RULES_DIR, "protected_terms.json")
    hedge_path = os.path.join(RULES_DIR, "hedge_words.json")
    determiners_path = os.path.join(RULES_DIR, "determiners.json")
    conjunctions_path = os.path.join(RULES_DIR, "conjunctions.json")
    
    # New stage tables
    passive_verbs_path = os.path.join(RULES_DIR, "passive_verbs.json")
    transition_phrases_path = os.path.join(RULES_DIR, "transition_phrases.json")
    verb_noun_pairs_path = os.path.join(RULES_DIR, "verb_noun_pairs.json")
    appositives_path = os.path.join(RULES_DIR, "appositives.json")
    discourse_markers_path = os.path.join(RULES_DIR, "discourse_markers.json")
    contractions_path = os.path.join(RULES_DIR, "contractions.json")

    # Verify that files exist
    required_paths = [
        synonyms_path, phrases_path, protected_path,
        hedge_path, determiners_path, conjunctions_path,
        passive_verbs_path, transition_phrases_path,
        verb_noun_pairs_path, appositives_path, discourse_markers_path,
        contractions_path
    ]
    for path in required_paths:
        if not os.path.exists(path):
            print(f"  ERROR: Required rules file not found: {path}")
            print("  Please make sure you have checked out the 'rules/' directory.")
            sys.exit(1)

    # Helper function to load JSON safely
    def load_json_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                print(f"  ERROR: Invalid JSON format in '{file_path}': {e}")
                sys.exit(1)

    # 1. Academic Synonyms
    synonyms = load_json_file(synonyms_path)

    # 2. Phrase Rewrites
    phrases_list = load_json_file(phrases_path)
    phrases = [(item[0], item[1]) for item in phrases_list]

    # 3. Protected Terms
    protected_list = load_json_file(protected_path)
    protected_terms = set(protected_list)

    # 4. Hedge Words
    hedge_words = load_json_file(hedge_path)

    # 5. Determiners Map
    determiner_map = load_json_file(determiners_path)

    # 6. Conjunctions List
    conjunctions = load_json_file(conjunctions_path)

    # 7. Passive Verbs Map
    passive_verbs = load_json_file(passive_verbs_path)

    # 8. Transition Phrases
    transition_phrases = load_json_file(transition_phrases_path)

    # 9. Verb Noun Pairs
    verb_noun_pairs = load_json_file(verb_noun_pairs_path)

    # 10. Appositive Map
    appositive_map = load_json_file(appositives_path)

    # 11. Discourse Markers
    discourse_markers = load_json_file(discourse_markers_path)

    # 12. Contractions
    contractions = load_json_file(contractions_path)

    return (synonyms, phrases, protected_terms, hedge_words, determiner_map, conjunctions,
            passive_verbs, transition_phrases, verb_noun_pairs, appositive_map, discourse_markers, contractions)

# Load rules dynamically on import
(ACADEMIC_SYNONYMS, PHRASE_REWRITES, PROTECTED_TERMS, HEDGE_WORDS, DETERMINER_MAP, SUBORDINATE_CONJUNCTIONS,
 PASSIVE_VERB_MAP, TRANSITION_PHRASES, VERB_NOUN_PAIRS, APPOSITIVE_MAP, DISCOURSE_MARKER_VARIANTS, CONTRACTIONS) = load_rules()
