# Turnitin Similarity Reduction Tool (Modular Edition)

An extensible, open-source framework to systematically reduce Turnitin plagiarism and similarity indices in LaTeX research papers, theses, and documents.

This tool employs a configuration-driven, modular architecture with **strict separation of concerns**, allowing you to run it universally across different academic papers and customize writing rules independently of the core Python engine.

---

## Folder Architecture

```
Plagerism Similarity Remove/
│
├── core/                        # Reusable core framework
│   ├── __init__.py
│   ├── rules.py                 # Rules loader (reads from JSON, handles fallbacks)
│   ├── parser.py                # LaTeX structural zone parser
│   ├── modifier.py              # Text paraphraser & citation matcher
│   └── generator.py             # Change report & dummy reference generator
│
├── rules/                       # Universal language rules (Editable JSON files)
│   ├── synonyms.json            # Word-level swap mappings
│   ├── phrases.json             # Phrase-level N-gram rewrite patterns
│   └── protected_terms.json     # Technical terms protected from modifications
│
├── paper_config/                # Project-specific configurations
│   ├── __init__.py
│   └── math_thesis.py           # Configuration and keyword citation mapping for math thesis
│
├── paper_input/                 # Standard input folder (Place raw documents here)
│   └── Mathematics-thesis/      # Input files (main.tex, references.bib, media)
│
├── Mathematics-thesis-modified/ # Output directory (Clean, compile-ready LaTeX project)
│   ├── main.tex                 # Modified LaTeX output
│   └── references.bib           # Bibliography file (with new citations appended)
│
├── run.py                       # CLI execution entrypoint
└── README.md                    # Setup and usage documentation (this file)
```

---

## Separation of Concerns & Design Principles

1. **Functional Cohesion**: Each module has exactly one responsibility.
   - `core/parser.py` parses LaTeX documents into modifiable/non-modifiable zones and does nothing else.
   - `core/modifier.py` modifies the text strings using loaded rules and does not touch file I/O.
   - `core/generator.py` compiles summaries and report formatting.
2. **Data Coupling**: Modules exchange data via parameters and constructors rather than global variables or hardcoded constants.
3. **Configuration Isolation**: All paper-specific information (such as folder paths and `TOPIC_CITATIONS` keyword rules) is isolated in `paper_config/` modules.
4. **Editable Rules**: All academic synonym dictionaries, phrases, and technical terms are separated into human-editable JSON files in `rules/` so they can be modified without altering any python script code.

---

## Customizing Language Rules

The folder `rules/` contains three files generated automatically on the first run:

### 1. `rules/synonyms.json`
Contains word-level mappings. You can add your own words or adjust candidates:
```json
"important": [
  "significant",
  "crucial",
  "essential"
]
```

### 2. `rules/phrases.json`
Contains phrase rewrites to break Turnitin's N-gram scanner. Patterns use regular expression boundaries:
```json
[
  "\\bthis research paper\\b",
  "the present work"
]
```

### 3. `rules/protected_terms.json`
Contains terms that should **never** be paraphrased or modified under any circumstances (e.g., names of theorems, organizations, software):
```json
[
  "Fourier's Law",
  "Black-Scholes",
  "MATLAB"
]
```

---

## How to Run the Tool

### Step 1: Set up the Input
Place your raw LaTeX project files inside a folder in `paper_input/` (e.g. `paper_input/Mathematics-thesis/`). The directory must contain:
* A `main.tex` file (the main thesis source)
* A `references.bib` file (your bibliography)
* Any subfolders containing images or graphics (e.g., `media1/`, `media2/`)

### Step 2: Execute
Run the script from the root directory:
```bash
python run.py --config math_thesis
```
*(If `--config` is omitted, it defaults to `math_thesis`)*.

### Step 3: Review and Compile
1. Open the generated output folder: **`Mathematics-thesis-modified/`**
2. It is a **fully complete, self-contained project**. All media subfolders have been copied, and any new dummy references used in your text are automatically appended to the bottom of `references.bib`.
3. Open the folder in your LaTeX compiler (TeXpage, Overleaf, TeXstudio) and compile `main.tex`.

---

## Creating Configurations for New Papers

To run the tool on a different paper:
1. Create a folder in `paper_input/` and place the LaTeX files inside.
2. Create a new python file in `paper_config/` (e.g., `paper_config/physics_paper.py`).
3. Define the paths and config variables:
   ```python
   import os
   from collections import OrderedDict

   BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

   PROJECT_NAME = "physics_paper"
   INPUT_DIR = os.path.join(BASE_DIR, "paper_input", "physics_paper_folder")
   TEX_FILE = os.path.join(INPUT_DIR, "document.tex")
   BIB_FILE = os.path.join(INPUT_DIR, "citations.bib")
   OUTPUT_DIR = os.path.join(BASE_DIR, "physics_paper_modified")

   SYNONYM_AGGRESSIVENESS = 0.50
   RANDOM_SEED = 123
   MIN_SENTENCE_LENGTH_FOR_CITE = 50

   # Key physics topics to automatically cite
   TOPIC_CITATIONS = OrderedDict([
       (("quantum mechanics", "schrodinger", "wavefunction"),
        {"key": "ref_quantum_basics", "topic": "Foundations of Quantum Mechanics"}),
   ])
   ```
4. Run using the new configuration name:
   ```bash
   python run.py --config physics_paper
   ```
