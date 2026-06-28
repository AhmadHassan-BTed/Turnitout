import os
import re
import sys
import json
from collections import OrderedDict, defaultdict
from dotenv import load_dotenv

# Resolve root directory relative to this file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

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

    class ConfigNamespace:
        def __init__(self, d, tc, agg, sd, mcl):
            self.PROJECT_NAME = d["project_name"]
            
            # Resolve relative paths relative to BASE_DIR
            self.INPUT_DIR = os.path.normpath(os.path.join(BASE_DIR, d["input_dir"]))
            self.TEX_FILE = os.path.normpath(os.path.join(BASE_DIR, d["tex_file"]))
            self.BIB_FILE = os.path.normpath(os.path.join(BASE_DIR, d["bib_file"]))
            self.OUTPUT_DIR = os.path.normpath(os.path.join(BASE_DIR, d["output_dir"]))
            
            self.SYNONYM_AGGRESSIVENESS = agg
            self.RANDOM_SEED = sd
            self.MIN_SENTENCE_LENGTH_FOR_CITE = mcl
            self.TOPIC_CITATIONS = tc

    return ConfigNamespace(data, topic_citations, aggressiveness, seed, min_cite_len)


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
            self.TOPIC_CITATIONS = topic_citations

    return AutoConfigNamespace()
