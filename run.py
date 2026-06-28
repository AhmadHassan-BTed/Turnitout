#!/usr/bin/env python3
"""
run.py — CLI Runner for the Turnitin Similarity Reduction Tool
==============================================================
Orchestrates the modular architecture by:
  1. Loading selected paper configurations dynamically
  2. Parsing structural zones using LaTeXZoneParser
  3. Modifying prose and section headings using TextModifier
  4. Generating outputs (main.tex, references.bib, change_report.md)
  5. Copying image assets/media directories

Usage:
    python run.py --config math_thesis
"""

import os
import re
import sys
import json
import shutil
import argparse
import importlib
from collections import defaultdict, OrderedDict

# Add current directory to path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.parser import LaTeXZoneParser
from core.modifier import TextModifier
from core.generator import DummyReferenceGenerator, ChangeReportGenerator

# ================================================================
# UTILITIES
# ================================================================

def load_existing_bib_keys(bib_path):
    """Load existing citation keys from a .bib file."""
    keys = set()
    if os.path.exists(bib_path):
        with open(bib_path, 'r', encoding='utf-8') as f:
            content = f.read()
        for match in re.finditer(r'@\w+\{(\w+),', content):
            keys.add(match.group(1))
    return keys


def validate_latex(content):
    """Basic LaTeX validation checks."""
    issues = []

    # Check balanced braces
    depth = 0
    for i, ch in enumerate(content):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        if depth < 0:
            line_num = content[:i].count('\n') + 1
            issues.append("Unmatched closing brace at line " + str(line_num))
            depth = 0
    if depth != 0:
        issues.append("Unbalanced braces: " + str(depth) + " unclosed '{' remaining")

    # Check balanced dollar signs
    dollar_count = 0
    in_escape = False
    for ch in content:
        if ch == '\\':
            in_escape = True
            continue
        if ch == '$' and not in_escape:
            dollar_count += 1
        in_escape = False
    if dollar_count % 2 != 0:
        issues.append("Odd number of '$' signs (" + str(dollar_count) + ") -- possible broken inline math")

    # Check begin/end environment pairing
    begins = re.findall(r'\\begin\{(\w+\*?)\}', content)
    ends = re.findall(r'\\end\{(\w+\*?)\}', content)
    begin_counts = defaultdict(int)
    end_counts = defaultdict(int)
    for b in begins:
        begin_counts[b] += 1
    for e in ends:
        end_counts[e] += 1
    for env in set(list(begin_counts.keys()) + list(end_counts.keys())):
        if begin_counts[env] != end_counts[env]:
            issues.append("Mismatched \\begin{" + env + "} (" + str(begin_counts[env]) +
                         ") vs \\end{" + env + "} (" + str(end_counts[env]) + ")")

    return issues


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config_json(config_name):
    """
    Loads config details from configs/{config_name}.json.
    Supports either a config name (e.g. 'math_thesis') or a direct path to a JSON file.
    """
    if config_name.endswith('.json'):
        config_path = config_name
    else:
        config_path = os.path.join(BASE_DIR, "configs", f"{config_name}.json")

    if not os.path.exists(config_path):
        print(f"  ERROR: Configuration file not found at: {config_path}")
        print("  Please make sure you have placed the JSON file in 'configs/' directory.")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  ERROR: Configuration file '{config_path}' is not a valid JSON file.")
            print(f"  Details: {e}")
            sys.exit(1)

    # Convert topic_citations list to OrderedDict with tuples of keywords
    topic_citations = OrderedDict()
    for item in data.get("topic_citations", []):
        if "keywords" not in item or "key" not in item or "topic" not in item:
            print(f"  ERROR: Invalid topic_citations entry in config: {item}")
            sys.exit(1)
        keywords = tuple(item["keywords"])
        topic_citations[keywords] = {
            "key": item["key"],
            "topic": item["topic"]
        }

    # Verify required keys in JSON
    required_keys = ["project_name", "input_dir", "tex_file", "bib_file", "output_dir"]
    for key in required_keys:
        if key not in data:
            print(f"  ERROR: Configuration is missing required property: '{key}'")
            sys.exit(1)

    class ConfigNamespace:
        def __init__(self, d, tc):
            self.PROJECT_NAME = d["project_name"]
            
            # Resolve relative paths relative to BASE_DIR
            self.INPUT_DIR = os.path.normpath(os.path.join(BASE_DIR, d["input_dir"]))
            self.TEX_FILE = os.path.normpath(os.path.join(BASE_DIR, d["tex_file"]))
            self.BIB_FILE = os.path.normpath(os.path.join(BASE_DIR, d["bib_file"]))
            self.OUTPUT_DIR = os.path.normpath(os.path.join(BASE_DIR, d["output_dir"]))
            
            self.SYNONYM_AGGRESSIVENESS = d.get("synonym_aggressiveness", 0.55)
            self.RANDOM_SEED = d.get("random_seed", 42)
            self.MIN_SENTENCE_LENGTH_FOR_CITE = d.get("min_sentence_length_for_cite", 60)
            self.TOPIC_CITATIONS = tc

    return ConfigNamespace(data, topic_citations)


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

    class AutoConfigNamespace:
        def __init__(self):
            self.PROJECT_NAME = project_dir_name
            self.INPUT_DIR = input_dir
            self.TEX_FILE = main_tex
            self.BIB_FILE = main_bib
            self.OUTPUT_DIR = os.path.join(BASE_DIR, "paper_output", f"{project_dir_name}-modified")
            self.SYNONYM_AGGRESSIVENESS = 0.55
            self.RANDOM_SEED = 42
            self.MIN_SENTENCE_LENGTH_FOR_CITE = 60
            self.TOPIC_CITATIONS = topic_citations

    return AutoConfigNamespace()


