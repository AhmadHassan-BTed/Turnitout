# Structured Tone-Specific Rules Architecture

All stylistic and syntactic rules are externalized to JSON files under the `rules/` directory, separated by tone. This ensures complete maintainability and ease of extending or adding new tones.

## ✅ Completed Tasks

- [x] **Proper File Structure for Each Tone**: Grouped qualifiers, hedges, determiners, and punctuation break lists into tone-specific subdirectories (`academic/` and `conversational/`) under `rules/`.
- [x] **No Hardcoded Words in Code**: Removed hardcoded adverbs, parentheticals, and determiner lists inside `similarity_evasion.py`, `ai_evasion.py`, and `modifier.py` and replaced them with dynamic parameters.
- [x] **Prompt-Based Rules Schema**: Every JSON rule file includes an instruction block under `__prompt__` (for dictionaries) or as the first element (for lists) to maintain consistency and support future automated generation.
- [x] **Global Rules Loader**: Updated `src/turnitout/core/rules.py` to dynamically check, load, and export these tone-specific JSONs on import.
- [x] **Preset-Aware Application**: Configured `DeterminerSwapTransformer`, `HedgeWordTransformer`, `BreakNgramChainTransformer`, and `SourceAwareNgramAuditTransformer` to dynamically apply the respective lists based on the active style preset (`academic` or `conversational`).

---

## Directory Layout

```
rules/
├── academic/
│   ├── determiners.json
│   ├── hedge_words.json
│   ├── ngram_inserts.json
│   └── qualifiers.json
├── conversational/
│   ├── determiners.json
│   ├── hedge_words.json
│   ├── ngram_inserts.json
│   └── qualifiers.json
└── excluded_ing_nouns.json (shared grammar exception list)
```

### 1. `academic/` (Formal Preset Rules)
* `determiners.json`: Academic syntactic variations (e.g., `the` ↔ `this`/`that`).
* `hedge_words.json`: Formal arguments mitigation (e.g., `perhaps`, `arguably`, `potentially`).
* `ngram_inserts.json`: Academic parenthetical insertions to disrupt sliding windows (e.g., `, namely,`, `, specifically,`).
* `qualifiers.json`: Formal adverbs inserted at safe targets (e.g., `notably`, `essentially`, `particularly`).

### 2. `conversational/` (Daily English Preset Rules)
* `determiners.json`: Safe, casual syntactic variations (minimizes robotic article swaps).
* `hedge_words.json`: Casual speech mitigations (e.g., `maybe`, `probably`, `likely`).
* `ngram_inserts.json`: Conversational parenthetical insertions (e.g., `, you know,`, `, basically,`, `, in fact,`).
* `qualifiers.json`: Everyday adverbs (e.g., `really`, `actually`, `simply`, `truly`).

### 3. Shared Grammar Safeguard
* `excluded_ing_nouns.json`: Exception dictionary containing common nouns ending in `-ing` (e.g., `engineering`, `building`) that must not be split by adverb insertions.
