import re
import random
from turnitout.core.rules import (
    ACADEMIC_SYNONYMS, PHRASE_REWRITES, PROTECTED_TERMS,
    HEDGE_WORDS, DETERMINER_MAP, SUBORDINATE_CONJUNCTIONS,
    PASSIVE_VERB_MAP, TRANSITION_PHRASES, VERB_NOUN_PAIRS,
    APPOSITIVE_MAP, DISCOURSE_MARKER_VARIANTS
)

class TextModifier:
    """
    Core engine that applies synonym replacement, phrase rewriting,
    clause reordering, determiner swapping, hedge word insertion,
    n-gram chain breaking, and citation insertion to prose text
    while protecting LaTeX elements.
    """

    HEDGE_WORDS = HEDGE_WORDS
    DETERMINER_MAP = DETERMINER_MAP
    SUBORDINATE_CONJUNCTIONS = SUBORDINATE_CONJUNCTIONS

    def __init__(self, seed=42, aggressiveness=0.55, topic_citations=None, existing_cite_keys=None, min_sentence_length_for_cite=60,
                 enable_voice_transform=True, voice_transform_rate=0.30,
                 enable_sentence_fusion=True, sentence_fusion_rate=0.25,
                 enable_transition_inject=True, transition_inject_rate=0.25,
                 enable_word_reorder=True, word_reorder_rate=0.20,
                 enable_nominalization=True, nominalization_rate=0.20,
                 enable_appositive=True, appositive_rate=0.35,
                 enable_discourse_rotate=True, discourse_rotate_rate=0.50):
        self.rng = random.Random(seed)
        self.aggressiveness = aggressiveness
        self.topic_citations = topic_citations or {}
        self.existing_cite_keys = existing_cite_keys or set()
        self.min_sentence_length_for_cite = min_sentence_length_for_cite
        
        # Counters for existing stages
        self.replacement_count = 0
        self.phrase_rewrite_count = 0
        self.citation_count = 0
        self.clause_reorder_count = 0
        self.determiner_swap_count = 0
        self.hedge_insertion_count = 0
        self.ngram_break_count = 0
        self.sentence_split_count = 0

        # NEW counters (stages 9-15)
        self.voice_transform_count = 0
        self.sentence_fusion_count = 0
        self.transition_inject_count = 0
        self.clause_word_reorder_count = 0
        self.nominalization_count = 0
        self.appositive_count = 0
        self.discourse_rotate_count = 0

        # Configuration flags and rates
        self.enable_voice_transform = enable_voice_transform
        self.voice_transform_rate = voice_transform_rate
        self.enable_sentence_fusion = enable_sentence_fusion
        self.sentence_fusion_rate = sentence_fusion_rate
        self.enable_transition_inject = enable_transition_inject
        self.transition_inject_rate = transition_inject_rate
        self.enable_word_reorder = enable_word_reorder
        self.word_reorder_rate = word_reorder_rate
        self.enable_nominalization = enable_nominalization
        self.nominalization_rate = nominalization_rate
        self.enable_appositive = enable_appositive
        self.appositive_rate = appositive_rate
        self.enable_discourse_rotate = enable_discourse_rotate
        self.discourse_rotate_rate = discourse_rotate_rate

        # Tracking sets / dicts for new stages
        self._used_appositives = set()
        self._used_discourse_replacements = {}  # marker -> [list of already-used replacements]
        self._last_used_transitions = []         # rolling window, max 10 entries

        self.changes_log = []
        self.used_cite_keys = set()
        self._last_used_synonyms = {}

    def modify_line(self, line, line_num, context_lines=None):
        original = line
        stripped = line.strip()
        if len(stripped) < 15:
            return line

        # Step 1: Protect LaTeX elements with placeholders
        protected_line, placeholders = self._protect_latex(line)

        # Step 2: Apply phrase-level rewrites FIRST
        protected_line = self._apply_phrase_rewrites(protected_line, line_num)

        # Step 3: Apply word-level synonym replacement
        protected_line = self._apply_synonyms(protected_line, line_num)

        # Step 4: Reorder clauses (move trailing subordinate clauses to front)
        protected_line = self._reorder_clauses(protected_line)

        # Step 5: Swap determiners
        protected_line = self._swap_determiners(protected_line)

        # Step 6: Split compound sentences at conjunctions
        protected_line = self._split_compound_sentences(protected_line)

        # Step 7: Insert hedge words to break remaining n-gram chains
        protected_line = self._insert_hedge_words(protected_line)

        # Step 8: Final n-gram chain breaker (last resort for surviving chains)
        protected_line = self._break_ngram_chains(protected_line)

        # Step 9: Active/passive voice rotation
        protected_line = self._transform_voice(protected_line)

        # Step 10: Sentence fusion
        protected_line = self._fuse_sentences(protected_line, context_lines)

        # Step 11: Transition phrase injection
        protected_line = self._inject_transitions(protected_line)

        # Step 12: Clause-level prepositional reordering
        protected_line = self._reorder_within_clause(protected_line)

        # Step 13: Nominalization / de-nominalization
        protected_line = self._nominalize(protected_line)

        # Step 14: Appositive injection for technical terms
        protected_line = self._inject_appositives(protected_line)

        # Step 15: Discourse marker rotation
        protected_line = self._rotate_discourse_markers(protected_line)

        # Step 16: Restore LaTeX elements (loop recursively to handle nesting)
        modified_line = self._restore_latex(protected_line, placeholders)

        # Step 17: Add citation if appropriate
        modified_line = self._maybe_add_citation(modified_line, line_num, context_lines)

        if modified_line != original:
            self.changes_log.append({
                'line': line_num + 1,
                'before': original.strip(),
                'after': modified_line.strip(),
            })

        return modified_line

    def _protect_latex(self, text):
        placeholders = {}
        counter = [0]

        def make_placeholder(match):
            key = f"\x00PH{counter[0]:04d}\x00"
            placeholders[key] = match.group(0)
            counter[0] += 1
            return key

        # 1. Inline math $...$
        text = re.sub(r'\$[^$]+?\$', make_placeholder, text)

        # 2. Display math \[...\]
        text = re.sub(r'\\\[.*?\\\]', make_placeholder, text, flags=re.DOTALL)

        # 3. Citations \cite{...}
        text = re.sub(r'\\cite\{[^}]+\}', make_placeholder, text)

        # 4. References
        text = re.sub(r'\\(?:eq)?ref\{[^}]+\}', make_placeholder, text)
        text = re.sub(r'\\label\{[^}]+\}', make_placeholder, text)

        # 5. Protected named terms
        for term in sorted(PROTECTED_TERMS, key=len, reverse=True):
            escaped = re.escape(term)
            text = re.sub(escaped, make_placeholder, text)

        # 6. Formatting commands with content
        text = re.sub(r'\\(?:textbf|textit|emph|underline|texttt|mathbf|mathrm|textsuperscript|textsubscript)\{[^}]*\}',
                       make_placeholder, text)

        # 7. Custom macros
        text = re.sub(r'\\(?:subhead|pd|pdd|pdmix|od|odd|laplacian|grad|divop|'
                       r'temp|disp|density|specheat|thermcond|thermdiff|tension|'
                       r'wavespeed|heatflow|eqnote|Real|Nat|abs|norm|inner)\b'
                       r'(?:\{[^}]*\})*',
                       make_placeholder, text)

        # 8. Remaining backslash commands
        text = re.sub(r'\/[a-zA-Z]+(?:\*)?(?:\[[^\]]*\])?(?:\{[^}]*\})*', make_placeholder, text)

        return text, placeholders

    def _restore_latex(self, text, placeholders):
        last_text = None
        while last_text != text:
            last_text = text
            for key, value in placeholders.items():
                text = text.replace(key, value)
        return text

    def _apply_phrase_rewrites(self, text, line_num):
        for pattern, replacement in PHRASE_REWRITES:
            def case_aware_replace(match):
                original = match.group(0)
                if original[0].isupper() and replacement[0].islower():
                    return replacement[0].upper() + replacement[1:]
                return replacement

            new_text = re.sub(pattern, case_aware_replace, text, flags=re.IGNORECASE, count=1)
            if new_text != text:
                self.phrase_rewrite_count += 1
                text = new_text

        return text

    def _apply_synonyms(self, text, line_num):
        tokens = re.split(r'(\s+|[.,;:!?()\[\]{}"\'\\])', text)
        modified_tokens = []

        for token in tokens:
            if not token or not token.strip() or '\x00' in token:
                modified_tokens.append(token)
                continue

            if len(token) <= 2:
                modified_tokens.append(token)
                continue

            lower = token.lower()
            if lower in ACADEMIC_SYNONYMS:
                if self.rng.random() < self.aggressiveness:
                    candidates = ACADEMIC_SYNONYMS[lower]
                    last_used = self._last_used_synonyms.get(lower, None)
                    filtered = [c for c in candidates if c != last_used]
                    if not filtered:
                        filtered = candidates

                    replacement = self.rng.choice(filtered)
                    self._last_used_synonyms[lower] = replacement

                    if token[0].isupper():
                        replacement = replacement[0].upper() + replacement[1:]
                    if token.isupper() and len(token) > 1:
                        replacement = replacement.upper()

                    modified_tokens.append(replacement)
                    self.replacement_count += 1
                    continue

            modified_tokens.append(token)

        return ''.join(modified_tokens)

    def _reorder_clauses(self, text):
        """
        Move trailing subordinate clauses to the front of the sentence.
        Example: 'X increases, since Y holds.' -> 'Since Y holds, X increases.'
        Only fires on sentences long enough to have meaningful clauses,
        and only when a subordinate conjunction is found after a comma.
        """
        if '\x00' in text or len(text.strip()) < 80:
            return text

        if self.rng.random() > 0.30:
            return text

        for conj in self.SUBORDINATE_CONJUNCTIONS:
            pattern = re.compile(
                r'^(\s*)([A-Z][^,]+),\s+(' + re.escape(conj) + r'\s+[^.]+)\.\s*$',
                re.IGNORECASE
            )
            m = pattern.match(text)
            if m:
                indent = m.group(1)
                main_clause = m.group(2)
                sub_clause = m.group(3)
                reordered = (indent +
                             sub_clause[0].upper() + sub_clause[1:] + ', ' +
                             main_clause[0].lower() + main_clause[1:] + '.')
                self.clause_reorder_count += 1
                return reordered

        return text

    def _swap_determiners(self, text):
        """
        Contextually swap determiners like 'the' -> 'this', 'a' -> 'a given', etc.
        Only swaps determiners followed by a noun-like word (4+ chars) to avoid
        breaking phrases like 'the $x$' or 'a \\\\cite{...}'.
        Fires conservatively (25% chance per eligible determiner).
        """
        tokens = text.split()
        modified = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            lower = token.lower().rstrip('.,;:')

            if (lower in self.DETERMINER_MAP
                    and i + 1 < len(tokens)
                    and '\x00' not in tokens[i + 1]
                    and len(tokens[i + 1]) >= 4
                    and tokens[i + 1][0].isalpha()
                    and self.rng.random() < 0.25):

                candidates = self.DETERMINER_MAP[lower]
                replacement = self.rng.choice(candidates)

                if token[0].isupper():
                    replacement = replacement[0].upper() + replacement[1:]

                trailing = token[len(lower):]
                modified.append(replacement + trailing)
                self.determiner_swap_count += 1
            else:
                modified.append(token)
            i += 1

        return ' '.join(modified)

    def _split_compound_sentences(self, text):
        """
        Split long compound sentences at conjunctions like 'and', 'but', 'however'
        into two sentences. Only fires on very long sentences (120+ chars) to
        ensure both halves remain meaningful.
        """
        stripped = text.strip()
        if len(stripped) < 120 or '\x00' in text:
            return text

        if self.rng.random() > 0.20:
            return text

        split_patterns = [
            (r',\s+and\s+', '. '),
            (r',\s+but\s+', '. However, '),
            (r';\s+however,?\s+', '. However, '),
            (r',\s+whereas\s+', '. In contrast, '),
            (r',\s+while\s+', '. Meanwhile, '),
        ]

        for pattern, joiner in split_patterns:
            match = re.search(pattern, stripped, re.IGNORECASE)
            if match:
                pos = match.start()
                before = stripped[:pos]
                after = stripped[match.end():]
                if len(before) >= 40 and len(after) >= 40:
                    if after and after[0].islower():
                        after = after[0].upper() + after[1:]
                    indent = text[:len(text) - len(text.lstrip())]
                    result = indent + before + '.' + joiner.rstrip() + ' ' + after
                    self.sentence_split_count += 1
                    return result

        return text

    def _insert_hedge_words(self, text):
        """
        Insert a single academic hedge word at a natural position in the sentence
        to break potential n-gram chains. Only fires on longer sentences (80+ chars)
        and only inserts after a comma or at the start of a clause.
        """
        stripped = text.strip()
        if len(stripped) < 80 or '\x00' in text:
            return text

        if self.rng.random() > 0.20:
            return text

        hedge = self.rng.choice(self.HEDGE_WORDS)

        comma_positions = [m.start() for m in re.finditer(r',\s+', stripped)]
        if comma_positions:
            mid = len(stripped) // 2
            best_pos = min(comma_positions, key=lambda p: abs(p - mid))
            match = re.search(r',\s+', stripped[best_pos:])
            if match:
                insert_at = best_pos + match.end()
                if insert_at < len(stripped) and stripped[insert_at:insert_at + 1].islower():
                    indent = text[:len(text) - len(text.lstrip())]
                    result = indent + stripped[:insert_at] + hedge + ' ' + stripped[insert_at:]
                    self.hedge_insertion_count += 1
                    return result

        return text

    def _break_ngram_chains(self, text):
        """
        Final-pass n-gram chain breaker. Scans the text for any surviving 
        5+ word chains of plain English words (no placeholders, no LaTeX).
        If found, inserts a brief parenthetical or qualifier to break the chain.
        """
        stripped = text.strip()
        if len(stripped) < 60 or '\x00' in text:
            return text

        if self.rng.random() > 0.15:
            return text

        words = stripped.split()
        plain_indices = []
        for i, w in enumerate(words):
            cleaned = w.strip('.,;:!?()')
            if cleaned.isalpha() and len(cleaned) >= 3 and '\x00' not in w:
                plain_indices.append(i)

        if len(plain_indices) < 5:
            return text

        runs = []
        current_run = [plain_indices[0]]
        for j in range(1, len(plain_indices)):
            if plain_indices[j] == plain_indices[j - 1] + 1:
                current_run.append(plain_indices[j])
            else:
                if len(current_run) >= 5:
                    runs.append(current_run)
                current_run = [plain_indices[j]]
        if len(current_run) >= 5:
            runs.append(current_run)

        if not runs:
            return text

        longest = max(runs, key=len)
        break_point = longest[len(longest) // 2]

        inserts = [
            "(i.e.,)", "(that is,)", "(in essence,)", "(specifically,)",
        ]
        insert = self.rng.choice(inserts)

        words_list = stripped.split()
        indent = text[:len(text) - len(text.lstrip())]
        result = indent + ' '.join(words_list[:break_point]) + ' ' + insert + ' ' + ' '.join(words_list[break_point:])
        self.ngram_break_count += 1
        return result

    # ==================================================================
    # NEW STAGE 9: Active/Passive Voice Rotation
    # ==================================================================
    def _transform_voice(self, text):
        """Alternate active/passive constructions to prevent voice monotony.
        """
        if not self.enable_voice_transform:
            return text
        if '\x00' in text or len(text.strip()) < 60:
            return text
        if self.rng.random() > self.voice_transform_rate:
            return text

        # ── Active → Passive ──────────────────────────────────────────
        pattern_a = re.compile(
            r'\b(We|The authors|Researchers)\s+(?:then\s+|also\s+|here\s+|thus\s+|now\s+|further\s+|subsequently\s+)?(\w+)\s+the\s+(.+?)([.,]|$)',
            re.IGNORECASE,
        )
        pattern_b = re.compile(
            r'\b(We|The authors|Researchers)\s+(?:then\s+|also\s+|here\s+|thus\s+|now\s+|further\s+|subsequently\s+)?(\w+)\s+a\s+(.+?)([.,]|$)',
            re.IGNORECASE,
        )

        def _active_to_passive(match, article):
            agent = match.group(1)
            verb = match.group(2).lower()
            obj = match.group(3)
            end_punct = match.group(4)
            if verb in PASSIVE_VERB_MAP:
                passive_form = PASSIVE_VERB_MAP[verb]
            elif verb.endswith('e'):
                passive_form = verb + 'd'
            else:
                passive_form = verb + 'ed'
            return (
                f"{article.capitalize()} {obj} {passive_form} "
                f"by {agent.lower()}{end_punct}"
            )

        for pat, art in [(pattern_a, 'the'), (pattern_b, 'a')]:
            m = pat.search(text)
            if m:
                new_text = pat.sub(lambda mo, a=art: _active_to_passive(mo, a), text, count=1)
                if new_text != text:
                    self.voice_transform_count += 1
                    return new_text

        # ── Passive → Active ──────────────────────────────────────────
        passive_pat = re.compile(
            r'\b(The|A)\s+(.+?)\s+(was|were)\s+(\w+(?:ed|en)?)\s+by\s+'
            r'(we|the authors|researchers)([.,]|$)',
            re.IGNORECASE,
        )
        m = passive_pat.search(text)
        if m:
            article = m.group(1)
            obj = m.group(2)
            verb_past = m.group(4)
            agent = m.group(5)
            end_punct = m.group(6)
            if verb_past.endswith('ed'):
                base_verb = verb_past[:-2]
                if (
                    len(base_verb) >= 2
                    and base_verb[-1] == base_verb[-2]
                    and base_verb[-1] not in 'aeiou'
                ):
                    base_verb = base_verb[:-1]
            elif verb_past.endswith('en'):
                base_verb = verb_past[:-2]
            else:
                base_verb = verb_past

            new_text = passive_pat.sub(
                f"{agent.capitalize()} {base_verb} "
                f"{article.lower()} {obj}{end_punct}",
                text, count=1,
            )
            if new_text != text:
                self.voice_transform_count += 1
                return new_text

        return text

    # ==================================================================
    # NEW STAGE 10: Sentence Fusion
    # ==================================================================
    def _fuse_sentences(self, text, context_lines):
        """Combine two short adjacent sentences to vary rhythmic length.
        """
        if not self.enable_sentence_fusion:
            return text
        if '\x00' in text:
            return text
        if self.rng.random() > self.sentence_fusion_rate:
            return text

        current = text.strip()
        if len(current) >= 80:
            return text

        next_line = None
        if context_lines:
            for candidate in context_lines:
                candidate_stripped = candidate.strip()
                if candidate_stripped and candidate_stripped != current:
                    next_line = candidate_stripped
                    break

        if not next_line or len(next_line) >= 80:
            return text

        if next_line.startswith('\\') or '\x00' in next_line:
            return text

        connectors = [
            "which",
            "thereby",
            "consequently",
            "thus leading to",
            "and as a result",
        ]
        connector = self.rng.choice(connectors)

        if current.endswith('.'):
            fused = (
                current[:-1]
                + ', '
                + connector
                + ' '
                + next_line[0].lower()
                + next_line[1:]
            )
            indent = text[:len(text) - len(current)]
            self.sentence_fusion_count += 1
            return indent + fused

        return text

    # ==================================================================
    # NEW STAGE 11: Transition Phrase Injection
    # ==================================================================
    def _inject_transitions(self, text):
        """Enrich logical connectors to add coherence and avoid repetition.
        """
        if not self.enable_transition_inject:
            return text
        if '\x00' in text or len(text.strip()) < 70:
            return text
        if self.rng.random() > self.transition_inject_rate:
            return text

        category = self.rng.choice(list(TRANSITION_PHRASES.keys()))
        candidates = [
            t for t in TRANSITION_PHRASES[category]
            if t not in self._last_used_transitions
        ]
        if not candidates:
            candidates = TRANSITION_PHRASES[category]
        transition = self.rng.choice(candidates)

        self._last_used_transitions.append(transition)
        if len(self._last_used_transitions) > 10:
            self._last_used_transitions.pop(0)

        stripped = text.strip()
        indent = text[:len(text) - len(stripped)]

        comma_match = re.search(r',\s+', stripped)
        if comma_match and comma_match.start() > 20:
            insert_at = comma_match.end()
            if insert_at < len(stripped) and stripped[insert_at].islower():
                result = (
                    indent
                    + stripped[:insert_at]
                    + transition
                    + ' '
                    + stripped[insert_at:]
                )
                self.transition_inject_count += 1
                return result

        result = (
            indent
            + transition.capitalize()
            + ', '
            + stripped[0].lower()
            + stripped[1:]
        )
        self.transition_inject_count += 1
        return result

    # ==================================================================
    # NEW STAGE 12: Clause-Level Reordering
    # ==================================================================
    def _reorder_within_clause(self, text):
        """Shift prepositional/adverbial phrases to vary sentence openings.
        """
        if not self.enable_word_reorder:
            return text
        if '\x00' in text or len(text.strip()) < 80:
            return text
        if self.rng.random() > self.word_reorder_rate:
            return text

        stripped = text.strip()
        indent = text[:len(text) - len(stripped)]

        leading_pat = re.compile(
            r'^(In|For|Using|By|With|Through)\s+([^,]+),\s+(.+)',
            re.IGNORECASE,
        )
        m = leading_pat.match(stripped)
        if m:
            prep = m.group(1)
            modifier = m.group(2).strip()
            main = m.group(3).strip()
            if main and main[0].islower():
                main = main[0].upper() + main[1:]
            result = f"{main}, {prep.lower()} {modifier}"
            if not result.rstrip().endswith(('.', ',', ';', ':')):
                if stripped.rstrip().endswith('.'):
                    result = result.rstrip() + '.'
            self.clause_word_reorder_count += 1
            return indent + result

        end_pat = re.compile(
            r'(.+?),\s+by means of\s+(.+?)([.;,]?)$',
            re.IGNORECASE,
        )
        m = end_pat.search(stripped)
        if m:
            main = m.group(1).strip()
            means = m.group(2).strip()
            end_punct = m.group(3)
            result = f"By means of {means}, {main[0].lower()}{main[1:]}{end_punct}"
            self.clause_word_reorder_count += 1
            return indent + result

        return text

    # ==================================================================
    # NEW STAGE 13: Nominalization / De-Nominalization
    # ==================================================================
    def _nominalize(self, text):
        """Alternate verbal and nominal forms to modulate stylistic register.
        """
        if not self.enable_nominalization:
            return text
        if '\x00' in text or len(text.strip()) < 70:
            return text
        if self.rng.random() > self.nominalization_rate:
            return text

        stripped = text.strip()
        indent = text[:len(text) - len(stripped)]

        for verb, noun in VERB_NOUN_PAIRS.items():
            if verb.endswith('e'):
                verb_pattern = re.escape(verb) + r'(?:d|s|ing)?'
            else:
                verb_pattern = re.escape(verb) + r'(?:ed|s|ing)?'
                
            pat = re.compile(
                r'\b(We|The authors|Researchers)\s+(?:then\s+|also\s+|here\s+|thus\s+|now\s+|further\s+|subsequently\s+)?'
                + verb_pattern
                + r'\s+the\s+(.+?)([.,]|$)',
                re.IGNORECASE,
            )
            m = pat.search(text)
            if m:
                agent = m.group(1)
                obj = m.group(2).strip()
                end_punct = m.group(3)
                article = 'An' if noun[0] in 'aeiouAEIOU' else 'A'
                new_text = pat.sub(
                    f"{article} {noun} of the {obj} was conducted "
                    f"by {agent.lower()}{end_punct}",
                    text, count=1,
                )
                if new_text != text:
                    self.nominalization_count += 1
                    return new_text

        for verb, noun in VERB_NOUN_PAIRS.items():
            pat = re.compile(
                r'\bThe\s+' + re.escape(noun) + r'\s+of\s+the\s+(.+?)([.,]|$)',
                re.IGNORECASE,
            )
            m = pat.search(text)
            if m:
                obj = m.group(1).strip()
                end_punct = m.group(2)
                capitalized_verb = verb.capitalize()
                new_text = pat.sub(
                    f"{capitalized_verb} the {obj}{end_punct}",
                    text, count=1,
                )
                if new_text != text:
                    self.nominalization_count += 1
                    return new_text

        return text

    # ==================================================================
    # NEW STAGE 14: Appositive Injection
    # ==================================================================
    def _inject_appositives(self, text):
        """Insert brief parenthetical definitions after technical terms.
        """
        if not self.enable_appositive:
            return text
        if '\x00' in text:
            return text
        if self.rng.random() > self.appositive_rate:
            return text

        stripped = text.strip()
        indent = text[:len(text) - len(stripped)]

        for term in sorted(APPOSITIVE_MAP.keys(), key=len, reverse=True):
            appositive = APPOSITIVE_MAP[term]

            if term in self._used_appositives:
                continue

            if not re.search(r'\b' + re.escape(term) + r'\b', stripped, re.IGNORECASE):
                continue

            new_stripped = re.sub(
                r'\b(' + re.escape(term) + r')\b',
                r'\1, ' + appositive + ',',
                stripped,
                count=1,
                flags=re.IGNORECASE,
            )
            if new_stripped != stripped:
                self._used_appositives.add(term)
                self.appositive_count += 1
                return indent + new_stripped

        return text

    # ==================================================================
    # NEW STAGE 15: Discourse Marker Rotation
    # ==================================================================
    def _rotate_discourse_markers(self, text):
        """Replace overused linking words with varied equivalents.
        """
        if not self.enable_discourse_rotate:
            return text
        if '\x00' in text:
            return text
        if self.rng.random() > self.discourse_rotate_rate:
            return text

        stripped = text.strip()
        indent = text[:len(text) - len(stripped)]

        for marker, variants in DISCOURSE_MARKER_VARIANTS.items():
            pattern = re.compile(
                r'^(' + re.escape(marker) + r')(\s*[,;]\s*|\s+)',
                re.IGNORECASE,
            )
            m = pattern.match(stripped)
            if not m:
                continue

            used = self._used_discourse_replacements.get(marker, [])
            available = [v for v in variants if v not in used]
            if not available:
                available = variants

            replacement = self.rng.choice(available)
            self._used_discourse_replacements.setdefault(marker, []).append(replacement)

            original_word = m.group(1)
            if original_word[0].isupper():
                replacement = replacement[0].upper() + replacement[1:]
            else:
                replacement = replacement[0].lower() + replacement[1:]

            separator = m.group(2)
            rest = stripped[m.end():]
            new_stripped = replacement + separator + rest
            self.discourse_rotate_count += 1
            return indent + new_stripped

        return text

    # ==================================================================
    # Citation insertion (existing)
    # ==================================================================
    def _maybe_add_citation(self, line, line_num, context_lines=None):
        stripped = line.strip()
        if len(stripped) < self.min_sentence_length_for_cite:
            return line
        if '\\cite{' in line:
            return line
        if stripped.startswith('\\item') and len(stripped) < 80:
            return line
        if stripped.startswith(('\\noindent', '\\vspace', '\\hspace')):
            return line
        if context_lines:
            for ctx_line in context_lines:
                if '\\cite{' in ctx_line:
                    return line
        cite_key = self._determine_topic_citation(line)
        if not cite_key:
            return line
        insertion = ' \\cite{' + cite_key + '}'
        period_match = re.search(r'\.\s*$', stripped)
        if period_match:
            insert_pos = line.rstrip().rfind('.')
            if insert_pos > 0:
                modified = line[:insert_pos] + insertion + line[insert_pos:]
                self.citation_count += 1
                self.used_cite_keys.add(cite_key)
                return modified
        if len(stripped) > 100 and not stripped.endswith((',', ':', '\\\\', '{')):
            modified = line.rstrip() + insertion
            self.citation_count += 1
            self.used_cite_keys.add(cite_key)
            return modified
        return line

    def _determine_topic_citation(self, line):
        lower = line.lower()
        for keywords_tuple, cite_info in self.topic_citations.items():
            for keyword in keywords_tuple:
                if keyword.lower() in lower:
                    return cite_info["key"]
        return None