# ================================================================
# MAIN PROCESS
# ================================================================

def main():
    parser = argparse.ArgumentParser(description="Turnitin Similarity Reduction Tool")
    parser.add_argument(
        "--config",
        type=str,
        default="math_thesis",
        help="Name of the JSON configuration in configs/ (default: math_thesis)"
    )
    args = parser.parse_args()

    print("=" * 65)
    print("  Turnitin Similarity Reduction Tool -- Modular Edition")
    print("=" * 65)
    print()

    # -- Load Selected Configuration File --
    config = None

    # If no configuration is explicitly passed or if we are using the default 'math_thesis',
    # we first check if there is a custom project inside paper_input/ that we can auto-detect
    if args.config == "math_thesis":
        # Check if there's any directory in paper_input/ besides Mathematics-thesis
        input_root = os.path.join(BASE_DIR, "paper_input")
        other_projects = []
        if os.path.exists(input_root):
            other_projects = [d for d in os.listdir(input_root) 
                              if os.path.isdir(os.path.join(input_root, d)) 
                              and d != "Mathematics-thesis" and not d.startswith('.')]
        
        if other_projects:
            print("[1/7] Auto-detecting project in paper_input/...")
            config = auto_configure_project()
            if config:
                print(f"  [Auto-Detected] Found project folder: {config.PROJECT_NAME}")
                print(f"  Main LaTeX file:  {config.TEX_FILE}")
                print(f"  Bibliography file: {config.BIB_FILE}")
            else:
                print("  Failed to auto-configure project. Falling back to math_thesis...")

    if config is None:
        print(f"[1/7] Loading paper configuration: {args.config}...")
        config = load_config_json(args.config)



    # Establish output file paths
    output_tex = os.path.join(config.OUTPUT_DIR, "main.tex")
    output_bib = os.path.join(config.OUTPUT_DIR, "dummy_references.bib")
    change_report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "change_report.md")

    # -- Load Input Files --
    print(f"\n[2/7] Loading LaTeX source: {config.TEX_FILE}...")
    if not os.path.exists(config.TEX_FILE):
        print(f"  ERROR: LaTeX file not found at: {config.TEX_FILE}")
        print("  Please place your files in the 'paper_input/' directory.")
        sys.exit(1)
        
    with open(config.TEX_FILE, 'r', encoding='utf-8') as f:
        tex_content = f.read()
    total_lines = tex_content.count('\n') + 1
    print(f"  Loaded {total_lines} lines ({len(tex_content)} characters)")

    # Load Bibliography keys
    print(f"  Loading existing bibliography: {config.BIB_FILE}...")
    existing_cite_keys = load_existing_bib_keys(config.BIB_FILE)
    print(f"  Found {len(existing_cite_keys)} existing citation keys in database")

    # -- Parse LaTeX structure --
    print(f"\n[3/7] Parsing LaTeX structure into zones...")
    parser_obj = LaTeXZoneParser()
    zones = parser_obj.parse(tex_content)

    zone_counts = defaultdict(int)
    for z in zones:
        zone_counts[z['type']] += 1
    print(f"  Zone breakdown:")
    for ztype, count in sorted(zone_counts.items()):
        print(f"    {ztype.ljust(10)}: {str(count).rjust(5)} lines")

    # -- Apply modifications --
    print(f"\n[4/7] Applying intelligent modifications...")
    
    # Instantiate Modifier with config settings
    aggressiveness = getattr(config, "SYNONYM_AGGRESSIVENESS", 0.55)
    seed = getattr(config, "RANDOM_SEED", 42)
    min_cite_len = getattr(config, "MIN_SENTENCE_LENGTH_FOR_CITE", 60)
    
    modifier = TextModifier(
        seed=seed,
        aggressiveness=aggressiveness,
        topic_citations=config.TOPIC_CITATIONS,
        existing_cite_keys=existing_cite_keys,
        min_sentence_length_for_cite=min_cite_len
    )

    modified_lines = []

    for i, zone in enumerate(zones):
        line = zone['text']

        if zone['type'] == 'PROSE':
            context = []
            for offset in [-2, -1, 1, 2]:
                ci = i + offset
                if 0 <= ci < len(zones):
                    context.append(zones[ci]['text'])

            modified = modifier.modify_line(line, zone['idx'], context)
            modified_lines.append(modified)

        elif zone['type'] == 'HEADING':
            # Light modifications for headings (phrase rewrites only, no synonyms)
            light_modifier = TextModifier(
                seed=seed + i,
                aggressiveness=0.0,
                topic_citations=config.TOPIC_CITATIONS,
                existing_cite_keys=existing_cite_keys,
                min_sentence_length_for_cite=min_cite_len
            )
            modified = light_modifier.modify_line(line, zone['idx'])
            modifier.phrase_rewrite_count += light_modifier.phrase_rewrite_count
            modifier.changes_log.extend(light_modifier.changes_log)
            modified_lines.append(modified)

        else:
            # Skip and math environments are untouched
            modified_lines.append(line)

    modified_content = '\n'.join(modified_lines)

    print(f"  Synonym replacements:  {modifier.replacement_count}")
    print(f"  Phrase rewrites:       {modifier.phrase_rewrite_count}")
    print(f"  Citations added:       {modifier.citation_count}")
    print(f"  Lines modified:        {len(modifier.changes_log)}")

    # -- Validate output --
    print(f"\n[5/7] Validating modified LaTeX output...")
    issues = validate_latex(modified_content)
    if issues:
        print(f"  WARNING: {len(issues)} potential issues found:")
        for issue in issues[:10]:
            print(f"    - {issue}")
    else:
        print(f"  All validation checks passed")

    # -- Write output files --
    print(f"\n[6/7] Writing output files to separate folder...")
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # 1. Write modified main.tex
    with open(output_tex, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    print(f"  Modified LaTeX (main.tex):  {output_tex}")

    # 2. Generate dummy references if any new ones are used
    ref_gen = DummyReferenceGenerator()
    bib_content = ref_gen.generate(modifier.used_cite_keys, existing_cite_keys, config.TOPIC_CITATIONS)
    with open(output_bib, 'w', encoding='utf-8') as f:
        f.write(bib_content)
    print(f"  Dummy references: {output_bib}")

    # 3. Copy/merge references.bib to output directory
    dest_bib = os.path.join(config.OUTPUT_DIR, "references.bib")
    if os.path.exists(config.BIB_FILE):
        shutil.copy(config.BIB_FILE, dest_bib)
        if "@article" in bib_content:
            with open(dest_bib, 'a', encoding='utf-8') as f:
                f.write("\n\n" + bib_content)
            print(f"  Merged new dummy references into: {dest_bib}")
    print(f"  Bibliography file: {dest_bib}")

    # 4. Copy media assets directories
    copied_media = []
    # Find any folders inside input directory besides references.bib and main.tex
    for item in os.listdir(config.INPUT_DIR):
        src_path = os.path.join(config.INPUT_DIR, item)
        dest_path = os.path.join(config.OUTPUT_DIR, item)
        if os.path.isdir(src_path) and not item.startswith('.'):
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            copied_media.append(item)
    if copied_media:
        print("  Copied media/assets directories: " + ", ".join(copied_media))

    # 5. Write Change Report
    report_gen = ChangeReportGenerator()
    report_content = report_gen.generate(modifier, change_report_path, config.TOPIC_CITATIONS)
    with open(change_report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"  Change report:   {change_report_path}")

    # 6. Generate pre-filled AI Prompt for added citation keys
    prompt_path = os.path.join(config.OUTPUT_DIR, "ai_prompt.txt")
    if modifier.used_cite_keys:
        prompt_lines = []
        prompt_lines.append("I am using a LaTeX similarity reduction tool. It has generated several dummy placeholder BibTeX citations in my document. I need you to find real, highly-cited, relevant academic papers (journal articles, books, or conference papers) that match these topics, and format them as valid BibTeX entries.\n")
        prompt_lines.append("For each topic, provide a real academic source. You MUST keep the exact BibTeX key I provide so that it matches my LaTeX file.\n")
        prompt_lines.append("Here is the list of citation keys and the academic topics they should cover:\n")
        
        for idx, key in enumerate(sorted(modifier.used_cite_keys), 1):
            topic = "Unknown"
            for kw_tuple, info in config.TOPIC_CITATIONS.items():
                if info["key"] == key:
                    topic = info["topic"]
                    break
            prompt_lines.append(f"{idx}. Key: {key}")
            prompt_lines.append(f"   Topic: {topic}\n")
            
        prompt_lines.append("Please ensure:")
        prompt_lines.append("- The BibTeX citation key matches my key EXACTLY (e.g., ref_thermal_modeling).")
        prompt_lines.append("- The papers are real, published, and highly cited (articles or textbooks).")
        prompt_lines.append("- The output is strictly formatted as valid BibTeX.")
        
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(prompt_lines))
        print(f"  Generated pre-filled AI Prompt: {prompt_path}")

    # -- Summary --
    print(f"\n[7/7] Done!")
    print("\n" + "=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    print(f"  Total lines processed:    {total_lines}")
    print(f"  Prose lines modified:     {len(modifier.changes_log)}")
    print(f"  Synonym replacements:     {modifier.replacement_count}")
    print(f"  Phrase rewrites:          {modifier.phrase_rewrite_count}")
    print(f"  Citations added:          {modifier.citation_count}")
    
    new_dummies = sum(1 for kw_tuple, info in config.TOPIC_CITATIONS.items() 
                      if info["key"] in modifier.used_cite_keys and info["key"] not in existing_cite_keys)
    print(f"  New dummy references:     {new_dummies}")
    print(f"  Validation issues:        {len(issues)}")
    print(f"\n  NEXT STEPS:")
    print(f"  1. The complete, compile-ready project has been written to:")
    print(f"     {config.OUTPUT_DIR}")
    print(f"  2. Review the change report: {change_report_path}")
    if new_dummies > 0:
        print(f"  3. Open and copy the pre-filled AI prompt from:")
        print(f"     {prompt_path}")
        print("     Paste it into ChatGPT/Claude to generate real BibTeX entries,")
        print("     and replace the dummy placeholders at the bottom of references.bib.")
    else:
        print("  3. (All citations were successfully matched with existing bibliography entries!)")
    print(f"  4. Open the output directory and build main.tex using your LaTeX editor.")
    print(f"  5. Compile with pdflatex and verify.")
    print(f"  6. Re-submit to Turnitin.")
    print("=" * 65)


if __name__ == '__main__':
    main()
