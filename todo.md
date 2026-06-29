# 🔓 Turnitout Extension — Cracking Turnitin's Algorithm

> **How to use this guide:**  
> For each section below:  
> 1. **Copy the file content** from the specified path and paste it to the AI  
> 2. **Then copy-paste the prompt** from that section  
> 3. Wait for the AI to return the extended file  
> 4. Replace the original file with the AI's output  
> 5. Move to the next section  

> [!IMPORTANT]  
> **Do them IN ORDER.** Section 1 (modifier.py) must be done first because later files depend on it.

---
---

## 📁 SECTION 1 — modifier.py (THE CORE ENGINE)

**File to paste first:** [modifier.py](file:///c:/Users/PMLS/Downloads/Plagerism%20Similarity%20Remove/src/turnitout/core/modifier.py)  
**Path:** `src/turnitout/core/modifier.py`

**After pasting the file, send this prompt:**

````
Here is `modifier.py` — the core transformation engine of "Turnitout", a tool that defeats Turnitin's similarity AND AI detection by applying intelligent text modifications to LaTeX academic documents.

# ═══════════════════════════════════════════════════════════
# PART 1: HOW TURNITIN'S SIMILARITY DETECTION WORKS (CRACKED)
# ═══════════════════════════════════════════════════════════

Turnitin's similarity engine is built on the **Winnowing Algorithm** (Schleimer, Wilkerson & Aiken, 2003 — "Winnowing: Local Algorithms for Document Fingerprinting"). Here's the EXACT internal process:

## Step 1: Text Preprocessing
- Strips ALL formatting (bold, italic, font changes — meaningless)
- Converts to lowercase
- Removes ALL punctuation and whitespace
- Result: a single continuous stream of lowercase words

## Step 2: K-gram Generation (NOT simple n-grams)
- Generates **k-grams** where k=5 (5 consecutive words)
- Example: "we analyze the heat equation" → one k-gram
- A sliding window moves one word at a time
- For a 100-word paragraph: generates 96 k-grams

## Step 3: Karp-Rabin Rolling Hash
- Each k-gram is hashed using **Karp-Rabin rolling hash** into a 32/64-bit integer
- Rolling hash means each new hash is computed from the previous one in O(1)
- "we analyze the heat equation" → hash 0x7A3F29B1
- Change ONE word: "we examine the heat equation" → hash 0x1D8E44C7 (COMPLETELY different)

## Step 4: Winnowing — Fingerprint Selection (THE KEY)
- Turnitin does NOT store ALL hashes (too expensive)
- It uses a **window of w=4** hashes and selects the MINIMUM hash in each window
- This creates a sparse set of "fingerprints" — roughly 1 fingerprint per 2-3 words
- **GUARANTEE**: Any matching passage of length ≥ k+w-1 = **8 consecutive words** is ALWAYS detected
- Passages of 5-7 matching words MIGHT be caught (depends on which hash gets selected as minimum)
- Passages of 1-4 matching words are NEVER caught

## Step 5: Database Comparison
- Fingerprints are compared against 1.5+ BILLION student papers, 99,000+ journals, and 70+ BILLION web pages
- Each fingerprint lookup is O(1) using hash tables
- Matching fingerprints = matching text passages

## Step 6: Match Clustering & Scoring
- Adjacent/nearby matching fingerprints are grouped into "flagged passages"
- Small isolated matches (single fingerprint) are ignored as coincidental
- Clusters of 3+ adjacent matching fingerprints trigger a flag
- Similarity % = (total words in flagged passages / total words in document) × 100

## CRITICAL VULNERABILITIES:
| Vulnerability | Why It Works | Attack Vector |
|--------------|-------------|---------------|
| k=5 word window | Changing ANY 1 word in 5 generates new hash | Synonym replacement |
| 8-word guarantee | Only 8+ word chains are 100% caught | Break ALL chains ≥5 words |
| Hash is order-dependent | Same words in different order = different hash | Clause reordering |
| Punctuation stripped | Inserting commas/periods doesn't help | Must change ACTUAL WORDS |
| Lowercased | Capitalization changes don't help | Must change ACTUAL WORDS |
| Min-hash selection | Some 5-7 word matches slip through | But we target ALL of them |
| Clustering threshold | Isolated single matches are ignored | Scatter modifications evenly |

# ═══════════════════════════════════════════════════════════
# PART 2: HOW TURNITIN'S AI DETECTION WORKS (CRACKED)
# ═══════════════════════════════════════════════════════════

Turnitin's AI detector (launched 2023, continuously updated) uses a multi-signal classifier. Here's how it works internally:

## Signal 1: Perplexity Scoring
- Feeds text through a language model and measures how "surprised" the model is by each word
- **AI-generated text has LOW perplexity** (very predictable, smooth, expected word choices)
- **Human-written text has HIGH perplexity** (surprising word choices, unusual phrasing, domain-specific jargon)
- Turnitin flags text with consistently low perplexity as AI-generated
- **TO DEFEAT**: Use unusual/rare synonyms, unexpected transitions, domain-specific technical vocabulary, and deliberately "imperfect" phrasing

## Signal 2: Burstiness Analysis
- Measures the VARIATION in sentence complexity across the document
- **AI text has LOW burstiness** — sentences are uniformly complex, similar lengths, predictable rhythm
- **Human text has HIGH burstiness** — wild variation: some very short sentences, some extremely long ones, some simple, some complex
- **TO DEFEAT**: Deliberately create extreme sentence-length variation. Mix 5-word sentences with 50-word sentences. Split some, fuse others. Create rhythm irregularity.

## Signal 3: Token Probability Distribution
- For each word, calculates the probability that a language model would choose that specific word
- **AI always picks high-probability tokens** — the "obvious" next word
- **Humans often pick low-probability tokens** — unusual word choices, rare synonyms, unexpected turns
- **TO DEFEAT**: Replace common words with RARER synonyms. Use "elucidate" instead of "explain", "corroborate" instead of "confirm", "delineate" instead of "describe". The rarer the synonym, the more "human" it looks.

## Signal 4: Stylometric Uniformity
- **Sentence length distribution**: AI produces a normal distribution with tight standard deviation. Humans produce irregular distributions.
- **Type-token ratio (TTR)**: AI has LOWER vocabulary diversity (repeats the same words). Humans use MORE diverse vocabulary.
- **Function word patterns**: AI uses function words (the, is, of, in) in statistically regular patterns. Humans are irregular.
- **TO DEFEAT**: Vary vocabulary aggressively. Never use the same transition word twice in a row. Vary sentence structure wildly.

## Signal 5: Entropy Analysis
- Measures randomness/unpredictability in word choice sequences
- **AI text has LOW entropy** — predictable patterns
- **Human text has HIGH entropy** — appears more random
- **TO DEFEAT**: Inject parenthetical asides, appositives, hedging language, discourse markers — things that add "noise" to the statistical signal.

## AI DETECTION VULNERABILITY MATRIX:
| Detection Signal | What Triggers It | What Defeats It |
|-----------------|-----------------|-----------------|
| Low perplexity | Predictable word choices | Rare synonyms, unusual phrasing |
| Low burstiness | Uniform sentence lengths | Sentence splitting + fusion (create variance) |
| High-prob tokens | "Obvious" word choices | Replace with rarer academic synonyms |
| Uniform style | Same sentence structure | Clause reordering, voice swaps, nominalization |
| Low entropy | Predictable patterns | Hedge words, appositives, parentheticals, discourse markers |

# ═══════════════════════════════════════════════════════════
# PART 3: YOUR TASK — EXTEND modifier.py
# ═══════════════════════════════════════════════════════════

The current pipeline has 10 stages. You must ADD 7 new stages that SPECIFICALLY target the vulnerabilities identified above. Insert them BETWEEN Step 8 (`_break_ngram_chains`) and Step 9 (`_restore_latex`).

Each new stage description includes which Turnitin signals it attacks.

## NEW STAGES TO ADD:

### Stage A: `_transform_voice()` — Active↔Passive Voice Transformation
**Attacks**: Winnowing (reorders words → new hashes), AI Detection (breaks stylometric uniformity, increases burstiness)
- Detect active voice and convert to passive (and vice versa)
- "We analyzed the results" → "The results were analyzed"
- "The method was applied by researchers" → "Researchers applied the method"  
- "The study examines the impact" → "The impact is examined in the study"
- "Scientists have demonstrated that" → "It has been demonstrated by scientists that"
- Use regex patterns matching subject-verb-object patterns
- Include a list of at least 20 common academic verbs with their passive forms (analyze→was analyzed, demonstrate→was demonstrated, investigate→was investigated, etc.)
- 30% fire rate, only on sentences 60+ chars
- Skip lines with LaTeX placeholders (`\x00`)
- **WHY THIS DEFEATS TURNITIN**: Completely rearranges word order → every k-gram in the sentence generates new hashes. Also breaks AI detection's stylometric uniformity by mixing voice types unpredictably.
- Counter: `self.voice_transform_count`

### Stage B: `_fuse_sentences()` — Sentence Fusion (Anti-Burstiness Weapon)
**Attacks**: AI Detection (creates sentence-length variation = high burstiness), Winnowing (merged sentence = new k-grams at junction point)
- This stage works at a HIGHER level — it needs awareness of adjacent lines
- Accept optional `context_lines` parameter
- Detect when the CURRENT line is short (<80 chars) and the NEXT context line is also short
- Fuse them with connectors: "which", "thereby", "consequently", "thus leading to", "and as a result"
- "The temperature increased. This caused expansion." → "The temperature increased, which consequently caused expansion."
- "The method converges quickly. It requires fewer iterations." → "The method converges quickly, thereby requiring fewer iterations."
- 25% fire rate
- Produce LONGER sentences to counterbalance the sentence-splitting stage — this creates the burstiness variance that defeats AI detection
- Counter: `self.sentence_fusion_count`

### Stage C: `_inject_transitions()` — Transition Phrase Injection (Anti-Perplexity Weapon)
**Attacks**: AI Detection (increases entropy, adds "noise" to token probability), Winnowing (inserts new words into k-gram chains)
- Maintain a categorized dictionary of 40+ transition phrases:
  - **Addition**: "furthermore", "in addition", "moreover", "additionally", "also of note", "equally important", "by the same token", "coupled with this"
  - **Contrast**: "conversely", "on the other hand", "in contrast", "by comparison", "paradoxically", "counterintuitively"
  - **Cause/Effect**: "consequently", "as a result", "therefore", "thus", "accordingly", "for this reason", "on account of this"
  - **Clarification**: "in other words", "that is to say", "specifically", "to clarify", "put differently", "stated another way"
  - **Sequence**: "subsequently", "following this", "in the next stage", "thereafter", "in turn", "proceeding further"
  - **Emphasis**: "indeed", "in fact", "notably", "remarkably", "crucially", "most importantly"
  - **Concession**: "admittedly", "granted", "to be sure", "it must be acknowledged", "notwithstanding this"
- Insert at sentence boundaries or after commas, 25% fire rate, 70+ char sentences only
- IMPORTANT: Track which transitions have been used recently to AVOID repetition (repetition = lower entropy = triggers AI detection)
- Counter: `self.transition_inject_count`

### Stage D: `_reorder_within_clause()` — Clause-Level Word Reordering (Hash Destroyer)
**Attacks**: Winnowing (same words in different order = completely different hashes), AI Detection (breaks predictable sentence structure)
- Rearrange prepositional phrases and adverbial modifiers within clauses
- "In this chapter, we present the results of our analysis" → "We present, in this chapter, the results of our analysis"
- "Using the finite difference method, we solved the equation" → "We solved the equation using the finite difference method"
- "For the purpose of validation, three test cases were selected" → "Three test cases were selected for the purpose of validation"
- Target patterns: "In/For/Using/By/With/Through X, [clause]" → "[clause], in/for/using/by/with/through X"
- Also handle end-position modifiers: "[clause] by means of X" → "By means of X, [clause]"
- 20% fire rate, 80+ char sentences
- **WHY THIS IS DEVASTATING**: The Karp-Rabin hash is ORDER-DEPENDENT. Same words in different positions produce completely different hashes. This breaks every single k-gram that spans the reordered section.
- Counter: `self.clause_word_reorder_count`

### Stage E: `_nominalize()` — Nominalization / De-nominalization (Structure Destroyer)
**Attacks**: AI Detection (alters sentence structure drastically = defeats stylometric analysis), Winnowing (completely different word forms = new hashes)
- Convert verbs to noun forms and vice versa, restructuring the sentence:
- Maintain a dictionary of 30+ verb↔noun pairs:
  ```
  analyze → analysis, investigate → investigation, apply → application,
  develop → development, improve → improvement, evaluate → evaluation,
  derive → derivation, compute → computation, simulate → simulation,
  approximate → approximation, converge → convergence, vary → variation,
  solve → solution, implement → implementation, formulate → formulation,
  transform → transformation, integrate → integration, differentiate → differentiation,
  observe → observation, measure → measurement, determine → determination,
  classify → classification, optimize → optimization, validate → validation,
  demonstrate → demonstration, establish → establishment, reduce → reduction,
  extend → extension, modify → modification, construct → construction
  ```
- Verb→Noun: "We investigated the phenomenon" → "An investigation of the phenomenon was conducted"
- Noun→Verb: "The application of the method" → "Applying the method"
- Noun→Verb: "The computation of eigenvalues" → "Computing the eigenvalues"
- 20% fire rate, 70+ char sentences
- **WHY THIS IS DEVASTATING**: Changes part of speech, sentence structure, AND word forms simultaneously. A single nominalization can destroy 3-4 k-grams at once. Also dramatically alters the stylometric fingerprint.
- Counter: `self.nominalization_count`

### Stage F: `_inject_appositives()` — Appositive Clause Injection (Entropy Bomb)
**Attacks**: AI Detection (massive entropy increase — inserts "unexpected" text that a language model would never predict), Winnowing (injects 4-8 new words into k-gram chains)
- Insert brief definitional/clarifying phrases after key technical terms
- Maintain a dictionary of 25+ term→appositive mappings:
  ```
  "finite difference" → "a discretization technique for differential equations"
  "Crank-Nicolson" → "an implicit second-order-accurate scheme"
  "boundary condition" → "a constraint imposed on the solution domain"
  "convergence" → "the tendency of a numerical sequence toward a limiting value"
  "stability" → "the property ensuring bounded error growth"
  "truncation error" → "the discrepancy between exact and discrete operators"
  "eigenvalue" → "a characteristic scalar of a linear transformation"
  "discretization" → "the process of converting continuous models to discrete form"
  "initial condition" → "the prescribed state at the starting time"
  "explicit method" → "a scheme computing future states from known values"
  "implicit method" → "a scheme requiring simultaneous solution of coupled equations"
  "differential equation" → "a mathematical relation involving derivatives"
  "partial derivative" → "a derivative with respect to one variable while others are held fixed"
  "numerical method" → "a computational algorithm for approximate solutions"
  "iterative process" → "a repetitive procedure converging toward a solution"
  "linear system" → "a set of equations involving linear combinations"
  "approximation" → "a value or expression close to the exact quantity"
  "error analysis" → "the systematic study of numerical inaccuracies"
  "time step" → "the discrete temporal increment in a marching scheme"
  "grid spacing" → "the distance between adjacent mesh nodes"
  "wave equation" → "a second-order PDE governing oscillatory phenomena"
  "heat equation" → "a parabolic PDE describing thermal diffusion"
  "Laplace equation" → "an elliptic PDE characterizing steady-state distributions"
  "Black-Scholes" → "a celebrated model for option pricing in mathematical finance"
  "stochastic process" → "a time-indexed collection of random variables"
  ```
- Format: "The Crank-Nicolson method" → "The Crank-Nicolson method, an implicit second-order-accurate scheme,"
- **CRITICAL**: Only inject each appositive ONCE per document. Track with `self._used_appositives = set()`
- 35% fire rate
- **WHY THIS IS AN ENTROPY BOMB**: Appositives inject 5-10 completely unexpected words that NO language model would predict at that position. This sends the perplexity score through the roof (= looks human) and simultaneously shatters 2-3 k-gram chains.
- Counter: `self.appositive_count`

### Stage G: `_rotate_discourse_markers()` — Discourse Marker Rotation (Anti-Repetition Shield)
**Attacks**: AI Detection (prevents the repetitive discourse patterns that AI detection looks for), Winnowing (different marker = different hash)
- Replace discourse markers with equivalent alternatives:
  ```
  "However" → ["Nevertheless", "Nonetheless", "On the other hand", "That said", "Be that as it may"]
  "Therefore" → ["Consequently", "Hence", "As a result", "It follows that", "Accordingly"]
  "Moreover" → ["Furthermore", "In addition", "Additionally", "What is more", "Beyond this"]
  "Although" → ["Even though", "Despite the fact that", "Notwithstanding", "While it is true that", "Granted that"]
  "Thus" → ["Hence", "Accordingly", "As such", "In this manner", "By this means"]
  "Indeed" → ["In fact", "Certainly", "As a matter of fact", "To be sure", "Without question"]
  "Similarly" → ["Likewise", "In a similar manner", "Comparably", "By the same token", "Along these lines"]
  "Specifically" → ["In particular", "More precisely", "To be specific", "Namely", "That is"]
  "Notably" → ["Remarkably", "Significantly", "Importantly", "Strikingly", "Conspicuously"]
  "Meanwhile" → ["In the interim", "Concurrently", "At the same time", "Simultaneously", "During this period"]
  "Conversely" → ["On the contrary", "In contrast", "By contrast", "Contrastingly", "On the flip side"]
  "Ultimately" → ["In the final analysis", "At the end of the day", "When all is considered", "In the last analysis"]
  "Evidently" → ["Apparently", "As it turns out", "It appears that", "Seemingly", "Ostensibly"]
  "Essentially" → ["Fundamentally", "At its core", "In essence", "Basically", "At the heart of it"]
  "Typically" → ["Generally", "Ordinarily", "As a rule", "In most cases", "Under normal circumstances"]
  ```
- Track which replacement was used for each marker to NEVER use the same replacement twice in a document
- 50% fire rate (these are safe, high-value swaps — they change a word that appears in nearly every k-gram window around them)
- **WHY THIS DEFEATS AI DETECTION**: AI models have a strong tendency to use the SAME discourse markers repeatedly ("However", "Therefore", "Moreover"). Turnitin's AI detector specifically looks for this repetitive pattern. By rotating markers to DIFFERENT equivalents each time, the text exhibits the varied discourse marker usage characteristic of human writing.
- Counter: `self.discourse_rotate_count`

## PIPELINE ORDER IN `modify_line()`:

After adding new stages, the FULL pipeline should be:
```
Step 1:  _protect_latex()           ← existing
Step 2:  _apply_phrase_rewrites()   ← existing
Step 3:  _apply_synonyms()          ← existing
Step 4:  _reorder_clauses()         ← existing
Step 5:  _swap_determiners()        ← existing
Step 6:  _split_compound_sentences()← existing
Step 7:  _insert_hedge_words()      ← existing
Step 8:  _break_ngram_chains()      ← existing
Step 9:  _transform_voice()         ← NEW (A)
Step 10: _fuse_sentences()          ← NEW (B)
Step 11: _inject_transitions()      ← NEW (C)
Step 12: _reorder_within_clause()   ← NEW (D)
Step 13: _nominalize()              ← NEW (E)
Step 14: _inject_appositives()      ← NEW (F)
Step 15: _rotate_discourse_markers()← NEW (G)
Step 16: _restore_latex()           ← existing
Step 17: _maybe_add_citation()      ← existing
```

## CRITICAL RULES:

1. **NEVER break LaTeX**. All new stages operate AFTER `_protect_latex()` and BEFORE `_restore_latex()`. If `'\x00'` is in the text, skip complex transformations.
2. **Use probability gating**: `if self.rng.random() > probability: return text`
3. **Initialize ALL new counters in `__init__`**: voice_transform_count, sentence_fusion_count, transition_inject_count, clause_word_reorder_count, nominalization_count, appositive_count, discourse_rotate_count. Also initialize `self._used_appositives = set()` and `self._used_discourse_replacements = {}`.
4. **Log changes to `self.changes_log`** when modifications occur.
5. **Preserve academic tone** — output must sound natural in a scholarly paper.
6. **Match existing code style** — use `self.rng`, `re.sub()`, same indentation.
7. **Update `modify_line()`** — add calls to all 7 new methods in the correct pipeline position.

## OUTPUT:
Return the COMPLETE, FULL, UNTRUNCATED `modifier.py` with all 7 new stages. Every line. Do not summarize or abbreviate.
````

---
---

## 📁 SECTION 2 — synonyms.json (WORD SYNONYM DICTIONARY)

**File to paste first:** [synonyms.json](file:///c:/Users/PMLS/Downloads/Plagerism%20Similarity%20Remove/rules/synonyms.json)  
**Path:** `rules/synonyms.json`

> [!TIP]
> Paste the first 100 lines as a format sample — it's 2629 lines total.

**After pasting the file (or sample), send this prompt:**

````
Here is my `synonyms.json` — a word-to-synonym mapping used by "Turnitout", a tool that defeats Turnitin's plagiarism similarity AND AI detection.

# HOW THIS FILE DEFEATS TURNITIN (DEEP TECHNICAL)

## Against Similarity Detection:
Turnitin uses the **Winnowing algorithm** with **k=5 word k-grams** hashed via **Karp-Rabin rolling hash**. Any match of 8+ consecutive words is GUARANTEED to be detected. Changing even ONE word in a 5-word window produces a COMPLETELY different hash. This synonym dictionary is the #1 weapon — by swapping words throughout the text, it ensures no 5-word window survives unchanged.

## Against AI Detection:
Turnitin's AI detector measures **token probability** — AI tends to choose the HIGHEST-probability word at each position. Humans pick "suboptimal" (less predictable) words. By replacing common words with RARER academic synonyms, we INCREASE the perplexity score, making the text look MORE human.

**KEY PRINCIPLE**: The rarer the synonym, the more it defeats BOTH systems. A rare synonym:
1. Changes the hash (defeats similarity)
2. Lowers token probability (defeats AI detection — increases perplexity)

## THE FORMAT:
```json
{
  "show": ["demonstrate", "illustrate", "reveal"],
  "shows": ["demonstrates", "illustrates", "reveals"]
}
```

## YOUR TASK:

Add AT LEAST 200 NEW word entries with 3-5 synonyms each. **PRIORITIZE RARE ACADEMIC SYNONYMS** — not the obvious/common alternatives, but the less-frequently-used scholarly equivalents that send perplexity scores through the roof.

### CATEGORIES (with examples of the RARE synonyms to prefer):

**Methodology Verbs (all 4 tenses: base, -s, -ed, -ing):**
- analyze → "scrutinize", "dissect", "interrogate" (NOT just "examine")
- compute → "enumerate", "ascertain", "reckon"
- derive → "extrapolate", "educe", "elicit"
- formulate → "posit", "propound", "articulate"
- implement → "instantiate", "operationalize", "effectuate"
- integrate → "amalgamate", "synthesize", "consolidate"
- optimize → "refine", "calibrate", "fine-tune"
- simulate → "emulate", "replicate", "model"
- validate → "corroborate", "substantiate", "authenticate"
- verify → "ascertain", "confirm", "attest"
- evaluate → "appraise", "gauge", "adjudicate"
- characterize → "delineate", "elucidate", "explicate"
- Plus 15+ more verbs with rare synonyms for each

**Results/Discussion (adjectives + adverbs):**
- significant → "appreciable", "consequential", "salient", "non-trivial"
- substantial → "considerable", "pronounced", "appreciable"
- important → "consequential", "pivotal", "instrumental", "paramount"
- accurate → "veridical", "faithful", "scrupulous"
- relevant → "germane", "pertinent", "apposite", "apropos"
- Plus 20+ more

**Nouns:**
- approach → "stratagem", "modality", "paradigm", "tack"
- method → "procedure", "protocol", "technique", "regimen"
- result → "outcome", "finding", "upshot", "yield"
- problem → "quandary", "predicament", "conundrum"
- Plus 20+ more

**Connectors & Adverbs:**
- however → "nonetheless", "notwithstanding", "be that as it may"
- therefore → "ergo", "ipso facto", "accordingly"
- also → "additionally", "correspondingly", "by the same token"
- Plus 15+ more

**Quantifiers:**
- many → "myriad", "a multitude of", "copious"
- some → "a subset of", "certain", "sundry"
- few → "a paucity of", "scant", "sparse"
- Plus 10+ more

## RULES:
1. **PREFER RARE SYNONYMS over common ones** — this is critical for defeating AI detection
2. Every synonym must be academically appropriate for scholarly papers
3. Include ALL tense forms for verbs (base, -s, -ed, -ing)
4. Don't duplicate entries already in the file
5. Output as valid JSON object — NEW entries only (I will merge)

Return ONLY the new entries as a valid JSON object.
````

---
---

## 📁 SECTION 3 — phrases.json (MULTI-WORD PHRASE REWRITES)

**File to paste first:** [phrases.json](file:///c:/Users/PMLS/Downloads/Plagerism%20Similarity%20Remove/rules/phrases.json)  
**Path:** `rules/phrases.json`

> [!TIP]  
> Paste the first 50 lines as a format sample.

**After pasting the file (or sample), send this prompt:**

````
Here is my `phrases.json` — multi-word academic phrase rewrite patterns for "Turnitout", a tool that defeats Turnitin's similarity AND AI detection.

# HOW THIS FILE DEFEATS TURNITIN (DEEP TECHNICAL)

## Against Similarity Detection:
Multi-word phrases are the HIGHEST-VALUE targets. A single 4-word phrase replacement destroys 4+ k-gram hashes simultaneously (because every 5-word window containing any word from that phrase now has a different hash). A phrase rewrite is 4× more effective than a single-word synonym swap.

The Winnowing algorithm with k=5 means that replacing "this research paper" (3 words) with "the present work" (3 words) breaks:
- k-gram starting 2 words before the phrase
- k-gram starting 1 word before
- k-gram starting at the phrase
- k-gram starting 1 word into the phrase
- k-gram starting 2 words into the phrase
= **5 hashes destroyed** from ONE phrase rewrite.

## Against AI Detection:
AI-generated text relies on PREDICTABLE academic phrase patterns — "it should be noted that", "in order to", "due to the fact that" — these are exactly the high-probability phrases an AI model would produce. Replacing them with LESS COMMON equivalents dramatically increases perplexity.

## THE FORMAT:
```json
[
  ["\\bthis research paper\\b", "the present work"],
  ["\\bin this study\\b", "in this investigation"]
]
```

## YOUR TASK:

Add AT LEAST 150 NEW phrase rewrite pairs. Use `\\b` word boundaries. **PREFER LESS COMMON replacements** — phrases that increase perplexity and look more authentically human.

### CATEGORIES:

**Literature Review (25+):**
- "previous studies have shown" → "prior investigations have substantiated"
- "has been widely studied" → "has been the subject of extensive inquiry"
- "it has been reported that" → "extant literature attests that"
- "according to recent research" → "as corroborated by contemporary scholarship"
- "is well documented" → "has been amply chronicled in the literature"
- "as mentioned earlier" → "as alluded to in the preceding discussion"
- "the existing literature" → "the prevailing body of scholarship"
- etc.

**Methodology (25+):**
- "was carried out" → "was undertaken"
- "in order to" → "with the objective of"
- "by means of" → "through recourse to"
- "with respect to" → "vis-à-vis"
- "was conducted" → "was effectuated"
- "takes into account" → "gives due consideration to"
- "is based on" → "draws its foundations from"
- etc.

**Results & Findings (25+):**
- "the results indicate" → "the findings bear witness to"
- "it can be seen that" → "it becomes manifest that"
- "as shown in" → "as rendered visible in"
- "it was found that" → "it was ascertained that"
- "a significant increase" → "an appreciable escalation"
- "is proportional to" → "scales commensurately with"
- etc.

**Discussion & Analysis (25+):**
- "it is worth noting that" → "it merits underscoring that"
- "this can be attributed to" → "this may be imputed to"
- "plays a crucial role" → "occupies a pivotal station"
- "is consistent with" → "accords harmoniously with"
- "in good agreement with" → "in satisfactory concordance with"
- etc.

**Conclusion & Summary (15+):**
- "in conclusion" → "to encapsulate"
- "further research is needed" → "subsequent investigation is warranted"
- "future work should" → "prospective endeavors ought to"
- etc.

**Hedging & Qualification (15+):**
- "it appears that" → "it would seem plausible that"
- "it is possible that" → "one may reasonably conjecture that"
- "to some extent" → "to a nontrivial degree"
- etc.

**Quantification & Comparison (20+):**
- "a large number of" → "a profusion of"
- "a wide range of" → "a broad gamut of"
- "due to the fact that" → "on the grounds that"
- "as a result of" → "consequent upon"
- etc.

## RULES:
1. All patterns use `\\b` word boundaries
2. Replacements must be semantically equivalent
3. **PREFER RARE/UNUSUAL PHRASINGS** — this is critical for AI detection evasion
4. Output NEW entries ONLY as valid JSON array

Return ONLY the new entries as a valid JSON array.
````

---
---

## 📁 SECTION 4 — Small Rule Files Bundle (4 files)

**Files to paste first:**
- [hedge_words.json](file:///c:/Users/PMLS/Downloads/Plagerism%20Similarity%20Remove/rules/hedge_words.json)
- [determiners.json](file:///c:/Users/PMLS/Downloads/Plagerism%20Similarity%20Remove/rules/determiners.json)
- [conjunctions.json](file:///c:/Users/PMLS/Downloads/Plagerism%20Similarity%20Remove/rules/conjunctions.json)
- [protected_terms.json](file:///c:/Users/PMLS/Downloads/Plagerism%20Similarity%20Remove/rules/protected_terms.json)

**Paste ALL 4 files, clearly labeled, then send this prompt:**

````
Here are 4 JSON rule files from "Turnitout" — a tool that defeats Turnitin's similarity AND AI detection. I need you to extend ALL 4 files with a deep understanding of how each one attacks Turnitin's algorithm.

# HOW TURNITIN WORKS (CONTEXT FOR ALL 4 FILES)

**Similarity Detection**: Uses Winnowing algorithm with k=5 word k-grams, Karp-Rabin rolling hashes, and minimum-hash fingerprint selection. Any 8+ word chain is guaranteed caught. Changing 1 word in any 5-word window destroys the hash.

**AI Detection**: Measures (1) perplexity — how surprising word choices are, (2) burstiness — variation in sentence complexity, (3) token probability — whether "obvious" words are chosen, (4) entropy — randomness in patterns, (5) stylometric uniformity — repetitive structure.

# FILE-BY-FILE ATTACK STRATEGY:

## 1. hedge_words.json — ENTROPY INJECTORS
**Current**: 12 entries. **Target**: 50+ entries.
These words are inserted into sentences to BREAK n-gram chains and INCREASE entropy (defeating AI detection). Each hedge word injected at a natural position (after a comma) disrupts 2-3 k-gram hashes AND adds an "unexpected" token that raises perplexity.

Add RARE hedging adverbs that maximize perplexity:
"arguably", "plausibly", "ostensibly", "conceivably", "purportedly", "putatively", "presumably", "tentatively", "provisionally", "speculatively", "conjecturally", "hypothetically", "admittedly", "indisputably", "undeniably", "incontrovertibly", "unquestionably", "demonstrably", "appreciably", "discernibly", "measurably", "tangibly", "palpably", "manifestly", "conspicuously", "strikingly", "decidedly", "markedly", "emphatically", "unambiguously", "categorically", "definitively", "conclusively", "incontestably", "assuredly", "certifiably", "verifiably", "observably", "detectably"

## 2. determiners.json — HASH DESTROYERS (High-Value Targets)
**Current**: 7 entries. **Target**: 20+ entries.
Determiners appear in nearly EVERY sentence. "The" alone appears in ~7% of all English words. A single determiner swap breaks every k-gram window containing that determiner — typically 3-5 hashes per swap.

Add these with multiple alternatives each:
- "several" → ["numerous", "a number of", "multiple", "sundry"]
- "many" → ["numerous", "a considerable number of", "myriad", "copious"]
- "some" → ["certain", "particular", "select", "sundry", "assorted"]
- "few" → ["a limited number of", "a scant handful of", "sparse"]
- "most" → ["the majority of", "the preponderance of", "the greater part of"]
- "all" → ["every", "each and every", "the entirety of", "the totality of"]
- "each" → ["every", "any given", "every individual", "each respective"]
- "every" → ["each", "any given", "all", "every single"]
- "both" → ["the two", "each of the two", "the pair of"]
- "any" → ["whichever", "any given", "an arbitrary"]
- "another" → ["an additional", "a further", "one more", "a supplementary"]
- "such" → ["said", "the aforementioned", "the given", "the specified"]
- "other" → ["alternative", "additional", "further", "supplementary"]

## 3. conjunctions.json — CLAUSE REORDER TRIGGERS
**Current**: 11 entries. **Target**: 25+ entries.
These are used to identify subordinate clauses that can be MOVED to the front of sentences. Moving a clause rearranges word order → completely different hashes for every k-gram spanning the moved section.

Add: "consequently", "provided that", "given that", "assuming that", "inasmuch as", "insofar as", "notwithstanding", "on condition that", "so long as", "in the event that", "for the reason that", "on the grounds that", "in light of the fact that", "considering that", "granted that", "supposing that"

## 4. protected_terms.json — SAFETY NET
**Current**: 35 entries. **Target**: 80+ entries.
These terms are NEVER modified — they're masked before any transformation. Missing a protected term = the tool might replace a word in "Navier-Stokes" with a synonym, breaking a mathematical reference.

Add: "Navier-Stokes", "Navier--Stokes", "Boltzmann", "Maxwell", "Helmholtz", "Schrödinger", "Schrodinger", "Heisenberg", "Bernoulli", "Lagrange", "Lagrangian", "Hamiltonian", "Jacobian", "Hessian", "Wronskian", "Green's function", "Green's theorem", "Stokes' theorem", "Gauss's theorem", "Cauchy", "Riemann", "Hilbert", "Banach", "Sobolev", "Lebesgue", "Monte Carlo", "Gaussian", "Bayesian", "Boolean", "Euclidean", "Cartesian", "Fibonacci", "Hermitian", "Abelian", "Kolmogorov", "Lyapunov", "Reynolds number", "Mach number", "Prandtl number", "Nusselt number", "TensorFlow", "PyTorch", "COMSOL", "ANSYS", "OpenFOAM", "MATLAB", "Simulink"

## OUTPUT FORMAT:
Return ALL 4 complete, updated JSON files, clearly labeled:
```
=== hedge_words.json ===
[full JSON]

=== determiners.json ===
{full JSON}

=== conjunctions.json ===
[full JSON]

=== protected_terms.json ===
[full JSON]
```
Each file must contain ALL original entries PLUS all new entries.
````

---
---

## 📁 SECTION 5 — config.py (CONFIGURATION SYSTEM)

**File to paste first:** [config.py](file:///c:/Users/PMLS/Downloads/Plagerism%20Similarity%20Remove/src/turnitout/config.py)  
**Path:** `src/turnitout/config.py`

**After pasting the file, send this prompt:**

````
Here is `config.py` from "Turnitout" — a tool that defeats Turnitin's similarity AND AI detection. This file handles configuration from JSON files and environment variables.

## CONTEXT

The tool's `modifier.py` has been extended with 7 new transformation stages that target specific Turnitin algorithm vulnerabilities:
1. **Voice Transform** — active↔passive (attacks word-order hashing + stylometric uniformity)
2. **Sentence Fusion** — merges short sentences (attacks burstiness detection)
3. **Transition Injection** — inserts academic transitions (attacks entropy/perplexity detection)
4. **Word Reorder** — rearranges prepositional phrases (attacks positional k-gram hashing)
5. **Nominalization** — verb↔noun form conversion (attacks sentence structure fingerprinting)
6. **Appositive Injection** — inserts definitional clauses (attacks perplexity scoring — entropy bomb)
7. **Discourse Rotation** — rotates discourse markers (attacks AI repetition detection)

Each stage needs:
- An enable/disable toggle (boolean)
- A fire-rate control (float 0.0-1.0 — probability of the stage activating on each eligible line)

## YOUR TASK

Add per-stage configuration for all 7 new stages to BOTH `ConfigNamespace` (in `load_config_json`) and `AutoConfigNamespace` (in `auto_configure_project`).

### For `ConfigNamespace`, add:
```python
# Stage toggle — env var overrides JSON, JSON overrides default
self.ENABLE_VOICE_TRANSFORM = os.getenv("TURNITOUT_VOICE_TRANSFORM", str(d.get("enable_voice_transform", True))).lower() in ("true", "1", "yes")
self.ENABLE_SENTENCE_FUSION = os.getenv("TURNITOUT_SENTENCE_FUSION", str(d.get("enable_sentence_fusion", True))).lower() in ("true", "1", "yes")
self.ENABLE_TRANSITION_INJECT = os.getenv("TURNITOUT_TRANSITION_INJECT", str(d.get("enable_transition_inject", True))).lower() in ("true", "1", "yes")
self.ENABLE_WORD_REORDER = os.getenv("TURNITOUT_WORD_REORDER", str(d.get("enable_word_reorder", True))).lower() in ("true", "1", "yes")
self.ENABLE_NOMINALIZATION = os.getenv("TURNITOUT_NOMINALIZATION", str(d.get("enable_nominalization", True))).lower() in ("true", "1", "yes")
self.ENABLE_APPOSITIVE = os.getenv("TURNITOUT_APPOSITIVE", str(d.get("enable_appositive", True))).lower() in ("true", "1", "yes")
self.ENABLE_DISCOURSE_ROTATE = os.getenv("TURNITOUT_DISCOURSE_ROTATE", str(d.get("enable_discourse_rotate", True))).lower() in ("true", "1", "yes")

# Per-stage fire rates
self.VOICE_TRANSFORM_RATE = float(os.getenv("TURNITOUT_VOICE_RATE", d.get("voice_transform_rate", 0.30)))
self.SENTENCE_FUSION_RATE = float(os.getenv("TURNITOUT_FUSION_RATE", d.get("sentence_fusion_rate", 0.25)))
self.TRANSITION_INJECT_RATE = float(os.getenv("TURNITOUT_TRANSITION_RATE", d.get("transition_inject_rate", 0.25)))
self.WORD_REORDER_RATE = float(os.getenv("TURNITOUT_REORDER_RATE", d.get("word_reorder_rate", 0.20)))
self.NOMINALIZATION_RATE = float(os.getenv("TURNITOUT_NOMINAL_RATE", d.get("nominalization_rate", 0.20)))
self.APPOSITIVE_RATE = float(os.getenv("TURNITOUT_APPOSITIVE_RATE", d.get("appositive_rate", 0.35)))
self.DISCOURSE_ROTATE_RATE = float(os.getenv("TURNITOUT_DISCOURSE_RATE", d.get("discourse_rotate_rate", 0.50)))
```

### For `AutoConfigNamespace`, add the same fields with defaults only (no JSON source):
```python
self.ENABLE_VOICE_TRANSFORM = os.getenv("TURNITOUT_VOICE_TRANSFORM", "true").lower() in ("true", "1", "yes")
# ... etc for all toggles and rates
```

### DON'T CHANGE existing functionality — only ADD.

Return the COMPLETE, FULL modified `config.py`. Do not truncate.
````

---
---

## 📁 SECTION 6 — cli.py (COMMAND-LINE INTERFACE)

**File to paste first:** [cli.py](file:///c:/Users/PMLS/Downloads/Plagerism%20Similarity%20Remove/src/turnitout/cli.py)  
**Path:** `src/turnitout/cli.py`

**After pasting the file, send this prompt:**

````
Here is `cli.py` from "Turnitout" — a tool that defeats Turnitin's similarity AND AI detection. This is the main CLI orchestrator.

## CONTEXT

The tool now has 7 new transformation stages in `modifier.py`, each with counters:
- voice_transform_count, sentence_fusion_count, transition_inject_count
- clause_word_reorder_count, nominalization_count, appositive_count, discourse_rotate_count

The `config.py` now has toggle/rate settings for each stage.

## YOUR TASK

### 1. ADD NEW CLI FLAGS:
```python
parser.add_argument("--dry-run", action="store_true",
    help="Preview changes without writing output files")
parser.add_argument("--verbose", action="store_true",
    help="Print detailed per-line modification logs during processing")
parser.add_argument("--disable-stages", type=str, default="",
    help="Comma-separated stages to disable: voice,fusion,transition,reorder,nominal,appositive,discourse")
parser.add_argument("--max-aggressiveness", action="store_true",
    help="Override all fire rates to maximum (0.95) for maximum similarity reduction")
```

### 2. HANDLE `--disable-stages`:
```python
if args.disable_stages:
    stage_map = {
        "voice": "ENABLE_VOICE_TRANSFORM",
        "fusion": "ENABLE_SENTENCE_FUSION",
        "transition": "ENABLE_TRANSITION_INJECT",
        "reorder": "ENABLE_WORD_REORDER",
        "nominal": "ENABLE_NOMINALIZATION",
        "appositive": "ENABLE_APPOSITIVE",
        "discourse": "ENABLE_DISCOURSE_ROTATE",
    }
    for stage in args.disable_stages.split(","):
        stage = stage.strip().lower()
        if stage in stage_map:
            setattr(config, stage_map[stage], False)
            print(f"  [Disabled] {stage} transformation stage")
```

### 3. HANDLE `--max-aggressiveness`:
```python
if args.max_aggressiveness:
    config.SYNONYM_AGGRESSIVENESS = 0.95
    config.VOICE_TRANSFORM_RATE = 0.90
    config.SENTENCE_FUSION_RATE = 0.80
    config.TRANSITION_INJECT_RATE = 0.80
    config.WORD_REORDER_RATE = 0.75
    config.NOMINALIZATION_RATE = 0.70
    config.APPOSITIVE_RATE = 0.85
    config.DISCOURSE_ROTATE_RATE = 0.95
    print("  [MAX AGGRESSIVENESS] All fire rates set to maximum")
```

### 4. UPDATE STATISTICS — Add new counters to both the [4/7] section and the SUMMARY:
```python
# In [4/7] section:
print(f"  Voice transforms:      {modifier.voice_transform_count}")
print(f"  Sentence fusions:      {modifier.sentence_fusion_count}")
print(f"  Transition injections: {modifier.transition_inject_count}")
print(f"  Clause word reorders:  {modifier.clause_word_reorder_count}")
print(f"  Nominalizations:       {modifier.nominalization_count}")
print(f"  Appositive injections: {modifier.appositive_count}")
print(f"  Discourse rotations:   {modifier.discourse_rotate_count}")
```

### 5. UPDATE `total_transforms` — include all new counters

### 6. `--dry-run` — Skip file writing in [6/7], print "DRY RUN — no files written" instead

### 7. `--verbose` — During [4/7], print each modification as it happens:
```python
if args.verbose and modified != line:
    print(f"    L{zone['idx']+1}: {line.strip()[:70]}...")
    print(f"       → {modified.strip()[:70]}...")
```

### DON'T CHANGE existing functionality — only ADD.

Return the COMPLETE, FULL modified `cli.py`. Do not truncate.
````

---
---

## 📁 SECTION 7 — .env (ENVIRONMENT CONFIG)

**File to paste first:** [.env](file:///c:/Users/PMLS/Downloads/Plagerism%20Similarity%20Remove/.env)  
**Path:** `.env`

**After pasting the file, send this prompt:**

````
Here is the `.env` file from "Turnitout" — a tool that defeats Turnitin's similarity AND AI detection. The tool now has 7 new transformation stages, each controllable via environment variables.

## YOUR TASK

Extend this `.env` file with FULLY DOCUMENTED configuration for all 7 new stages. Follow the EXACT same documentation style as sections 1-3 (with `========` header bars, detailed explanation, "How to adjust" guidance, and defaults).

Each new stage needs TWO variables:
1. **Enable/disable toggle** (true/false)
2. **Fire rate** (0.0 to 1.0 — probability of activating per eligible line)

### ADD THESE (with full documentation for each):

**Section 4: VOICE TRANSFORMATION**
- `TURNITOUT_VOICE_TRANSFORM=true` — enable active↔passive voice conversion
- `TURNITOUT_VOICE_RATE=0.30` — 30% of eligible sentences get voice-flipped
- Explain: Destroys word-order fingerprints in Turnitin's k-gram hashing AND breaks AI detection's stylometric uniformity

**Section 5: SENTENCE FUSION**
- `TURNITOUT_SENTENCE_FUSION=true`
- `TURNITOUT_FUSION_RATE=0.25`
- Explain: Merges short sentences to create length variation (high burstiness) that defeats AI detection

**Section 6: TRANSITION PHRASE INJECTION**
- `TURNITOUT_TRANSITION_INJECT=true`
- `TURNITOUT_TRANSITION_RATE=0.25`
- Explain: Inserts academic transitions that inject new words into k-gram chains AND increase text entropy

**Section 7: CLAUSE WORD REORDERING**
- `TURNITOUT_WORD_REORDER=true`
- `TURNITOUT_REORDER_RATE=0.20`
- Explain: Rearranges prepositional phrases — same words in different order = completely different hashes

**Section 8: NOMINALIZATION**
- `TURNITOUT_NOMINALIZATION=true`
- `TURNITOUT_NOMINAL_RATE=0.20`
- Explain: Converts between verb and noun forms, completely restructuring sentence syntax

**Section 9: APPOSITIVE INJECTION**
- `TURNITOUT_APPOSITIVE=true`
- `TURNITOUT_APPOSITIVE_RATE=0.35`
- Explain: Injects definitional clauses that are "entropy bombs" — massively increase perplexity score

**Section 10: DISCOURSE MARKER ROTATION**
- `TURNITOUT_DISCOURSE_ROTATE=true`
- `TURNITOUT_DISCOURSE_RATE=0.50`
- Explain: Rotates discourse markers to prevent the repetitive patterns AI detection looks for

Return the COMPLETE, FULL updated `.env` file with all sections documented.
````

---
---

## ✅ Execution Checklist

| Step | File(s) | What It Attacks | Status |
|------|---------|----------------|--------|
| 1 | `modifier.py` | All Turnitin systems (7 new stages) | ⬜ |
| 2 | `synonyms.json` | k-gram hashes + token probability | ⬜ |
| 3 | `phrases.json` | Multi-hash destruction + perplexity | ⬜ |
| 4 | 4 small JSONs | Entropy + hash destruction + safety | ⬜ |
| 5 | `config.py` | Per-stage control infrastructure | ⬜ |
| 6 | `cli.py` | CLI flags + max-aggressiveness mode | ⬜ |
| 7 | `.env` | Documented environment controls | ⬜ |

> [!CAUTION]  
> After extending ALL files, **test**: `python run.py` — verify no crashes, check change report, compile LaTeX output.
