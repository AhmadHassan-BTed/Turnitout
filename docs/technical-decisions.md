# Technical Decisions — Turnitout

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
