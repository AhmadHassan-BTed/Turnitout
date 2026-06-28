# Turnitout — Intelligent LaTeX Plagiarism & Similarity Reduction Tool

[![CI Build Status](https://github.com/AhmadHassan-BTed/Turnitout/workflows/CI/badge.svg)](https://github.com/AhmadHassan-BTed/Turnitout/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)

Turnitout is a production-grade, highly-cohesive, configuration-driven command-line tool designed to systematically lower Turnitin similarity and plagiarism scores in LaTeX documents. It utilizes deterministic parsing, contextual word and phrase mutations, and automated keyword-driven citation injections to break up Turnitin's sequential n-gram detection windows while fully preserving mathematical equations, formatting macros, and compilation validity.

---

## 🚀 Key Features

* **Strict LaTeX Structural Zone Parsing**: Isolates prose from preamble, formatting commands, comments, listings, tables, figures, and inline/display math blocks (`$ ... $`, `\[ ... \]`, `\begin{equation}`).
* **Linguistic Mutation Engine**:
  * **Academic Synonym Substitution**: Dynamically swaps verbs, nouns, and adjectives with academically sound synonyms.
  * **Turnitin N-Gram Idiom Rewriter**: Rewrites common academic word sequences to break Turnitin's sequential scanner.
  * **Contextual Determiner Swapping**: Swaps determiners to disrupt structural matches.
  * **Voice & Clause Reordering**: Automatically transforms clauses (e.g. passive/active structures) to restructure lines.
  * **Sentence Splitting & Hedge Word Injection**: Splits complex sentences at conjunctions and injects qualifiers.
* **Automated Keyword Citation Injections**: Dynamically matches prose blocks against configurable target subjects, inserting citations (`\cite{...}`) for assertions to bypass Turnitin's "Not Cited or Quoted" matches.
* **Zero-Configuration Run Mode**: Automatically detects LaTeX directories inside `paper_input/`, identifies `.tex` and `.bib` files, extracts core keywords using local term-frequency analysis, and processes the paper on-the-fly.
* **Separation of Concerns**: Statically separates execution logic from word/phrase dictionaries (`rules/*.json`) and project paths (`configs/*.json`).

---

## 📐 Project Architecture

Turnitout is structured as a clean, installable Python package matching professional repository standards:

```text
Turnitout/
├── .github/                  # GitHub Community Configs & CI/CD Pipelines
│   ├── ISSUE_TEMPLATE/       # Bug and Feature templates
│   └── workflows/ci.yml      # CI/CD test automation runs
├── configs/                  # Paper-specific configuration JSONs
├── docs/                     # Documentation and release history
│   ├── architecture.md       # Pipeline architecture diagrams
│   ├── changelog.md          # Release change history
│   ├── getting-started.md    # Detailed onboarding usage guide
│   ├── roadmap.md            # Upcoming features and planning
│   └── technical-decisions.md# Decision records (Offline-only logic, data separation)
├── paper_input/              # Directory to copy raw LaTeX files
├── paper_output/             # Folder containing clean, processed outputs
├── rules/                    # Dictionaries of synonyms, phrases, and technical rules
├── src/                      # Source package directory
│   └── turnitout/
│       ├── __init__.py
│       ├── cli.py            # Command Line Interface runner
│       ├── config.py         # Config parser & environment loader
│       └── core/
│           ├── parser.py     # Structural LaTeX tokenizer
│           ├── modifier.py   # Mutation pipeline engine
│           ├── generator.py  # References & report compiler
│           ├── rules.py      # Rule file JSON database parser
│           └── utils.py      # LaTeX syntax checkers
├── tests/                    # Automated testing suite
│   ├── test_parser.py        # Parser zone validation tests
│   ├── test_modifier.py      # Modifier syntax-safety test runs
│   └── test_rules.py         # JSON files contract checkers
├── pyproject.toml            # Package build configuration & PEP 517 metadata
├── run.py                    # Root entrypoint launcher wrapper
└── .env.example              # Template environment configuration variables
```

---

## 📦 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/AhmadHassan-BTed/Turnitout.git
   cd Turnitout
   ```

2. **Configure Virtual Environment**:
   ```bash
   python -m venv env
   # On Windows:
   env\Scripts\activate
   # On macOS/Linux:
   source env/bin/activate
   ```

3. **Install Dependencies & Package**:
   Install the package locally in editable development mode:
   ```bash
   pip install -e .[dev]
   ```

---

## ⚙️ Configuration & Environment Settings

Turnitout supports environment variables to override default pipeline behaviors. Copy the `.env.example` file to `.env` to configure your overrides:

```bash
cp .env.example .env
```

Available variables inside `.env`:
* `TURNITOUT_AGGRESSIVENESS`: Mutation probability threshold (float, default: `0.75`).
* `TURNITOUT_MIN_SENTENCE_LEN`: Minimum line character length to append citations (int, default: `45`).
* `TURNITOUT_RANDOM_SEED`: Random generator seed to guarantee reproducible outputs (int, default: `42`).

---

## 📖 Basic Usage

### Option 1: Zero-Configuration Auto-Detection (Default)
Place your raw LaTeX project folder inside `paper_input/` (e.g. `paper_input/MyBiologyPaper/` containing `main.tex`, `references.bib`, and asset images). 

Then, run:
```bash
python run.py
```
*The tool automatically scans `paper_input/`, configures files on-the-fly, extracts the top 10 scientific keywords from your paper, paraphrases prose, and outputs the result in `paper_output/MyBiologyPaper-modified/`.*

### Option 2: Configured Run with Overrides
If you want to explicitly define citation keywords or adjust paths, configure a JSON file in `configs/my_paper.json` and execute with the `--config` flag:
```bash
python run.py --config my_paper
```

---

## 🧪 Testing & Quality Control

Verify code and formatting syntax rules pass before committing:

```bash
# Run unit tests
python -m pytest

# Check code formatting rules
black --check src/ tests/

# Perform lint analysis
flake8 src/ tests/
```

---

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
