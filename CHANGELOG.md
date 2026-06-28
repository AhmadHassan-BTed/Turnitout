# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-beta] - 2026-06-28

### Added
- Modular, data-driven structure separating rules and configurations into JSON files.
- Dynamic auto-detection of LaTeX papers under `paper_input/` without manual configuration requirements.
- Extracted automated word-frequency analysis to dynamically generate topic citations.
- 5 new regex-based linguistic modification passes: determiner swapping, clause reordering, sentence splitting, hedge word insertion, and final n-gram chain breaking.
- Dynamically generated `ai_prompt.txt` file inside output directories for fast resolving of BibTeX references using external LLMs.
- Strict validation checks on LaTeX output parsing and structure integrity.
