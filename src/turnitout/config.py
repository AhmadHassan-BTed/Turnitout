import os
import re
import sys
import json
from collections import OrderedDict, defaultdict
from dotenv import load_dotenv

# Resolve root directory relative to this file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def validate_config_contract(data, config_path):
    """
    Validates that data contains all required keys with the expected types.
    """
    required_keys = {
        "project_name": str,
        "input_dir": str,
        "tex_file": str,
        "bib_file": str,
        "output_dir": str,
        "synonym_aggressiveness": (int, float),
        "random_seed": int,
        "min_sentence_length_for_cite": int,
        "max_citations_to_insert": int,
        "enable_voice_transform": bool,
        "voice_transform_rate": (int, float),
        "enable_sentence_fusion": bool,
        "sentence_fusion_rate": (int, float),
        "enable_transition_inject": bool,
        "transition_inject_rate": (int, float),
        "enable_word_reorder": bool,
        "word_reorder_rate": (int, float),
        "enable_nominalization": bool,
        "nominalization_rate": (int, float),
        "enable_appositive": bool,
        "appositive_rate": (int, float),
        "enable_discourse_rotate": bool,
        "discourse_rotate_rate": (int, float),
        "enable_contraction": bool,
        "contraction_rate": (int, float),
        "enable_ngram_audit": bool,
        "enable_risk_citation": bool,
        "enable_info_reorder": bool,
        "info_reorder_rate": (int, float),
        "enable_conceptual_bridge": bool,
        "conceptual_bridge_rate": (int, float),
        "topic_citations": list,
    }

    errors = []

    for key, expected_type in required_keys.items():
        if key not in data:
            errors.append(f"Missing required key: '{key}'")
            continue

        value = data[key]
        
        # Check type
        if isinstance(expected_type, tuple):
            if not isinstance(value, expected_type) or isinstance(value, bool):  # bool is subclass of int in Python
                type_names = " or ".join(t.__name__ for t in expected_type)
                errors.append(f"Key '{key}' must be of type {type_names}, got {type(value).__name__}")
        else:
            if not isinstance(value, expected_type) or (expected_type is not bool and isinstance(value, bool)):
                errors.append(f"Key '{key}' must be of type {expected_type.__name__}, got {type(value).__name__}")

    # Validate topic_citations items structure if it is a list
    if "topic_citations" in data and isinstance(data["topic_citations"], list):
        for idx, item in enumerate(data["topic_citations"]):
            if not isinstance(item, dict):
                errors.append(f"topic_citations[{idx}] must be a JSON object (dict), got {type(item).__name__}")
                continue
            for subkey in ["keywords", "key", "topic"]:
                if subkey not in item:
                    errors.append(f"topic_citations[{idx}] is missing subkey: '{subkey}'")
            if "keywords" in item and not isinstance(item["keywords"], list):
                errors.append(f"topic_citations[{idx}]['keywords'] must be a list, got {type(item['keywords']).__name__}")
            if "key" in item and not isinstance(item["key"], str):
                errors.append(f"topic_citations[{idx}]['key'] must be a string, got {type(item['key']).__name__}")
            if "topic" in item and not isinstance(item["topic"], str):
                errors.append(f"topic_citations[{idx}]['topic'] must be a string, got {type(item['topic']).__name__}")

    if errors:
        print("=" * 65)
        print(f"  CONFIGURATION CONTRACT VIOLATED in: {config_path}")
        print("=" * 65)
        for err in errors:
            print(f"  [Error] {err}")
        print("=" * 65)
        print("  Processing halted to prevent silent failure.")
        sys.exit(1)

