# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-06-29

### Added
- **7 New Linguistic Transformation Stages**: Voice Transform (active/passive), Sentence Fusion, Transition Phrase Injection, Clause Word Reordering, Nominalization, Appositive Injection, and Discourse Marker Rotation.
- **Morphological Inflection Stemmer**: Automatically stems and conjugates synonym replacements to match plurals (`-s`/`-es`/`-ies`), past tenses (`-ed`/`-ied`), present participles (`-ing`), and adverbs (`-ly`/`-ily`), dramatically increasing natural matches.
- **New CLI Flags**: Added `--dry-run`, `--verbose`, `--disable-stages`, and `--max-aggressiveness` to `cli.py` for control over fire rates and pipeline execution.
- **Prose-Only Context Filtering**: Prevents neighboring LaTeX `MATH` and `SKIP` environments from being incorrectly fused into prose sentences during rhythm enhancement.
- **Placeholder Segment-Splitting Protection**: Isolates LaTeX placeholders (`\x00PH0000\x00`) from string replacements, completely preventing file encoding corruption (eliminating LaTeX binary/NULL byte compile errors).

## [1.0.0-beta] - 2026-06-28

### Added
- Modular, data-driven structure separating rules and configurations into JSON files.
- Dynamic auto-detection of LaTeX papers under `paper_input/` without manual configuration requirements.
- Extracted automated word-frequency analysis to dynamically generate topic citations.
- 5 new regex-based linguistic modification passes: determiner swapping, clause reordering, sentence splitting, hedge word insertion, and final n-gram chain breaking.
- Dynamically generated `ai_prompt.txt` file inside output directories for fast resolving of BibTeX references using external LLMs.
- Strict validation checks on LaTeX output parsing and structure integrity.
