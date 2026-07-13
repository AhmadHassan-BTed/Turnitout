# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-07-08

### Added
- **Detailed GitHub Verification Failure Messages**: Replaced generic verification failure errors on the checklist screen with detailed, user-friendly markdown logs highlighting precisely which follow or star actions are outstanding.
- **Clickable Missing Repository Links**: Unstarred repositories are now shown as direct, clickable links inside the verification failure error box, making it simple for the user to open and star them.

### Changed
- **Conversational Style Preset Default**: Made "Conversational / Daily English" the default Style Preset instead of the academic one.
- **Advanced UI Checkbox Alignment**: Dynamically synced checkbox values in the Advanced Options expander to match the preset defaults (automatically hiding/disabling technical options when in conversational mode).

### Fixed
- **DOCX Formatting & Spacing Preservation**: Rewrote the paragraph-processing engine in `doc_processor.py` to use character-level sequence alignment (`difflib.SequenceMatcher`) across all descendant XML runs (including nested hyperlink and citation field runs). This fully preserves Table of Contents hyperlinks, colors, font styling, and dynamic cross-references while preventing adjacent words from merging.
- **Streamlit State Syncing on Failure**: Added `st.rerun()` upon verification failure to ensure the checklist UI and error messages update immediately.
- **GitHub API Rate Limit Graceful Fallback**: Modified follow status check to treat HTTP 403 (Rate Limit) errors as successful follow status so users are not blocked.
- **Flaky Unit Test Assertion**: Fixed a flaky assertion in `test_modifier.py` to accept all valid sentence fusion connectors from the externalized JSON.

## [1.3.0] - 2026-07-07

### Added
- **Logarithmic Intensity Slider**: Replaced the linear slider mapping with a base-10 exponential volume-curve, offering fine-grained control at the lower range (75% default maps to 20% internal aggressiveness) and rapid scaling at the high end.
- **Decoupled Architecture (Linguistic Data Separation)**: Extracted all remaining hardcoded helper verb sets, adjective suffixes, adverbs, qualifiers, conjunctions, and sentence split patterns into structured JSON rules with AI metadata prompts, documented in `ARCHITECTURE_RULES.md`.
- **Contextual Synonym Repetition Blocker**: Synonym selection now actively filters out candidates that are already present in the active sentence, eliminating duplicate word collisions.
- **Determiner Swap Repetition Memory**: Implemented recently-used memory buffers for determiners to prevent repetitive insertion of formal words like *"aforementioned"* or *"given"*.
- **Grammar-Preserving Clause Splitting & Reordering**:
  - Voice transformations now ignore sentences with coordinating conjunctions (`and`/`but`/`or`) to prevent clause mangling.
  - Compound sentence splitting only triggers if the split segment starts with a valid subject pronoun/determiner, avoiding splitting Oxford commas and lists.
  - Sentence fusion uses only clause-friendly connectors like `"and as a result"`, `"which means"`, `"and therefore"`, and `"and thus"`.

### Fixed
- **Streamlit Cookie Controller Crash**: Wrapped cookie retrievals in `safe_get_cookie` handler to gracefully capture exceptions (`TypeError`) when `self.__cookies` is `None` during early async mounts on Streamlit Cloud.
- **Excluded Fractal-PrivacyPolicy**: Modified developer repos logic to ignore repositories with `"fractal-privacypolicy"` in the name, preventing users from needing to star this repo.
- **Removed /stargazers from URLs**: Stripped `/stargazers` from URLs to direct users directly to the main repository page rather than the stargazers page (which returns 404 when the star count is zero).
- **Simplified Setting Toggle Labels**: Simplified technical settings (e.g. "Nominalization", "N-gram Audit", "Appositive Explanations") to simpler terms (e.g. "Switch Verb & Noun Forms", "Smart Similarity Shield", "Add Explanatory Details") to hide pipeline implementation details.

## [1.2.0] - 2026-07-05

### Added
- **Streamlit Web Application**: An aesthetic web interface containing format selectors, Proportional Intensity sliders, advanced options toggles, and document processors.
- **Tkinter Desktop GUI**: A native desktop application with split side-by-side text inputs/outputs, real-time counters, citation limiters, and custom BibTeX references viewers.
- **Word Document (.docx) Parser**: Added fully decoupled processing of body paragraphs, tables, table cells, headers, and footers while preserving styles (bold, italics, etc.) run-by-run.
- **Strict Star & Follow Gating**: Gated access on the Streamlit app to require following your personal account (`AhmadHassan-BTed`) and organization account (`Fractal-Compute-Orchestrations`) plus starring ALL public repositories.
- **Active Anti-Bypass checks**: Verifies stargazer and follow status in the background every single time they try to humanize text/documents to prevent sly unfollows.
- **Persistent Help & Feedback**: Integrated a feedback form inside the sidebar that dynamically generates pre-filled links to submit private emails or file GitHub issues.
- **Linguistic Upgrades**: Strips LLM indicators (em-dashes `—` and en-dashes `–`) and implemented a rolling synonym FIFO buffer (size 15) to prevent repetition.

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