def load_config_json(config_name):
    """
    Loads config details from configs/{config_name}.json.
    Supports either a config name (e.g. 'math_thesis') or a direct path to a JSON file.
    """
    if os.path.exists(config_name) and config_name.endswith('.json'):
        config_path = config_name
    else:
        config_path = os.path.join(BASE_DIR, "configs", f"{config_name}.json")

    if not os.path.exists(config_path):
        print(f"  ERROR: Configuration file not found at: {config_path}")
        print("  Please make sure you have checked out the 'configs/' directory.")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  ERROR: Invalid JSON format in '{config_path}': {e}")
            sys.exit(1)

    validate_config_contract(data, config_path)

    # Convert list of dicts to OrderedDict for topic citations
    topic_citations = OrderedDict()
    for item in data.get("topic_citations", []):
        keywords = tuple(item["keywords"])
        topic_citations[keywords] = {
            "key": item["key"],
            "topic": item["topic"]
        }

    # Environment variables override values if present
    aggressiveness = float(os.getenv("TURNITOUT_AGGRESSIVENESS", data.get("synonym_aggressiveness", 0.75)))
    seed = int(os.getenv("TURNITOUT_RANDOM_SEED", data.get("random_seed", 42)))
    min_cite_len = int(os.getenv("TURNITOUT_MIN_SENTENCE_LEN", data.get("min_sentence_length_for_cite", 45)))
    max_citations = int(os.getenv("TURNITOUT_MAX_CITATIONS", data.get("max_citations_to_insert", 30)))

    enable_voice = os.getenv("TURNITOUT_VOICE_TRANSFORM", str(data.get("enable_voice_transform", True))).lower() in ("true", "1", "yes")
    voice_rate = float(os.getenv("TURNITOUT_VOICE_RATE", data.get("voice_transform_rate", 0.30)))

    enable_fusion = os.getenv("TURNITOUT_SENTENCE_FUSION", str(data.get("enable_sentence_fusion", True))).lower() in ("true", "1", "yes")
    fusion_rate = float(os.getenv("TURNITOUT_FUSION_RATE", data.get("sentence_fusion_rate", 0.25)))

    enable_transition = os.getenv("TURNITOUT_TRANSITION_INJECT", str(data.get("enable_transition_inject", True))).lower() in ("true", "1", "yes")
    transition_rate = float(os.getenv("TURNITOUT_TRANSITION_RATE", data.get("transition_inject_rate", 0.25)))

    enable_reorder = os.getenv("TURNITOUT_WORD_REORDER", str(data.get("enable_word_reorder", True))).lower() in ("true", "1", "yes")
    reorder_rate = float(os.getenv("TURNITOUT_REORDER_RATE", data.get("word_reorder_rate", 0.20)))

    enable_nominal = os.getenv("TURNITOUT_NOMINALIZATION", str(data.get("enable_nominalization", True))).lower() in ("true", "1", "yes")
    nominal_rate = float(os.getenv("TURNITOUT_NOMINAL_RATE", data.get("nominalization_rate", 0.20)))

    enable_appositive = os.getenv("TURNITOUT_APPOSITIVE", str(data.get("enable_appositive", True))).lower() in ("true", "1", "yes")
    appositive_rate = float(os.getenv("TURNITOUT_APPOSITIVE_RATE", data.get("appositive_rate", 0.35)))

    enable_discourse = os.getenv("TURNITOUT_DISCOURSE_ROTATE", str(data.get("enable_discourse_rotate", True))).lower() in ("true", "1", "yes")
    discourse_rate = float(os.getenv("TURNITOUT_DISCOURSE_RATE", data.get("discourse_rotate_rate", 0.50)))

    enable_contraction = os.getenv("TURNITOUT_CONTRACTION", str(data.get("enable_contraction", True))).lower() in ("true", "1", "yes")
    contraction_rate = float(os.getenv("TURNITOUT_CONTRACTION_RATE", data.get("contraction_rate", 0.20)))

    enable_ngram_audit = os.getenv("TURNITOUT_NGRAM_AUDIT", str(data.get("enable_ngram_audit", True))).lower() in ("true", "1", "yes")
    enable_risk_citation = os.getenv("TURNITOUT_RISK_CITATION", str(data.get("enable_risk_citation", True))).lower() in ("true", "1", "yes")

    enable_info_reorder = os.getenv("TURNITOUT_INFO_REORDER", str(data.get("enable_info_reorder", True))).lower() in ("true", "1", "yes")
    info_reorder_rate = float(os.getenv("TURNITOUT_INFO_REORDER_RATE", data.get("info_reorder_rate", 0.20)))
    enable_conceptual_bridge = os.getenv("TURNITOUT_CONCEPTUAL_BRIDGE", str(data.get("enable_conceptual_bridge", True))).lower() in ("true", "1", "yes")
    conceptual_bridge_rate = float(os.getenv("TURNITOUT_CONCEPTUAL_BRIDGE_RATE", data.get("conceptual_bridge_rate", 0.20)))

    class ConfigNamespace:
        def __init__(self, d, tc, agg, sd, mcl, mc, ev, vr, ef, fr, et, tr, er, rr, en, nr, ea, ar, ed, dr, ec, cr, ena, erc, eir, irr, ecb, cbr):
            self.PROJECT_NAME = d["project_name"]
            
            # Resolve relative paths relative to BASE_DIR
            self.INPUT_DIR = os.path.normpath(os.path.join(BASE_DIR, d["input_dir"]))
            self.TEX_FILE = os.path.normpath(os.path.join(BASE_DIR, d["tex_file"]))
            self.BIB_FILE = os.path.normpath(os.path.join(BASE_DIR, d["bib_file"]))
            self.OUTPUT_DIR = os.path.normpath(os.path.join(BASE_DIR, d["output_dir"]))
            
            self.SYNONYM_AGGRESSIVENESS = agg
            self.RANDOM_SEED = sd
            self.MIN_SENTENCE_LENGTH_FOR_CITE = mcl
            self.MAX_CITATIONS_TO_INSERT = mc
            self.TOPIC_CITATIONS = tc
 
            self.ENABLE_VOICE_TRANSFORM = ev
            self.VOICE_TRANSFORM_RATE = vr
            self.ENABLE_SENTENCE_FUSION = ef
            self.SENTENCE_FUSION_RATE = fr
            self.ENABLE_TRANSITION_INJECT = et
            self.TRANSITION_INJECT_RATE = tr
            self.ENABLE_WORD_REORDER = er
            self.WORD_REORDER_RATE = rr
            self.ENABLE_NOMINALIZATION = en
            self.NOMINALIZATION_RATE = nr
            self.ENABLE_APPOSITIVE = ea
            self.APPOSITIVE_RATE = ar
            self.ENABLE_DISCOURSE_ROTATE = ed
            self.DISCOURSE_ROTATE_RATE = dr
            self.ENABLE_CONTRACTION = ec
            self.CONTRACTION_RATE = cr
            self.ENABLE_NGRAM_AUDIT = ena
            self.ENABLE_RISK_CITATION = erc
            self.ENABLE_INFO_REORDER = eir
            self.INFO_REORDER_RATE = irr
            self.ENABLE_CONCEPTUAL_BRIDGE = ecb
            self.CONCEPTUAL_BRIDGE_RATE = cbr

    return ConfigNamespace(data, topic_citations, aggressiveness, seed, min_cite_len, max_citations,
                           enable_voice, voice_rate, enable_fusion, fusion_rate,
                           enable_transition, transition_rate, enable_reorder, reorder_rate,
                           enable_nominal, nominal_rate, enable_appositive, appositive_rate,
                           enable_discourse, discourse_rate, enable_contraction, contraction_rate,
                           enable_ngram_audit, enable_risk_citation,
                           enable_info_reorder, info_reorder_rate, enable_conceptual_bridge, conceptual_bridge_rate)


