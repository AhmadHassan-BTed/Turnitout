# Technical Decisions: Turnitout

This document outlines the major architectural and design decisions made in the development of Turnitout.

---

## 1. Rule-Based Preprocessing vs. Run-time LLM APIs
**Context**: Turnitin similarity reduction requires replacing phrases and adding citations. A naive approach would query an LLM (like GPT-4) at runtime to paraphrase the text.

**Decision**: A deterministic, rule-based and regex-based pipeline is used.
- **Why**:
  - **Zero Cost & Speed**: Run-time LLM APIs are expensive, have latency, and require API keys. A local Python script processes thousands of lines in milliseconds.
  - **Math Integrity**: LLMs frequently introduce subtle mathematical bugs or break custom LaTeX macros. By protecting math zones and running exact replacements, we guarantee compilation.
  - **Privacy**: The user's research papers and intellectual property are not sent to any third-party AI APIs during the preprocessing run.

---

## 2. Dynamic Auto-Detection of Projects
**Context**: Users processing new papers previously had to build separate JSON configs defining directories, filenames, and keywords.

**Decision**: Implement dynamic project auto-detection when running the CLI.
- **Why**: 
  - Allows zero-configuration runs for a layman.
  - Automatically identifies `.tex` and `.bib` files, extracts core keywords using local term-frequency counters, and configures path spaces.

---

## 3. Dynamic Externalization of Dictionaries
**Context**: Phrase rewrites, synonyms, and conjunctions are vocabulary databases. Storing them as hardcoded variables inside python scripts violates clean architecture code principles.

**Decision**: Externalize all dictionaries to JSON files under `rules/`.
- **Why**:
  - **Maintainability**: Contributors can expand or edit synonyms and terms without looking at or modification of the core code.
  - **Configuration Integrity**: Keeps the core script light, cohesive, and easily testable.

---

## 4. UI Layer Architecture (Tkinter & Streamlit)
**Context**: Desktop users need a lightweight native app (zero network/browser dependencies), while web users need a central browser-based deployment on Streamlit Cloud.

**Decision**: Reusable core helper functions are packaged into `turnitout.ui_shared`.
- **Why**: 
  - Allows both `streamlit_app.py` and `ui_launcher.py` to import identical logic wrappers, avoiding code duplication.
  - Prevents Tkinter GUI elements from causing dependency failures when building on Streamlit Community Cloud servers.

---

## 5. Decoupled Word Document (.docx) Processing
**Context**: Word Documents contain nested paragraph structures, table cells, headers, footers, and inline styles (bold, italics, run formatting) that simple text parsing destroys.

**Decision**: Implement a decoupled document processor in `doc_processor.py` that accepts a pipeline callback function.
- **Why**:
  - By passing the humanizer wrapper as an external argument, `doc_processor.py` is fully decoupled from Streamlit/Tkinter and CLI configurations.
  - Run-by-run processing is selectively triggered if custom formats (like bold, italics) are present, ensuring styling run properties are 100% preserved.

---

## 6. Logarithmic Intensity Mapping & Contextual Repetition Blocking
**Context**: A linear intensity slider is too crude for linguistic adjustments; small changes at the low end (where quality is highest) should be highly sensitive, whereas high-end changes should scale rapidly. Additionally, synonym/determiner replacements can cause repetitive word collisions.

**Decision**:
- Map the slider value to internal aggressiveness using an exponential curve (base-10 volume curve) where the default 75% setting maps to 20% internal aggressiveness.
- Filter out synonym replacements that are already present in the active sentence to prevent duplicate word collisions.
- Track determiners in a recently-used FIFO queue to block repetitive use of formal words (e.g. "aforementioned").

---

## 7. Metadata-Driven Rule Extensibility (AI Prompts)
**Context**: Rule extension (e.g. expanding synonyms or adverbs) by automated AI agents can sometimes result in incorrect, informal, or ungrammatical lists.

**Decision**: Include strict metadata `__prompt__` instruction blocks inside all JSON rules files (as root keys for objects, or as the index 0 element for arrays).
- **Why**: 
  - Directs any future AI agent editing the JSON file on the precise grammar rules, casing, and style boundaries for extensions.
  - Dynamically filtered out during rules loading by the Python runtime (`rules.py`), keeping the engine's configurations clean.
