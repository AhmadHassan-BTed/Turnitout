import re
import random
from turnitout.core.rules import (
    ACADEMIC_SYNONYMS, PHRASE_REWRITES, PROTECTED_TERMS,
    HEDGE_WORDS, DETERMINER_MAP, SUBORDINATE_CONJUNCTIONS,
    PASSIVE_VERB_MAP, TRANSITION_PHRASES, VERB_NOUN_PAIRS,
    APPOSITIVE_MAP, DISCOURSE_MARKER_VARIANTS, CONTRACTIONS
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
                 max_citations_to_insert=30,
                 enable_voice_transform=True, voice_transform_rate=0.30,
                 enable_sentence_fusion=True, sentence_fusion_rate=0.25,
                 enable_transition_inject=True, transition_inject_rate=0.25,
                 enable_word_reorder=True, word_reorder_rate=0.20,
                 enable_nominalization=True, nominalization_rate=0.20,
                 enable_appositive=True, appositive_rate=0.35,
                 enable_discourse_rotate=True, discourse_rotate_rate=0.50,
                 enable_contraction=True, contraction_rate=0.20,
                 enable_ngram_audit=True, enable_risk_citation=True,
                 enable_info_reorder=True, info_reorder_rate=0.20,
                 enable_conceptual_bridge=True, conceptual_bridge_rate=0.20,
                 source_grams=None):
        self.rng = random.Random(seed)
        self.aggressiveness = aggressiveness
        self.topic_citations = topic_citations or {}
        self.existing_cite_keys = existing_cite_keys or set()
        self.min_sentence_length_for_cite = min_sentence_length_for_cite
        self.max_citations_to_insert = max_citations_to_insert
        self.source_grams = source_grams or set()
        
        # Counters for existing stages
        self.replacement_count = 0
        self.phrase_rewrite_count = 0
        self.citation_count = 0
        self.clause_reorder_count = 0
        self.determiner_swap_count = 0
        self.hedge_insertion_count = 0
        self.ngram_break_count = 0
        self.sentence_split_count = 0

        # NEW counters (stages 9-16)
        self.voice_transform_count = 0
        self.sentence_fusion_count = 0
        self.transition_inject_count = 0
        self.clause_word_reorder_count = 0
        self.nominalization_count = 0
        self.appositive_count = 0
        self.discourse_rotate_count = 0
        self.contraction_count = 0
        self.ngram_audit_count = 0
        self.risk_citation_count = 0
        self.structural_guarantee_count = 0
        self.info_reorder_count = 0
        self.conceptual_bridge_count = 0

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
        self.enable_contraction = enable_contraction
        self.contraction_rate = contraction_rate
        self.enable_ngram_audit = enable_ngram_audit
        self.enable_risk_citation = enable_risk_citation
        self.enable_info_reorder = enable_info_reorder
        self.info_reorder_rate = info_reorder_rate
        self.enable_conceptual_bridge = enable_conceptual_bridge
        self.conceptual_bridge_rate = conceptual_bridge_rate

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

        struct_changes = 0

        # Step 4: Reorder clauses (move trailing subordinate clauses to front)
        prev_text = protected_line
        protected_line = self._reorder_clauses(protected_line)
        if protected_line != prev_text:
            struct_changes += 1

        # Step 5: Swap determiners
        prev_text = protected_line
        protected_line = self._swap_determiners(protected_line)
        if protected_line != prev_text:
            struct_changes += 1

        # Step 6: Split compound sentences at conjunctions
        protected_line = self._split_compound_sentences(protected_line)

        # Step 7: Insert hedge words to break remaining n-gram chains
        protected_line = self._insert_hedge_words(protected_line)

        # Step 8: Final n-gram chain breaker (last resort for surviving chains)
        protected_line = self._break_ngram_chains(protected_line)

        # Step 9: Active/passive voice rotation
        prev_text = protected_line
        protected_line = self._transform_voice(protected_line)
        if protected_line != prev_text:
            struct_changes += 1

        # Step 10: Sentence fusion
        protected_line = self._fuse_sentences(protected_line, context_lines)

        # Step 11: Transition phrase injection
        protected_line = self._inject_transitions(protected_line)

        # Step 12: Clause-level prepositional reordering
        prev_text = protected_line
        protected_line = self._reorder_within_clause(protected_line)
        if protected_line != prev_text:
            struct_changes += 1

        # Step 13: Nominalization / de-nominalization
        prev_text = protected_line
        protected_line = self._nominalize(protected_line)
        if protected_line != prev_text:
            struct_changes += 1

        # Step 14: Appositive injection for technical terms
        prev_text = protected_line
        protected_line = self._inject_appositives(protected_line)
        if protected_line != prev_text:
            struct_changes += 1

        # Step 15: Discourse marker rotation
        prev_text = protected_line
        protected_line = self._rotate_discourse_markers(protected_line)
        if protected_line != prev_text:
            struct_changes += 1

        # Step 15b: Paragraph-level sentence reordering
        protected_line = self._reorder_sentences(protected_line)

        # Structural Diversity Guarantee: For sentences > 60 chars, ensure at least 2 structural transformations are applied.
        if len(stripped) > 60 and struct_changes < 2:
            fallbacks = [
                ('_swap_determiners', self._swap_determiners),
                ('_transform_voice', self._transform_voice),
                ('_reorder_within_clause', self._reorder_within_clause),
                ('_nominalize', self._nominalize),
                ('_inject_appositives', self._inject_appositives),
                ('_rotate_discourse_markers', self._rotate_discourse_markers)
            ]
            self.rng.shuffle(fallbacks)
            for name, func in fallbacks:
                if struct_changes >= 2:
                    break
                prev_text = protected_line
                protected_line = func(protected_line, force=True)
                if protected_line != prev_text:
                    struct_changes += 1
                    self.structural_guarantee_count += 1

        # Step 16: Contraction conversion
        protected_line = self._rotate_contractions(protected_line)

        # Step 17: Post-Pass Source-Aware N-gram Audit
        protected_line = self._source_aware_ngram_audit(protected_line)

        # Step 17b: Conceptual bridging insertion
        protected_line = self._insert_conceptual_bridge(protected_line)

        # Step 18: Restore LaTeX elements (loop recursively to handle nesting)
        modified_line = self._restore_latex(protected_line, placeholders)

        # Step 19: Add citation if appropriate
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
        text = re.sub(r'\\[a-zA-Z]+(?:\*)?(?:\[[^\]]*\])?(?:\{[^}]*\})*', make_placeholder, text)

        return text, placeholders

    def _restore_latex(self, text, placeholders):
        last_text = None
        while last_text != text:
            last_text = text
            for key, value in placeholders.items():
                text = text.replace(key, value)
        return text

    def _apply_phrase_rewrites(self, text, line_num):
        # Split text by placeholder keys to prevent matching/modifying placeholder strings
        parts = re.split(r'(\x00PH\d{4}\x00)', text)
        for i in range(len(parts)):
            if not parts[i].startswith('\x00') or not parts[i].endswith('\x00'):
                for pattern, replacement in PHRASE_REWRITES:
                    def case_aware_replace(match):
                        original = match.group(0)
                        if original[0].isupper() and replacement[0].islower():
                            return replacement[0].upper() + replacement[1:]
                        return replacement

                    new_part = re.sub(pattern, case_aware_replace, parts[i], flags=re.IGNORECASE)
                    if new_part != parts[i]:
                        matches = len(re.findall(pattern, parts[i], flags=re.IGNORECASE))
                        self.phrase_rewrite_count += matches
                        parts[i] = new_part

        return ''.join(parts)

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
            
            # 1. Direct match
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
            
            # 2. Inflection fallback match (plural, past, present participle, adverb)
            # This makes the synonym replacement engine infinitely more robust.
            replaced = False
            if self.rng.random() < self.aggressiveness:
                # Plural/Third-person singular (-s, -es, -ies)
                if lower.endswith('s') and len(lower) > 3:
                    base = None
                    suffix = ''
                    if lower.endswith('ies'):
                        base = lower[:-3] + 'y'
                        suffix = 'ies'
                    elif lower.endswith('es') and any(lower.endswith(x) for x in ['ses', 'shes', 'ches', 'xes', 'zes']):
                        base = lower[:-2]
                        suffix = 'es'
                    else:
                        base = lower[:-1]
                        suffix = 's'
                    
                    if base in ACADEMIC_SYNONYMS:
                        candidates = ACADEMIC_SYNONYMS[base]
                        last_used = self._last_used_synonyms.get(base, None)
                        filtered = [c for c in candidates if c != last_used]
                        if not filtered: filtered = candidates
                        base_rep = self.rng.choice(filtered)
                        self._last_used_synonyms[base] = base_rep
                        
                        # Conjugate synonym to plural/s-form
                        if suffix == 'ies':
                            rep = base_rep[:-1] + 'ies' if base_rep.endswith('y') else base_rep + 's'
                        elif suffix == 'es':
                            rep = base_rep + 'es' if any(base_rep.endswith(x) for x in ['s', 'sh', 'ch', 'x', 'z']) else base_rep + 's'
                        else:
                            if base_rep.endswith('y') and not any(base_rep.endswith(x) for x in ['ay', 'ey', 'oy', 'uy']):
                                rep = base_rep[:-1] + 'ies'
                            elif any(base_rep.endswith(x) for x in ['s', 'sh', 'ch', 'x', 'z']):
                                rep = base_rep + 'es'
                            else:
                                rep = base_rep + 's'
                        
                        if token[0].isupper(): rep = rep[0].upper() + rep[1:]
                        if token.isupper() and len(token) > 1: rep = rep.upper()
                        modified_tokens.append(rep)
                        self.replacement_count += 1
                        replaced = True
                        
                # Past tense/participle (-ed, -ied, -d)
                elif not replaced and lower.endswith('ed') and len(lower) > 4:
                    base = None
                    suffix = ''
                    if lower.endswith('ied'):
                        base = lower[:-3] + 'y'
                        suffix = 'ied'
                    elif lower.endswith('ed'):
                        if (lower[:-1]) in ACADEMIC_SYNONYMS:
                            base = lower[:-1]
                            suffix = 'd'
                        else:
                            base = lower[:-2]
                            suffix = 'ed'
                    
                    if base in ACADEMIC_SYNONYMS:
                        candidates = ACADEMIC_SYNONYMS[base]
                        last_used = self._last_used_synonyms.get(base, None)
                        filtered = [c for c in candidates if c != last_used]
                        if not filtered: filtered = candidates
                        base_rep = self.rng.choice(filtered)
                        self._last_used_synonyms[base] = base_rep
                        
                        # Conjugate synonym to past form
                        if suffix == 'ied':
                            rep = base_rep[:-1] + 'ied' if base_rep.endswith('y') else base_rep + 'ed'
                        elif suffix == 'd':
                            rep = base_rep + 'd' if base_rep.endswith('e') else base_rep + 'ed'
                        else:
                            if base_rep.endswith('y') and not any(base_rep.endswith(x) for x in ['ay', 'ey', 'oy', 'uy']):
                                rep = base_rep[:-1] + 'ied'
                            elif base_rep.endswith('e'):
                                rep = base_rep + 'd'
                            else:
                                rep = base_rep + 'ed'
                                
                        if token[0].isupper(): rep = rep[0].upper() + rep[1:]
                        if token.isupper() and len(token) > 1: rep = rep.upper()
                        modified_tokens.append(rep)
                        self.replacement_count += 1
                        replaced = True
                        
                # Present participle/gerund (-ing)
                elif not replaced and lower.endswith('ing') and len(lower) > 5:
                    base = None
                    suffix = ''
                    if (lower[:-3]) in ACADEMIC_SYNONYMS:
                        base = lower[:-3]
                        suffix = 'ing'
                    elif (lower[:-3] + 'e') in ACADEMIC_SYNONYMS:
                        base = lower[:-3] + 'e'
                        suffix = 'eing'
                    
                    if base in ACADEMIC_SYNONYMS:
                        candidates = ACADEMIC_SYNONYMS[base]
                        last_used = self._last_used_synonyms.get(base, None)
                        filtered = [c for c in candidates if c != last_used]
                        if not filtered: filtered = candidates
                        base_rep = self.rng.choice(filtered)
                        self._last_used_synonyms[base] = base_rep
                        
                        # Conjugate synonym to ing form
                        if base_rep.endswith('e') and not base_rep.endswith('ee'):
                            rep = base_rep[:-1] + 'ing'
                        else:
                            rep = base_rep + 'ing'
                            
                        if token[0].isupper(): rep = rep[0].upper() + rep[1:]
                        if token.isupper() and len(token) > 1: rep = rep.upper()
                        modified_tokens.append(rep)
                        self.replacement_count += 1
                        replaced = True
                        
                # Adverb (-ly, -ily)
                elif not replaced and lower.endswith('ly') and len(lower) > 4:
                    base = None
                    suffix = ''
                    if lower.endswith('ily'):
                        base = lower[:-3] + 'y'
                        suffix = 'ily'
                    else:
                        base = lower[:-2]
                        suffix = 'ly'
                        
                    if base in ACADEMIC_SYNONYMS:
                        candidates = ACADEMIC_SYNONYMS[base]
                        last_used = self._last_used_synonyms.get(base, None)
                        filtered = [c for c in candidates if c != last_used]
                        if not filtered: filtered = candidates
                        base_rep = self.rng.choice(filtered)
                        self._last_used_synonyms[base] = base_rep
                        
                        # Conjugate synonym to adverb form
                        if suffix == 'ily':
                            rep = base_rep[:-1] + 'ily' if base_rep.endswith('y') else base_rep + 'ly'
                        else:
                            if base_rep.endswith('y') and not any(base_rep.endswith(x) for x in ['ay', 'ey', 'oy', 'uy']):
                                rep = base_rep[:-1] + 'ily'
                            else:
                                rep = base_rep + 'ly'
                                
                        if token[0].isupper(): rep = rep[0].upper() + rep[1:]
                        if token.isupper() and len(token) > 1: rep = rep.upper()
                        modified_tokens.append(rep)
                        self.replacement_count += 1
                        replaced = True

            if not replaced:
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

    def _swap_determiners(self, text, force=False):
        """
        Contextually swap determiners (e.g. 'the' <-> 'this', 'a' <-> 'another').
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
                    and (force or self.rng.random() < 0.25)):

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
    def _transform_voice(self, text, force=False):
        """Alternate active/passive constructions to prevent voice monotony.
        """
        if not self.enable_voice_transform:
            return text
        if '\x00' in text or len(text.strip()) < 60:
            return text
        if not force and self.rng.random() > self.voice_transform_rate:
            return text

        # Helper to get the correct past participle form of any verb
        def _get_past_participle(verb):
            vl = verb.lower()
            if vl in PASSIVE_VERB_MAP:
                return PASSIVE_VERB_MAP[vl]
            if vl.endswith('ed'):
                return vl
            if vl.endswith('es'):
                base = vl[:-2]
                if base in PASSIVE_VERB_MAP:
                    return PASSIVE_VERB_MAP[base]
                if base.endswith('e'):
                    return base + 'd'
                return base + 'ed'
            if vl.endswith('s'):
                base = vl[:-1]
                if base in PASSIVE_VERB_MAP:
                    return PASSIVE_VERB_MAP[base]
                if base.endswith('e'):
                    return base + 'd'
                return base + 'ed'
            if vl.endswith('e'):
                return vl + 'd'
            return vl + 'ed'

        # ── Active → Passive ──────────────────────────────────────────
        pattern_a = re.compile(
            r'\b(We|The authors|Researchers|Scientists|Investigators|The study|The paper|This work|This research|The investigation|The analysis)\s+(?:then\s+|also\s+|here\s+|thus\s+|now\s+|further\s+|subsequently\s+)?(\w+)\s+the\s+(.+?)([.,]|$)',
            re.IGNORECASE,
        )
        pattern_b = re.compile(
            r'\b(We|The authors|Researchers|Scientists|Investigators|The study|The paper|This work|This research|The investigation|The analysis)\s+(?:then\s+|also\s+|here\s+|thus\s+|now\s+|further\s+|subsequently\s+)?(\w+)\s+a\s+(.+?)([.,]|$)',
            re.IGNORECASE,
        )

        def _active_to_passive(match, article):
            agent = match.group(1)
            verb = match.group(2)
            obj = match.group(3)
            end_punct = match.group(4)
            
            passive_form = _get_past_participle(verb)
            
            # Determine if the verb is past or present
            is_past = verb.lower().endswith('ed') or verb.lower().endswith('d') or verb.lower() in ["solved", "analyzed", "investigated", "evaluated", "derived", "computed", "simulated", "applied", "developed", "improved", "validated", "implemented", "formulated", "transformed", "determined", "measured", "observed", "optimized", "constructed"]
            is_plural = obj.strip().lower().endswith('s') or " and " in obj.lower()
            
            if is_past:
                aux = "were" if is_plural else "was"
            else:
                aux = "are" if is_plural else "is"

            if agent.lower() in ["we", "the authors"]:
                return f"{article.capitalize()} {obj} {aux} {passive_form}{end_punct}"
            else:
                prep = "in" if agent.lower() in ["the study", "the paper", "this work", "this research", "the investigation", "the analysis"] else "by"
                return f"{article.capitalize()} {obj} {aux} {passive_form} {prep} {agent.lower()}{end_punct}"

        for pat, art in [(pattern_a, 'the'), (pattern_b, 'a')]:
            m = pat.search(text)
            if m:
                new_text = pat.sub(lambda mo, a=art: _active_to_passive(mo, a), text, count=1)
                if new_text != text:
                    self.voice_transform_count += 1
                    return new_text

        # ── Pattern C: "Scientists have demonstrated that..." ─────────
        pattern_c = re.compile(
            r'\b(We|The authors|Researchers|Scientists|Investigators)\s+(?:have\s+|has\s+|had\s+)?(\w+)\s+that\s+(.+?)([.,]|$)',
            re.IGNORECASE,
        )
        m = pattern_c.search(text)
        if m:
            agent = m.group(1)
            verb = m.group(2)
            clause = m.group(3)
            end_punct = m.group(4)
            
            passive_form = _get_past_participle(verb)

            if agent.lower() in ["we", "the authors"]:
                new_text = pattern_c.sub(f"It has been {passive_form} that {clause}{end_punct}", text, count=1)
            else:
                new_text = pattern_c.sub(f"It has been {passive_form} by {agent.lower()} that {clause}{end_punct}", text, count=1)
            
            if new_text != text:
                self.voice_transform_count += 1
                return new_text

        # ── Passive → Active ──────────────────────────────────────────
        passive_pat = re.compile(
            r'\b(The|A)\s+(.+?)\s+(was|were)\s+(\w+(?:ed|en)?)\s+by\s+'
            r'(we|the authors|researchers|scientists|investigators)([.,]|$)',
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
    def _reorder_within_clause(self, text, force=False):
        """Shift prepositional/adverbial phrases to vary sentence openings.
        """
        if not self.enable_word_reorder:
            return text
        if '\x00' in text or len(text.strip()) < 80:
            return text
        if not force and self.rng.random() > self.word_reorder_rate:
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
            
            # Check if main clause starts with subject + verb to inject modifier in middle
            mid_match = re.match(
                r'\b(We|The authors|Researchers|Scientists|Investigators)\s+(\w+)\s+(the|a|an)\s+(.+)',
                main,
                re.IGNORECASE
            )
            if mid_match:
                subj = mid_match.group(1)
                verb = mid_match.group(2)
                art = mid_match.group(3)
                rest = mid_match.group(4)
                result = f"{subj} {verb}, {prep.lower()} {modifier}, {art} {rest}"
            else:
                # Fallback: append at the end
                if prep.lower() in ["using", "by", "with", "through", "for"]:
                    result = f"{main} {prep.lower()} {modifier}"
                else:
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
    def _nominalize(self, text, force=False):
        """Alternate verbal and nominal forms to modulate stylistic register.
        """
        if not self.enable_nominalization:
            return text
        if '\x00' in text or len(text.strip()) < 70:
            return text
        if not force and self.rng.random() > self.nominalization_rate:
            return text

        stripped = text.strip()
        indent = text[:len(text) - len(stripped)]

        for verb, noun in VERB_NOUN_PAIRS.items():
            if verb.endswith('e'):
                verb_pattern = re.escape(verb) + r'(?:d|s|ing)?'
            else:
                verb_pattern = re.escape(verb) + r'(?:ed|s|ing)?'
                
            pat = re.compile(
                r'\b(We|The authors|Researchers|Scientists|Investigators)\s+(?:then\s+|also\s+|here\s+|thus\s+|now\s+|further\s+|subsequently\s+)?'
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
                    f"{article} {noun} of the {obj} was conducted{end_punct}",
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
                if verb.endswith('e'):
                    gerund = verb[:-1] + 'ing'
                else:
                    gerund = verb + 'ing'
                gerund_capitalized = gerund.capitalize()
                new_text = pat.sub(
                    f"{gerund_capitalized} the {obj}{end_punct}",
                    text, count=1,
                )
                if new_text != text:
                    self.nominalization_count += 1
                    return new_text

        return text

    # ==================================================================
    # NEW STAGE 14: Appositive Injection
    # ==================================================================
    def _inject_appositives(self, text, force=False):
        """Insert brief parenthetical definitions after technical terms.
        """
        if not self.enable_appositive:
            return text
        if '\x00' in text:
            return text
        if not force and self.rng.random() > self.appositive_rate:
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
    def _rotate_discourse_markers(self, text, force=False):
        """Replace overused linking words with varied equivalents.
        """
        if not self.enable_discourse_rotate:
            return text
        if '\x00' in text:
            return text
        if not force and self.rng.random() > self.discourse_rotate_rate:
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
        if self.citation_count >= self.max_citations_to_insert:
            return line
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

        # Risk-Driven Citation Shielding: Place citation at the boundary of a matching 5-gram
        if self.enable_risk_citation and self.source_grams:
            parts = re.split(r'(\s+)', line)
            word_indices = [i for i, part in enumerate(parts) if part.strip() and not part.startswith('\x00')]
            k = 5
            for idx in range(len(word_indices) - k + 1):
                window_parts = [parts[word_indices[idx + j]] for j in range(k)]
                cleaned_window = [re.sub(r'[^a-zA-Z]', '', w).lower() for w in window_parts]
                if all(cleaned_window) and tuple(cleaned_window) in self.source_grams:
                    # Found matching 5-gram! Inject citation right after the second word of the matching sequence.
                    w_idx = word_indices[idx + 1] # Index of second word
                    parts[w_idx] = parts[w_idx] + '\\cite{' + cite_key + '}'
                    self.risk_citation_count += 1
                    self.citation_count += 1
                    self.used_cite_keys.add(cite_key)
                    return ''.join(parts)

        insertion = ' \\cite{' + cite_key + '}'
        period_match = re.search(r'\.\s*$', stripped)
        if period_match:
            insert_pos = line.rstrip().rfind('.')
            if insert_pos > 0:
                modified = line[:insert_pos] + insertion + line[insert_pos:]
                self.citation_count += 1
                self.used_cite_keys.add(cite_key)
                return modified
        if len(stripped) >= self.min_sentence_length_for_cite and not stripped.endswith((',', ':', '\\\\', '{', '%')):
            modified = line.rstrip() + insertion
            self.citation_count += 1
            self.used_cite_keys.add(cite_key)
            return modified
        return line

    FILLER_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'by', 'for', 'from', 'in', 'into', 'of', 'off', 'on', 'onto', 'out', 'over', 'to', 'up', 'with', 'under', 'above', 'below', 'between', 'among',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'can', 'could', 'should', 'would', 'will', 'shall', 'may', 'might', 'must',
        'i', 'me', 'my', 'myself', 'we', 'us', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'this', 'that', 'these', 'those', 'such', 'what', 'which', 'who', 'whom', 'whose', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'now', 'also', 'here',
        'we', 'our', 'show', 'paper', 'chapter', 'section', 'thesis', 'study', 'results', 'equations', 'equation', 'method', 'methods', 'solutions', 'solution', 'using', 'used', 'obtain', 'pde', 'pdes', 'ode', 'odes', 'specifically', 'notably', 'clearly', 'indeed', 'essentially'
    }

    def _extract_sentence_keywords(self, sentence):
        cleaned = re.sub(r'\\[a-zA-Z]+(?:\*)?(?:\[[^\]]*\])?(?:\{[^}]*\})*', ' ', sentence)
        cleaned = re.sub(r'\$[^\$]+\$', ' ', cleaned)
        cleaned = re.sub(r'[^a-zA-Z\s]', ' ', cleaned)
        words = [w.lower() for w in cleaned.split() if len(w) > 0]
        
        if not words:
            return None
            
        # 3-gram candidates
        for i in range(len(words) - 2):
            phrase = (words[i], words[i+1], words[i+2])
            if all(w not in self.FILLER_WORDS for w in (phrase[0], phrase[-1])) and all(len(w) > 2 for w in phrase):
                return " ".join(phrase)
                
        # 2-gram candidates
        for i in range(len(words) - 1):
            phrase = (words[i], words[i+1])
            if all(w not in self.FILLER_WORDS for w in (phrase[0], phrase[-1])) and all(len(w) > 2 for w in phrase):
                return " ".join(phrase)
                
        # 1-word candidates
        candidates = [w for w in words if w not in self.FILLER_WORDS and len(w) > 4]
        if candidates:
            return max(candidates, key=len)
            
        return None

    def _determine_topic_citation(self, line):
        lower = line.lower()
        # 1. Try matching existing topic citations first
        for keywords_tuple, cite_info in self.topic_citations.items():
            for keyword in keywords_tuple:
                if keyword.lower() in lower:
                    return cite_info["key"]
                    
        # 2. Dynamically extract keyword/phrase from the sentence
        phrase = self._extract_sentence_keywords(line)
        if phrase:
            key_suffix = phrase.replace(" ", "_")
            key = f"ref_{key_suffix}"
            topic = phrase.title() + " and Related Research"
            keywords_tuple = tuple(phrase.split())
            
            # Register in topic_citations if not already present
            if keywords_tuple not in self.topic_citations:
                self.topic_citations[keywords_tuple] = {
                    "key": key,
                    "topic": topic
                }
            return key
            
        # 3. Fallback generic key if no keywords were found
        fallback_key = "ref_numerical_study"
        fallback_tuple = ("numerical", "study")
        if fallback_tuple not in self.topic_citations:
            self.topic_citations[fallback_tuple] = {
                "key": fallback_key,
                "topic": "Numerical Investigation and Analysis"
            }
        return fallback_key

    # ==================================================================
    # NEW STAGE 16: Contraction Converter
    # ==================================================================
    def _rotate_contractions(self, text):
        """Contextually swap formal word groups to contractions and vice-versa.
        Ensures burstiness variation for AI detectors while preserving a professional academic look.
        """
        if not self.enable_contraction:
            return text
        if '\x00' in text:
            return text
        if self.rng.random() > self.contraction_rate:
            return text

        # Split text by placeholder keys to prevent matching placeholder strings
        parts = re.split(r'(\x00PH\d{4}\x00)', text)
        for i in range(len(parts)):
            if not parts[i].startswith('\x00') or not parts[i].endswith('\x00'):
                # Process plain prose parts
                for pattern, replacement in CONTRACTION_PATTERNS:
                    def case_aware_replace(match):
                        original = match.group(0)
                        if original[0].isupper():
                            return replacement[0].upper() + replacement[1:]
                        return replacement

                    new_part = re.sub(pattern, case_aware_replace, parts[i])
                    if new_part != parts[i]:
                        self.contraction_count += 1
                        parts[i] = new_part
                        break  # Only contract/expand one pair per line to maintain academic look

        return ''.join(parts)

    def _normalize_tokens(self, text):
        # Remove placeholders
        clean = re.sub(r'\x00PH\d{4}\x00', ' ', text)
        # Remove LaTeX commands
        clean = re.sub(r'\\[a-zA-Z]+(?:\*)?(?:\[[^\]]*\])?(?:\{[^}]*\})*', ' ', clean)
        # Remove non-alpha chars, convert to lowercase
        clean = re.sub(r'[^a-zA-Z\s]', ' ', clean)
        return [w.lower() for w in clean.split() if len(w) > 0]

    def _get_kgrams(self, text, k=5):
        tokens = self._normalize_tokens(text)
        if len(tokens) < k:
            return []
        return [tuple(tokens[i:i+k]) for i in range(len(tokens) - k + 1)]

    def _get_kgrams_masked(self, text, k=5):
        parts = re.split(r'(\s+)', text)
        word_tokens = []
        for part in parts:
            if part.strip() and not part.startswith('\x00'):
                cleaned = re.sub(r'[^a-zA-Z]', '', part).lower()
                if cleaned:
                    word_tokens.append(cleaned)
        if len(word_tokens) < k:
            return []
        return [tuple(word_tokens[i:i+k]) for i in range(len(word_tokens) - k + 1)]

    def audit_document_ngrams(self, zones):
        """Document-level post-pass to scan and eliminate remaining overlapping 5-grams across line boundaries."""
        if not self.enable_ngram_audit or not self.source_grams:
            return

        # We will keep a list of all prose tokens across all prose zones
        # Each element is: (cleaned_word, zone_index, part_index)
        zone_parts = {}
        prose_tokens_map = []

        for zi, zone in enumerate(zones):
            if zone['type'] == 'PROSE':
                protected, placeholders = self._protect_latex(zone['text'])
                parts = re.split(r'(\s+)', protected)
                zone_parts[zi] = (parts, placeholders)

                for pi, part in enumerate(parts):
                    if part.strip() and not part.startswith('\x00'):
                        cleaned = re.sub(r'[^a-zA-Z]', '', part).lower()
                        if cleaned:
                            prose_tokens_map.append((cleaned, zi, pi))

        k = 5
        idx = 0
        modified_zones = set()

        while idx <= len(prose_tokens_map) - k:
            window_tokens = [prose_tokens_map[idx + j][0] for j in range(k)]
            if tuple(window_tokens) in self.source_grams:
                broken = False
                
                # Option A: Try synonym replacement
                for j in range(k):
                    cleaned, zi, pi = prose_tokens_map[idx + j]
                    parts, placeholders = zone_parts[zi]
                    w = parts[pi]
                    match = re.match(r'^([^a-zA-Z]*)([a-zA-Z]+)([^a-zA-Z]*)$', w)
                    if match:
                        prefix, word_core, suffix = match.groups()
                        lower_core = word_core.lower()
                        if lower_core in ACADEMIC_SYNONYMS:
                            candidates = ACADEMIC_SYNONYMS[lower_core]
                            replacement = self.rng.choice(candidates)
                            if word_core[0].isupper():
                                replacement = replacement.capitalize()
                            parts[pi] = prefix + replacement + suffix
                            self.ngram_audit_count += 1
                            modified_zones.add(zi)
                            broken = True
                            break

                # Option B: Insert a natural adverbial qualifier if no synonym was found
                if not broken:
                    cleaned, zi, pi = prose_tokens_map[idx + 1]
                    parts, placeholders = zone_parts[zi]
                    qualifiers = ["notably", "indeed", "essentially", "specifically", "particularly", "clearly"]
                    qualifier = self.rng.choice(qualifiers)
                    parts[pi] = parts[pi] + " " + qualifier
                    self.ngram_audit_count += 1
                    modified_zones.add(zi)
                    broken = True

                if broken:
                    prose_tokens_map = []
                    for zi, (parts, placeholders) in zone_parts.items():
                        for pi, part in enumerate(parts):
                            if part.strip() and not part.startswith('\x00'):
                                cleaned = re.sub(r'[^a-zA-Z]', '', part).lower()
                                if cleaned:
                                    prose_tokens_map.append((cleaned, zi, pi))
                    continue

            idx += 1

        # Restore LaTeX and write modified text back into the zones
        for zi in modified_zones:
            parts, placeholders = zone_parts[zi]
            restored = self._restore_latex(''.join(parts), placeholders)
            zones[zi]['text'] = restored

    def _source_aware_ngram_audit(self, text):
        """Deterministic post-pass to scan for and eliminate remaining overlapping 5-grams."""
        if not self.enable_ngram_audit or not self.source_grams:
            return text

        # Split text by whitespace to preserve spacing and formatting
        parts = re.split(r'(\s+)', text)
        # Identify word token indices (excluding spaces, punctuation-only, and LaTeX placeholders)
        word_indices = [i for i, part in enumerate(parts) if part.strip() and not part.startswith('\x00')]

        if len(word_indices) < 5:
            return text

        modified = False
        k = 5

        idx = 0
        while idx <= len(word_indices) - k:
            window_parts = [parts[word_indices[idx + j]] for j in range(k)]
            cleaned_window = [re.sub(r'[^a-zA-Z]', '', w).lower() for w in window_parts]

            # Check if we have 5 valid alphabetical words that match a source 5-gram
            if all(cleaned_window) and tuple(cleaned_window) in self.source_grams:
                broken = False
                
                # Option A: Try synonym replacement on one of the words
                for j in range(k):
                    w_idx = word_indices[idx + j]
                    w = parts[w_idx]
                    match = re.match(r'^([^a-zA-Z]*)([a-zA-Z]+)([^a-zA-Z]*)$', w)
                    if match:
                        prefix, word_core, suffix = match.groups()
                        lower_core = word_core.lower()
                        if lower_core in ACADEMIC_SYNONYMS:
                            candidates = ACADEMIC_SYNONYMS[lower_core]
                            replacement = self.rng.choice(candidates)
                            if word_core[0].isupper():
                                replacement = replacement.capitalize()
                            parts[w_idx] = prefix + replacement + suffix
                            self.ngram_audit_count += 1
                            broken = True
                            modified = True
                            break

                # Option B: Insert a natural adverbial qualifier if no synonym was found
                if not broken:
                    w_idx_1 = word_indices[idx + 1]  # after the second word
                    
                    qualifiers = ["notably", "indeed", "essentially", "specifically", "particularly", "clearly"]
                    qualifier = self.rng.choice(qualifiers)

                    parts[w_idx_1] = parts[w_idx_1] + " " + qualifier
                    self.ngram_audit_count += 1
                    broken = True
                    modified = True

                # Re-parse if broken to avoid index misalignment on updated spacing/words
                if broken:
                    text_rebuilt = ''.join(parts)
                    parts = re.split(r'(\s+)', text_rebuilt)
                    word_indices = [i for i, part in enumerate(parts) if part.strip() and not part.startswith('\x00')]
                    continue

            idx += 1

        return ''.join(parts)

    def _reorder_sentences(self, text):
        """Rotate sentence sequence inside a paragraph line if they don't have start pronouns/transition dependencies.
        """
        if not self.enable_info_reorder:
            return text
        if '\x00' in text:
            return text
        if self.rng.random() > self.info_reorder_rate:
            return text

        stripped = text.strip()
        indent = text[:len(text) - len(stripped)]

        # Split into sentences (keeping punctuation/spacing)
        sentences = re.split(r'(?<=[.!?])\s+', stripped)
        if len(sentences) < 3:
            return text

        # Check which sentences are independent (do not start with dependent words)
        dependent_starts = (
            "this", "that", "these", "those", "they", "it", "their", "he", "she", "him", "her",
            "therefore", "thus", "consequently", "however", "hence", "moreover", "furthermore",
            "meanwhile", "nevertheless", "nonetheless", "subsequently", "accordingly"
        )
        
        modified = False
        for i in range(len(sentences) - 1):
            s1 = sentences[i]
            s2 = sentences[i + 1]
            
            words_s2 = s2.split()
            first_word_s2 = words_s2[0].lower().strip('.,;:!?()[]{}') if words_s2 else ""
            if first_word_s2 and first_word_s2 not in dependent_starts:
                # Swap sentence i and sentence i+1
                sentences[i], sentences[i + 1] = s2, s1
                self.info_reorder_count += 1
                modified = True
                break
                
        if modified:
            return indent + ' '.join(sentences)
        return text

    CONCEPTUAL_BRIDGES = [
        "This approach provides a robust framework for further analysis.",
        "These aspects are crucial for establishing the validity of the model.",
        "This relation plays a key role in the subsequent computations.",
        "The underlying assumptions remain valid under standard conditions.",
        "These observations are consistent with existing theoretical benchmarks.",
        "This formulation simplifies the implementation of the numerical scheme."
    ]

    def _insert_conceptual_bridge(self, text):
        if not self.enable_conceptual_bridge:
            return text
        if '\x00' in text or len(text.strip()) < 120:
            return text
        if self.rng.random() > self.conceptual_bridge_rate:
            return text

        stripped = text.strip()
        if stripped.endswith('.'):
            bridge = self.rng.choice(self.CONCEPTUAL_BRIDGES)
            result = stripped + ' ' + bridge
            self.conceptual_bridge_count += 1
            indent = text[:len(text) - len(stripped)]
            return indent + result
        return text




CONTRACTION_PATTERNS = [
    (re.compile(r'\b' + re.escape(item[0]) + r'\b', re.IGNORECASE), item[1])
    for item in CONTRACTIONS
]
