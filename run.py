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
import shutil
import argparse
import importlib
from collections import defaultdict

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


# ================================================================
# MAIN PROCESS
# ================================================================

def main():
    parser = argparse.ArgumentParser(description="Turnitin Similarity Reduction Tool")
    parser.add_argument(
        "--config",
        type=str,
        default="math_thesis",
        help="Name of the paper configuration module in paper_config/ (default: math_thesis)"
    )
    args = parser.parse_args()

    print("=" * 65)
    print("  Turnitin Similarity Reduction Tool -- Modular Edition")
    print("=" * 65)
    print()

    # -- Load Selected Configuration Module --
    config_module_name = f"paper_config.{args.config}"
    print(f"[1/7] Loading paper configuration: {config_module_name}...")
    try:
        config = importlib.import_module(config_module_name)
    except ImportError as e:
        print(f"  ERROR: Could not load configuration '{config_module_name}'.")
        print(f"  Details: {e}")
        print("  Please make sure the file exists in paper_config/ folder.")
        sys.exit(1)

    # Validate configuration contents
    required_attrs = ["TEX_FILE", "BIB_FILE", "OUTPUT_DIR", "TOPIC_CITATIONS"]
    for attr in required_attrs:
        if not hasattr(config, attr):
            print(f"  ERROR: Configuration is missing required attribute: '{attr}'")
            sys.exit(1)

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
    print(f"  3. Open the output directory and build main.tex using your LaTeX editor.")
    print(f"  4. Compile with pdflatex and verify.")
    print(f"  5. Re-submit to Turnitin.")
    print("=" * 65)


if __name__ == '__main__':
    main()