def auto_configure_project():
    """
    Scans paper_input/ to find a project folder, auto-detects .tex and .bib files,
    and extracts key topics/keywords from the text to build a dynamic configuration.
    """
    input_root = os.path.join(BASE_DIR, "paper_input")
    if not os.path.exists(input_root):
        return None

    # Find directories inside paper_input/ (ignoring Mathematics-thesis and hidden dirs)
    dirs = [d for d in os.listdir(input_root) 
            if os.path.isdir(os.path.join(input_root, d)) 
            and d != "Mathematics-thesis" and not d.startswith('.')]

    # Fallback to Mathematics-thesis if it is the only folder
    if not dirs:
        if os.path.exists(os.path.join(input_root, "Mathematics-thesis")):
            project_dir_name = "Mathematics-thesis"
        else:
            return None
    else:
        project_dir_name = dirs[0]
        
    input_dir = os.path.join(input_root, project_dir_name)

    # Find the main .tex file
    tex_files = []
    for root_dir, _, files in os.walk(input_dir):
        for f in files:
            if f.endswith('.tex'):
                tex_files.append(os.path.join(root_dir, f))

    if not tex_files:
        return None

    # Identify the main tex file: look for \begin{document} or take the largest one
    main_tex = tex_files[0]
    for tf in tex_files:
        try:
            with open(tf, 'r', encoding='utf-8') as f:
                if '\\begin{document}' in f.read():
                    main_tex = tf
                    break
        except:
            pass

    # Find the .bib file
    bib_files = []
    for root_dir, _, files in os.walk(input_dir):
        for f in files:
            if f.endswith('.bib'):
                bib_files.append(os.path.join(root_dir, f))
    
    main_bib = bib_files[0] if bib_files else os.path.join(input_dir, "references.bib")

    # Read the main tex file to extract keywords/topics automatically
    try:
        with open(main_tex, 'r', encoding='utf-8') as f:
            tex_content = f.read()
    except Exception as e:
        print(f"  ERROR: Could not read LaTeX file {main_tex}: {e}")
        return None

    # Extract scientific/technical words for topic_citations
    # Filter out LaTeX commands, math zones, and common stop words
    clean_text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})*', ' ', tex_content) # remove commands
    clean_text = re.sub(r'\$[^\$]+\$', ' ', clean_text) # remove inline math
    clean_text = re.sub(r'[^a-zA-Z\s]', ' ', clean_text) # remove numbers and punctuation
    
    words = clean_text.lower().split()
    
    # Common academic stop words to filter out
    stop_words = {
        'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'were', 'been',
        'obtained', 'solved', 'using', 'used', 'method', 'methods', 'solution', 'solutions',
        'equation', 'equations', 'results', 'value', 'values', 'boundary', 'initial',
        'condition', 'conditions', 'order', 'second', 'first', 'linear', 'partial',
        'differential', 'approximate', 'approximation', 'numerical', 'scheme', 'schemes',
        'defined', 'where', 'also', 'such', 'then', 'here', 'given', 'there', 'which',
        'these', 'their', 'only', 'both', 'each', 'some', 'more', 'about', 'above',
        'after', 'also', 'than', 'them', 'into', 'well', 'many', 'very', 'could',
        'would', 'should', 'other', 'another', 'chapter', 'section', 'figure', 'table',
        'show', 'shows', 'shown', 'present', 'presents', 'presented', 'case', 'cases'
    }

    # Count frequencies of words with length > 4
    word_counts = defaultdict(int)
    for w in words:
        if len(w) > 4 and w not in stop_words:
            word_counts[w] += 1

    # Take the top 10 most frequent words as key topics
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    # Dynamically build TOPIC_CITATIONS
    topic_citations = OrderedDict()
    for w, count in top_words:
        keywords = (w, f"{w}s" if not w.endswith('s') else w[:-1])
        key = f"ref_topic_{w}"
        topic = f"{w.capitalize()} Analysis and Modeling"
        topic_citations[keywords] = {
            "key": key,
            "topic": topic
        }

    # Environment variables override values if present
    aggressiveness = float(os.getenv("TURNITOUT_AGGRESSIVENESS", 0.75))
    seed = int(os.getenv("TURNITOUT_RANDOM_SEED", 42))
    min_cite_len = int(os.getenv("TURNITOUT_MIN_SENTENCE_LEN", 45))
    max_citations = int(os.getenv("TURNITOUT_MAX_CITATIONS", 30))

    class AutoConfigNamespace:
        def __init__(self):
            self.PROJECT_NAME = project_dir_name
            self.INPUT_DIR = input_dir
            self.TEX_FILE = main_tex
            self.BIB_FILE = main_bib
            self.OUTPUT_DIR = os.path.join(BASE_DIR, "paper_output", f"{project_dir_name}-modified")
            self.SYNONYM_AGGRESSIVENESS = aggressiveness
            self.RANDOM_SEED = seed
            self.MIN_SENTENCE_LENGTH_FOR_CITE = min_cite_len
            self.MAX_CITATIONS_TO_INSERT = max_citations
            self.TOPIC_CITATIONS = topic_citations

            self.ENABLE_VOICE_TRANSFORM = os.getenv("TURNITOUT_VOICE_TRANSFORM", "true").lower() in ("true", "1", "yes")
            self.VOICE_TRANSFORM_RATE = float(os.getenv("TURNITOUT_VOICE_RATE", 0.30))
            self.ENABLE_SENTENCE_FUSION = os.getenv("TURNITOUT_SENTENCE_FUSION", "true").lower() in ("true", "1", "yes")
            self.SENTENCE_FUSION_RATE = float(os.getenv("TURNITOUT_FUSION_RATE", 0.25))
            self.ENABLE_TRANSITION_INJECT = os.getenv("TURNITOUT_TRANSITION_INJECT", "true").lower() in ("true", "1", "yes")
            self.TRANSITION_INJECT_RATE = float(os.getenv("TURNITOUT_TRANSITION_RATE", 0.25))
            self.ENABLE_WORD_REORDER = os.getenv("TURNITOUT_WORD_REORDER", "true").lower() in ("true", "1", "yes")
            self.WORD_REORDER_RATE = float(os.getenv("TURNITOUT_REORDER_RATE", 0.20))
            self.ENABLE_NOMINALIZATION = os.getenv("TURNITOUT_NOMINALIZATION", "true").lower() in ("true", "1", "yes")
            self.NOMINALIZATION_RATE = float(os.getenv("TURNITOUT_NOMINAL_RATE", 0.20))
            self.ENABLE_APPOSITIVE = os.getenv("TURNITOUT_APPOSITIVE", "true").lower() in ("true", "1", "yes")
            self.APPOSITIVE_RATE = float(os.getenv("TURNITOUT_APPOSITIVE_RATE", 0.35))
            self.ENABLE_DISCOURSE_ROTATE = os.getenv("TURNITOUT_DISCOURSE_ROTATE", "true").lower() in ("true", "1", "yes")
            self.DISCOURSE_ROTATE_RATE = float(os.getenv("TURNITOUT_DISCOURSE_RATE", 0.50))
            self.ENABLE_CONTRACTION = os.getenv("TURNITOUT_CONTRACTION", "true").lower() in ("true", "1", "yes")
            self.CONTRACTION_RATE = float(os.getenv("TURNITOUT_CONTRACTION_RATE", 0.20))
            self.ENABLE_NGRAM_AUDIT = os.getenv("TURNITOUT_NGRAM_AUDIT", "true").lower() in ("true", "1", "yes")
            self.ENABLE_RISK_CITATION = os.getenv("TURNITOUT_RISK_CITATION", "true").lower() in ("true", "1", "yes")
            self.ENABLE_INFO_REORDER = os.getenv("TURNITOUT_INFO_REORDER", "true").lower() in ("true", "1", "yes")
            self.INFO_REORDER_RATE = float(os.getenv("TURNITOUT_INFO_REORDER_RATE", 0.20))
            self.ENABLE_CONCEPTUAL_BRIDGE = os.getenv("TURNITOUT_CONCEPTUAL_BRIDGE", "true").lower() in ("true", "1", "yes")
            self.CONCEPTUAL_BRIDGE_RATE = float(os.getenv("TURNITOUT_CONCEPTUAL_BRIDGE_RATE", 0.20))

    return AutoConfigNamespace()
