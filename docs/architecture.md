# System Architecture — Turnitout

Turnitout utilizes a deterministic, modular pipeline to reduce plagiarism and similarity indices in LaTeX documents. It prioritizes semantic preservation and syntax security.

---

## High-Level System Workflow

```mermaid
flowchart TD
    A[Raw LaTeX Input] --> B[LaTeXZoneParser]
    B --> C[Zone Breakdown: PROSE, MATH, SKIP, HEADING]
    C --> D[TextModifier]
    D --> E[1. LaTeX Commands Protection]
    E --> F[2. Phrase Rewrites]
    F --> G[3. Synonym Replacements]
    G --> H[4. Clause Reordering]
    H --> I[5. Determiner Swaps]
    I --> J[6. Compound Splits]
    J --> K[7. Hedge Insertions]
    K --> L[8. N-gram Chain Breaker]
    L --> M[9. LaTeX Restorations]
    M --> N[10. Topic Citation Appender]
    N --> O[Modified LaTeX main.tex]
    N --> P[ai_prompt.txt Template]
```

---

## Core Components

### 1. Configuration & Environments (`turnitout.config`)
- Loads settings from `configs/*.json` or performs folder auto-detection inside `paper_input/`.
- Merges configurations with `.env` settings (for parameters like random seed or aggressiveness threshold), enforcing standard priority rules.

### 2. LaTeX Parser (`turnitout.core.parser`)
- Scans files line-by-line to isolate prose from LaTeX syntax.
- Places lines into strict zone categories:
  - `PROSE`: Modifiable text body lines.
  - `HEADING`: Header rows (subject to light edits like phrase rewrites; never synonym replaced).
  - `MATH`: Display/inline equations (completely untouchable).
  - `SKIP`: Preamble, figures, bibliography, code listings, and tables (completely untouchable).

### 3. Text Modifier (`turnitout.core.modifier`)
- Operates on a character-level placeholder engine to temporarily mask all remaining LaTeX commands (e.g. `\textbf`, `\cite`) inside prose lines.
- Sequentially executes 8 pipeline stages:
  1. **Masking**: Replaces LaTeX syntax with temporary indicators (`\x00PH0000\x00`).
  2. **Phrase Rewrites**: Replaces long, flagged academic idioms with concise alternatives.
  3. **Synonym Replacements**: Iterates over tokens and rolls for synonym swaps against the custom JSON dictionary.
  4. **Clause Reordering**: Switches subordinate clause positions (e.g. "Main clause, since sub clause" -> "Since sub clause, main clause").
  5. **Determiner Swaps**: Switches determiners contextually.
  6. **Compound Splits**: Breaks long compound sentences into smaller sentences to disrupt sequential word matches.
  7. **Hedge Insertions**: Inserts academic qualifiers (like "notably", "essentially") near clause breaks.
  8. **N-gram Chain Breaker**: Scans lines for remaining consecutive word chains of length 5+ and inserts parentheticals like `(i.e.,)`.
  9. **Restoration**: Recursively unmasks the placeholder indicators.
  10. **Citations**: Automatically appends `\cite{...}` if keywords match a configured citation topic.
