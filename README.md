<h1 align="center">Turnitout</h1>

<p align="center">
  <strong>Intelligent LaTeX Plagiarism & Similarity Reduction Tool</strong>
</p>

<p align="center">
  <a href="https://github.com/AhmadHassan-BTed/Turnitout/actions"><img src="https://github.com/AhmadHassan-BTed/Turnitout/workflows/CI/badge.svg" alt="CI Build Status"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg" alt="Python Support"/></a>
  <a href="https://semver.org/"><img src="https://img.shields.io/badge/version-1.0.0--beta-orange.svg" alt="Semantic Versioning"/></a>
</p>

<p align="center">
  Created and maintained by <a href="https://github.com/AhmadHassan-BTed"><strong>Ahmad Hassan (B-Ted)</strong></a>.
</p>

---

## 💡 Preserving the Academic Voice

Writing is a deeply personal, human craft. Yet, under the rigid constraints of automated similarity scanners like Turnitin, researchers, students, and authors are often forced to rewrite their natural voice, break their equations, or spend days manually replacing phrases simply to bypass automated string matching. 

Turnitout resolves this friction. By automating the mechanical process of breaking up matching n-gram chains while leaving mathematical formulations, structure, and academic formatting untouched, Turnitout protects formatting integrity, allowing researchers to focus their energy on real scientific discovery.

---

## ⚡ Getting Started (3-Minute Setup)

Turnitout runs out-of-the-box with zero configuration required. Follow these simple steps:

