import os
import sys
import shutil
import argparse
from collections import defaultdict

from turnitout.config import load_config_json, auto_configure_project, BASE_DIR
from turnitout.core.parser import LaTeXZoneParser
from turnitout.core.modifier import TextModifier
from turnitout.core.generator import DummyReferenceGenerator, ChangeReportGenerator
from turnitout.core.utils import validate_latex, load_existing_bib_keys

def main():
    parser = argparse.ArgumentParser(description="LaTeX Academic Document Stylistic Enhancer & Citation Helper")
    parser.add_argument(
        "--config",
        type=str,
        default="math_thesis",
        help="Name of the JSON configuration in configs/ (default: math_thesis)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing output files"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed per-line modification logs during processing"
    )
    parser.add_argument(
        "--disable-stages",
        type=str,
        default="",
        help="Comma-separated stages to disable: voice,fusion,transition,reorder,nominal,appositive,discourse"
    )
    parser.add_argument(
        "--max-aggressiveness",
        action="store_true",
        help="Override all fire rates to maximum (0.95) for maximum similarity reduction"
    )
    args = parser.parse_args()

    print("=" * 65)
    print("  LaTeX Academic Document Stylistic Enhancer -- Modular Edition")
    print("=" * 65)
    print()

    # -- Load Selected Configuration File --
    config = None

    # If no configuration is explicitly passed or if we are using the default 'math_thesis',
    # we first check if there is a custom project inside paper_input/ that we can auto-detect
    if args.config == "math_thesis":
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

    # -- Handle CLI Overrides --
    if args.disable_stages:
        stage_map = {
            "voice": "ENABLE_VOICE_TRANSFORM",
            "fusion": "ENABLE_SENTENCE_FUSION",
            "transition": "ENABLE_TRANSITION_INJECT",
            "reorder": "ENABLE_WORD_REORDER",
            "nominal": "ENABLE_NOMINALIZATION",
            "appositive": "ENABLE_APPOSITIVE",
            "discourse": "ENABLE_DISCOURSE_ROTATE",
            "contraction": "ENABLE_CONTRACTION",
        }
        for stage in args.disable_stages.split(","):
            stage = stage.strip().lower()
            if stage in stage_map:
                setattr(config, stage_map[stage], False)
                print(f"  [Disabled] {stage} transformation stage")
 
    if args.max_aggressiveness:
        config.SYNONYM_AGGRESSIVENESS = 0.95
        config.VOICE_TRANSFORM_RATE = 0.90
        config.SENTENCE_FUSION_RATE = 0.80
        config.TRANSITION_INJECT_RATE = 0.80
        config.WORD_REORDER_RATE = 0.75
        config.NOMINALIZATION_RATE = 0.70
        config.APPOSITIVE_RATE = 0.85
        config.DISCOURSE_ROTATE_RATE = 0.95
        config.CONTRACTION_RATE = 0.90
        print("  [MAX AGGRESSIVENESS] All fire rates set to maximum")

    # Establish output file paths
    output_tex = os.path.join(config.OUTPUT_DIR, "main.tex")
    output_bib = os.path.join(config.OUTPUT_DIR, "dummy_references.bib")
    change_report_path = os.path.join(BASE_DIR, "change_report.md")

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

    # Breakdown zones count
    zone_counts = defaultdict(int)
    for z in zones:
        zone_counts[z['type']] += 1
    print(f"  Zone breakdown:")
    for ztype, count in sorted(zone_counts.items()):
        print(f"    {ztype.ljust(10)}: {str(count).rjust(5)} lines")

    # -- Apply modifications --
    print(f"\n[4/7] Applying intelligent modifications...")
    
    # Instantiate Modifier with config settings
    aggressiveness = getattr(config, "SYNONYM_AGGRESSIVENESS", 0.75)
    seed = getattr(config, "RANDOM_SEED", 42)
    min_cite_len = getattr(config, "MIN_SENTENCE_LENGTH_FOR_CITE", 45)
    
    modifier = TextModifier(
        seed=seed,
        aggressiveness=aggressiveness,
        topic_citations=config.TOPIC_CITATIONS,
        existing_cite_keys=existing_cite_keys,
        min_sentence_length_for_cite=min_cite_len,
        enable_voice_transform=config.ENABLE_VOICE_TRANSFORM,
        voice_transform_rate=config.VOICE_TRANSFORM_RATE,
        enable_sentence_fusion=config.ENABLE_SENTENCE_FUSION,
        sentence_fusion_rate=config.SENTENCE_FUSION_RATE,
        enable_transition_inject=config.ENABLE_TRANSITION_INJECT,
        transition_inject_rate=config.TRANSITION_INJECT_RATE,
        enable_word_reorder=config.ENABLE_WORD_REORDER,
        word_reorder_rate=config.WORD_REORDER_RATE,
        enable_nominalization=config.ENABLE_NOMINALIZATION,
        nominalization_rate=config.NOMINALIZATION_RATE,
        enable_appositive=config.ENABLE_APPOSITIVE,
        appositive_rate=config.APPOSITIVE_RATE,
        enable_discourse_rotate=config.ENABLE_DISCOURSE_ROTATE,
        discourse_rotate_rate=config.DISCOURSE_ROTATE_RATE,
        enable_contraction=config.ENABLE_CONTRACTION,
        contraction_rate=config.CONTRACTION_RATE
    )

    modified_lines = []

    for i, zone in enumerate(zones):
        line = zone['text']

        if zone['type'] == 'PROSE':
            context = []
            for offset in [-2, -1, 1, 2]:
                ci = i + offset
                if 0 <= ci < len(zones) and zones[ci]['type'] == 'PROSE':
                    context.append(zones[ci]['text'])

            modified = modifier.modify_line(line, zone['idx'], context)
            if args.verbose and modified != line:
                print(f"    L{zone['idx']+1}: {line.strip()[:70]}...")
                print(f"       -> {modified.strip()[:70]}...")
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
            if args.verbose and modified != line:
                print(f"    L{zone['idx']+1} (Heading): {line.strip()[:70]}...")
                print(f"       -> {modified.strip()[:70]}...")
            modifier.phrase_rewrite_count += light_modifier.phrase_rewrite_count
            modifier.changes_log.extend(light_modifier.changes_log)
            modified_lines.append(modified)

        else:
            # Skip and math environments are untouched
            modified_lines.append(line)

    modified_content = '\n'.join(modified_lines)

    print(f"  Synonym replacements:  {modifier.replacement_count}")
    print(f"  Phrase rewrites:       {modifier.phrase_rewrite_count}")
    print(f"  Clause reorders:       {modifier.clause_reorder_count}")
    print(f"  Determiner swaps:      {modifier.determiner_swap_count}")
    print(f"  Hedge insertions:      {modifier.hedge_insertion_count}")
    print(f"  N-gram chain breaks:   {modifier.ngram_break_count}")
    print(f"  Sentence splits:       {modifier.sentence_split_count}")
    print(f"  Voice transforms:      {modifier.voice_transform_count}")
    print(f"  Sentence fusions:      {modifier.sentence_fusion_count}")
    print(f"  Transition injections: {modifier.transition_inject_count}")
    print(f"  Clause word reorders:  {modifier.clause_word_reorder_count}")
    print(f"  Nominalizations:       {modifier.nominalization_count}")
    print(f"  Appositive injections: {modifier.appositive_count}")
    print(f"  Discourse rotations:   {modifier.discourse_rotate_count}")
    print(f"  Contraction swaps:     {modifier.contraction_count}")
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
    if args.dry_run:
        print(f"\n[6/7] DRY RUN — no files written")
    else:
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
            prompt_lines.append("I am using a LaTeX document stylistic enhancer and pre-submission validation helper. It has inserted recommended bibliographic citation keys as placeholders in my document. I need you to find real, highly-cited, relevant academic papers (journal articles, books, or conference papers) that match these topics, and format them as valid BibTeX entries.\n")
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
    total_transforms = (modifier.replacement_count + modifier.phrase_rewrite_count +
                         modifier.clause_reorder_count + modifier.determiner_swap_count +
                         modifier.hedge_insertion_count + modifier.ngram_break_count +
                         modifier.sentence_split_count + modifier.citation_count +
                         modifier.voice_transform_count + modifier.sentence_fusion_count +
                         modifier.transition_inject_count + modifier.clause_word_reorder_count +
                         modifier.nominalization_count + modifier.appositive_count +
                         modifier.discourse_rotate_count + modifier.contraction_count)
    print(f"  Total lines processed:    {total_lines}")
    print(f"  Prose lines modified:     {len(modifier.changes_log)}")
    print(f"  Total transformations:    {total_transforms}")
    print(f"    Synonym replacements:   {modifier.replacement_count}")
    print(f"    Phrase rewrites:        {modifier.phrase_rewrite_count}")
    print(f"    Clause reorders:        {modifier.clause_reorder_count}")
    print(f"    Determiner swaps:       {modifier.determiner_swap_count}")
    print(f"    Hedge insertions:       {modifier.hedge_insertion_count}")
    print(f"    N-gram breaks:          {modifier.ngram_break_count}")
    print(f"    Sentence splits:        {modifier.sentence_split_count}")
    print(f"    Voice transforms:      {modifier.voice_transform_count}")
    print(f"    Sentence fusions:      {modifier.sentence_fusion_count}")
    print(f"    Transition injections: {modifier.transition_inject_count}")
    print(f"    Clause word reorders:  {modifier.clause_word_reorder_count}")
    print(f"    Nominalizations:       {modifier.nominalization_count}")
    print(f"    Appositive injections: {modifier.appositive_count}")
    print(f"    Discourse rotations:   {modifier.discourse_rotate_count}")
    print(f"    Contraction swaps:     {modifier.contraction_count}")
    print(f"    Citations added:        {modifier.citation_count}")
    
    new_dummies = sum(1 for kw_tuple, info in config.TOPIC_CITATIONS.items() 
                      if info["key"] in modifier.used_cite_keys and info["key"] not in existing_cite_keys)
    print(f"  New dummy references:     {new_dummies}")
    print(f"  Validation issues:        {len(issues)}")
    print(f"\n  NEXT STEPS:")
    if args.dry_run:
        print("  1. Preview complete. This was a dry run -- no files were generated.")
    else:
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
        print(f"  6. Submit document for peer review.")
    print("=" * 65)

if __name__ == '__main__':
    main()
