# Turnitout Architecture & Rule Management Guidelines

This document outlines the strict coding and design constraints established for this repository. All developers contributing to the project must adhere to these guidelines.

## 1. Decoupling Words and Dictionaries from Source Code

**CRITICAL RULE**: Do not define or hardcode any lists of words, synonym dictionaries, adverbs, helper verbs, conjunctions, or regex pattern lists directly inside Python source files (e.g. `similarity_evasion.py`, `ai_evasion.py`, `modifier.py`, etc.).

### Rationale
* **Asset Decoupling**: Keep language and parsing data completely separate from core processing code.
* **Easy Maintenance**: Content adjustments can be made directly in the JSON files under the `rules/` directory without editing source code.
* **Architecture Integrity**: Ensures that the pipeline code focuses strictly on logic, flow, and parsing, rather than linguistic databases.

---

## 2. JSON Prompt Metadata & Rule Formatting

All JSON rule files must contain a `__prompt__` metadata block as instructions for future AI agents to extend the file without introducing incorrect or ungrammatical words.

### Dictionary Mappings (JSON Objects)
For JSON files structured as objects/dictionaries (e.g. `determiners.json`), define `__prompt__` as a direct key:
```json
{
  "__prompt__": "Role: Syntactic Variator...\nRules:\n- ...",
  "a": ["a certain", "a given"]
}
```

### Word Lists (JSON Arrays)
For JSON files structured as lists/arrays (e.g. `qualifiers.json`), the **first element** (index 0) of the array must be an object containing the `__prompt__` key:
```json
[
  {
    "__prompt__": "Role: Adverbial Evasion Generator...\nRules:\n- ..."
  },
  "notably",
  "indeed"
]
```
The dynamic rules loader automatically filters out the `__prompt__` key/element during import.

---

## 3. Rule Configuration Directory (`rules/`)

All dictionary lists and mappings must reside as JSON files inside the `rules/` folder at the root of the workspace:

```
rules/
├── synonyms.json
├── phrases.json
├── protected_terms.json
├── qualifiers.json            <-- Adverb qualifiers for Option B (with Array Prompt)
├── subject_indicators.json    <-- Pronouns/Articles for list division checks (with Array Prompt)
├── helper_verbs.json          <-- Verbs used in safe qualifier checks (with Array Prompt)
├── adj_suffixes.json          <-- Suffixes used in safe qualifier checks (with Array Prompt)
├── common_past_verbs.json      <-- Fallback verbs list for active-to-passive conversion (with Array Prompt)
├── sentence_fusion_connectors.json (with Array Prompt)
├── dependent_starts.json      <-- Conjunctions/pronouns for sentence rotation (with Array Prompt)
└── split_patterns.json        <-- Conjunction split regexes (with Array Prompt)
```

---

## 4. Dynamic Rule Loading in Python

All JSON rule files must be loaded dynamically inside [rules.py](file:///p:/Plagerism%20Similarity%20Remove/src/turnitout/core/rules.py). 

### How to add a new word list:
1. Create a corresponding JSON file in `rules/` (e.g. `my_new_words.json`) with an appropriate prompt.
2. Open `rules.py` and register the file path:
   ```python
   my_new_words_path = os.path.join(RULES_DIR, "my_new_words.json")
   ```
3. Add it to the verification check list (`required_paths`).
4. Load the file using the `load_json_file(my_new_words_path)` helper.
5. Return the value from `load_rules()` and assign it to a capitalized constant, which is then imported in the transformers:
   ```python
   from turnitout.core.rules import MY_NEW_WORDS_CONSTANT
   ```

---

## 5. Part of Speech Safe Qualifier Target checks

When modifying Option B (qualifier injection), always use the `is_safe_qualifier_target` helper to locate helper verbs, adjectives, or past/present verbs. Do not hardcode adverbs inline; instead use:
```python
qualifier = rng.choice(QUALIFIERS)
```