### 1. Install Python
* Download and install Python from [python.org/downloads](https://www.python.org/downloads/).
* **Windows Users**: Ensure the box that says **"Add Python to PATH"** is checked during setup.

### 2. Prepare the Input Folder
1. Locate the **`paper_input/`** folder in this directory.
2. Copy your LaTeX paper folder into it (e.g., copy a folder named `MyPaper` containing `main.tex`, `references.bib`, and any image assets).

### 3. Run the Process
1. Open a terminal or command prompt in this directory.
   - *Windows Shortcut*: Open this folder in File Explorer, click the address bar, type `cmd`, and press Enter.
2. Execute the following command:
   ```bash
   python run.py
   ```
3. The pipeline will automatically scan your folder, run keyword analysis, and perform similarity reduction.

### 4. Finalize Citations with AI
1. Go to the **`paper_output/`** directory and open the generated folder.
2. Open the file **`ai_prompt.txt`** (which has been generated for you).
3. **Copy the entire text** and paste it directly into ChatGPT, Claude, or Gemini.
4. Copy the AI's BibTeX response and paste it at the bottom of the **`references.bib`** file in your output folder.
5. Upload the output folder to Overleaf or compile it locally. The document is compile-ready.

---

## 🛠️ Advanced Customization & Configurations

For advanced use cases, settings and overrides can be customized easily:

### Configuration Parameters
Overrides are controlled via environment variables inside a `.env` file placed at the project root:

| Variable | Description | Type | Default |
| --- | --- | --- | --- |
| `TURNITOUT_AGGRESSIVENESS` | Probability rate of swapping words with synonyms | Float (`0.0`-`1.0`) | `0.75` |
| `TURNITOUT_MIN_SENTENCE_LEN` | Minimum char length of a sentence to inject citations | Integer | `45` |
| `TURNITOUT_RANDOM_SEED` | Seed value ensuring output reproducibility | Integer | `42` |

<details>
<summary><b>⚙️ View Configuration File Example</b></summary>

Copy `.env.example` to `.env` to configure your overrides:
```bash
# Synonym aggressiveness (float value between 0.0 and 1.0)
TURNITOUT_AGGRESSIVENESS=0.75

# Minimum sentence length for citation insertion (integer)
TURNITOUT_MIN_SENTENCE_LEN=45

# Random seed (integer)
TURNITOUT_RANDOM_SEED=42
```
</details>

<details>
<summary><b>📂 View Project File Directory Structure</b></summary>

```text
Turnitout/
├── .github/                  # Community configurations and workflows
│   ├── CODE_OF_CONDUCT.md    # Contributor Covenant Code of Conduct
│   ├── CONTRIBUTING.md       # Onboarding guide
│   ├── SECURITY.md           # Security disclosure instructions
│   └── SUPPORT.md            # Community support directions
├── configs/                  # Paper-specific configurations
├── docs/                     # Release documentation, roadmaps, and guides
│   ├── architecture.md       # LaTeX parser zone structures
│   ├── changelog.md          # Semantic version history log
│   ├── getting-started.md    # Detailed onboarding user guide
│   └── roadmap.md            # Project milestone planning
├── paper_input/              # Raw document input folder
├── paper_output/             # Paraphrased clean document output folder
├── rules/                    # Editable rules database JSON files
├── src/                      # Packaged source directory
│   └── turnitout/
│       ├── __init__.py
│       ├── cli.py            # CLI Runner orchestrator
│       ├── config.py         # Config loader & environment parser
│       └── core/
│           ├── parser.py     # Structural LaTeX tokenizer
│           ├── modifier.py   # Mutation pipeline engine
│           ├── generator.py  # References & report compiler
│           ├── rules.py      # Rule file JSON loader
│           └── utils.py      # LaTeX syntax validation checkers
├── tests/                    # Automated testing suite
├── .editorconfig             # Standardized indent styles
├── .env.example              # Environment variable overrides template
├── .gitattributes            # Line normalization rules (eol=lf)
├── .gitignore                # Target directories exclusion definitions
├── LICENSE                   # MIT License
├── README.md                 # Project documentation (this file)
├── pyproject.toml            # Python package setup & test configurations
└── run.py                    # Root launcher wrapper calling CLI module
```
</details>

---

## 🏗️ Under the Hood: System Architecture

The following sections illustrate the internal flow, zone tokenization, and data structures:

### 1. Processing Pipeline
The document undergoes structural zoning before modification to ensure mathematical equations, formatting macros, and citations remain intact:

```mermaid
flowchart TD
    subgraph Inputs ["1. Setup & Inputs"]
        Raw["Raw LaTeX Document\n(main.tex)"]
        Env[".env Configuration\n(Aggressiveness, Seed)"]
    end
    subgraph Parser ["2. LaTeXZoneParser"]
        Z1["Preamble & Setup\n(SKIP Zone)"]
        Z2["Equations & Matrices\n(MATH Zone)"]
        Z3["Prose Paragraphs\n(PROSE Zone)"]
        Z4["Chapter/Section Titles\n(HEADING Zone)"]
    end
    subgraph Modifier ["3. TextModifier Mutation Engine"]
        PH["Mask LaTeX Commands"]
        PR["Apply Phrase Rewrites"]
        SR["Apply Synonym Replacements"]
        CO["Reorder Clauses"]
        DS["Swap Determiners"]
        CS["Split Compound Sentences"]
        HI["Insert Hedge Words"]
        NB["N-gram Chain Breaker"]
        UN["Unmask LaTeX Commands"]
        CI["Inject Citations"]
    end
    subgraph Output ["4. Output Compilation"]
        Mod["Paraphrased main.tex"]
        Bib["references.bib with appended references"]
        Prompt["ai_prompt.txt (AI prompt template)"]
    end

    Raw --> Parser
    Env --> Modifier
    Z3 --> Modifier
    Modifier --> Output
```

### 2. Internal Module Coupling
The codebase is structured to enforce high functional cohesion and clear interface boundaries:

```mermaid
graph TD
    classDef package fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px;
    classDef module fill:#fffde7,stroke:#f57f17,stroke-width:1.5px;
    
    subgraph Package ["turnitout package"]
        cli["cli.py\n(CLI Orchestrator)"]:::module
        config["config.py\n(Config Loader)"]:::module
        core["core package"]:::package
        
        subgraph core ["core package"]
            parser["parser.py\n(LaTeX Zone Parser)"]:::module
            modifier["modifier.py\n(Mutation Engine)"]:::module
            rules["rules.py\n(JSON rule Loader)"]:::module
            generator["generator.py\n(Report Compiler)"]:::module
            utils["utils.py\n(LaTeX Checkers)"]:::module
        end
    end
    
    cli --> config
    cli --> parser
    cli --> modifier
    cli --> generator
    cli --> utils
    modifier --> rules
```

---

## 🧪 Testing & Developer Workflow

### local Testing
Tests are designed to verify syntax-safety and programmatic API contracts:
```bash
# Install development dependencies
pip install -e .[dev]

# Run unit tests
python -m pytest

# Check code formatting & linting
black --check src/ tests/
flake8 src/ tests/
```

### Contribution Integration
New modifications are validated automatically via CI checks:

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Contributor
    participant Git as Git Branch
    participant Lint as Linter & Formatter
    participant Test as Pytest Suite
    participant GA as GitHub Actions CI
    
    Dev->>Git: Create branch (feature/name)
    Dev->>Lint: Check formatting (black, flake8)
    Dev->>Test: Run local tests (pytest)
    Dev->>Git: Commit and push changes
    Git->>GA: Trigger automated check workflows
    GA-->>Dev: Build status result (Pass/Fail)
```

Detailed guides are located in [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md).

---

## 🛡️ Release, Support & Security

- **Release Changes**: History logs are available in [docs/changelog.md](docs/changelog.md).
- **Milestone Planning**: Upcoming changes are outlined in [docs/roadmap.md](docs/roadmap.md).
- **Support Directions**: Guidelines are available in [SUPPORT.md](.github/SUPPORT.md).
- **Security Reporting**: Vulnerabilities should be reported according to [SECURITY.md](.github/SECURITY.md).
