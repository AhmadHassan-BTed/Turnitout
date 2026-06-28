import re
import random
from turnitout.core.rules import (
    ACADEMIC_SYNONYMS, PHRASE_REWRITES, PROTECTED_TERMS,
    HEDGE_WORDS, DETERMINER_MAP, SUBORDINATE_CONJUNCTIONS
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

    def __init__(self, seed=42, aggressiveness=0.55, topic_citations=None, existing_cite_keys=None, min_sentence_length_for_cite=60):
        self.rng = random.Random(seed)
        self.aggressiveness = aggressiveness
        self.topic_citations = topic_citations or {}
        self.existing_cite_keys = existing_cite_keys or set()
        self.min_sentence_length_for_cite = min_sentence_length_for_cite
        
        self.replacement_count = 0
        self.phrase_rewrite_count = 0
        self.citation_count = 0
        self.clause_reorder_count = 0
        self.determiner_swap_count = 0
        self.hedge_insertion_count = 0
        self.ngram_break_count = 0
        self.sentence_split_count = 0
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

        # Step 9: Restore LaTeX elements (loop recursively to handle nesting)
        modified_line = self._restore_latex(protected_line, placeholders)

        # Step 10: Add citation if appropriate
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

    # ================================================================
    # NEW TRANSFORMATION PASSES
    # ================================================================

    def _reorder_clauses(self, text):
        """
        Move trailing subordinate clauses to the front of the sentence.
        Example: 'X increases, since Y holds.' -> 'Since Y holds, X increases.'
        Only fires on sentences long enough to have meaningful clauses,
        and only when a subordinate conjunction is found after a comma.
        """
        # Skip lines with placeholders (complex LaTeX) or very short lines
        if '\x00' in text or len(text.strip()) < 80:
            return text

        # Only reorder with a probability to avoid over-transforming
        if self.rng.random() > 0.30:
            return text

        # Match: "Main clause, <conjunction> subordinate clause."
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
                # Capitalize subordinate, lowercase main
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
        if '\x00' in text:
            # Still process, but only swap determiners not adjacent to placeholders
            pass

        tokens = text.split()
        modified = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            lower = token.lower().rstrip('.,;:')

            # Check: is this a determiner followed by a plain word (not a placeholder)?
            if (lower in self.DETERMINER_MAP
                    and i + 1 < len(tokens)
                    and '\x00' not in tokens[i + 1]
                    and len(tokens[i + 1]) >= 4
                    and tokens[i + 1][0].isalpha()
                    and self.rng.random() < 0.25):

                candidates = self.DETERMINER_MAP[lower]
                replacement = self.rng.choice(candidates)

                # Preserve case
                if token[0].isupper():
                    replacement = replacement[0].upper() + replacement[1:]

                # Preserve trailing punctuation
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

        # Only split with 20% probability to avoid over-fragmentation
        if self.rng.random() > 0.20:
            return text

        # Find a conjunction preceded by a comma near the middle of the sentence
        # Pattern: "..., and ..." or "..., but ..." or "...; however, ..."
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
                # Only split if both halves would be 40+ chars
                before = stripped[:pos]
                after = stripped[match.end():]
                if len(before) >= 40 and len(after) >= 40:
                    # Ensure the second part starts with uppercase
                    if after and after[0].islower():
                        after = after[0].upper() + after[1:]
                    # Preserve leading whitespace
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

        # Only insert with 20% probability to keep text natural
        if self.rng.random() > 0.20:
            return text

        hedge = self.rng.choice(self.HEDGE_WORDS)

        # Strategy 1: Insert after an existing comma (most natural position)
        comma_positions = [m.start() for m in re.finditer(r',\s+', stripped)]
        if comma_positions:
            # Pick a comma roughly in the middle of the sentence
            mid = len(stripped) // 2
            best_pos = min(comma_positions, key=lambda p: abs(p - mid))
            match = re.search(r',\s+', stripped[best_pos:])
            if match:
                insert_at = best_pos + match.end()
                # Make sure we're not inserting before a placeholder or uppercase proper noun
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
        
        This is the LAST RESORT pass — it only fires on chains that survived
        all previous transformations.
        """
        stripped = text.strip()
        if len(stripped) < 60 or '\x00' in text:
            return text

        # Only attempt with 15% probability per line to keep output natural
        if self.rng.random() > 0.15:
            return text

        # Extract sequences of plain words (no placeholders)
        words = stripped.split()
        plain_indices = []
        for i, w in enumerate(words):
            # A "plain" word is one that's all alphabetic, 3+ chars, not a placeholder
            cleaned = w.strip('.,;:!?()')
            if cleaned.isalpha() and len(cleaned) >= 3 and '\x00' not in w:
                plain_indices.append(i)

        # Find runs of 5+ consecutive plain-word indices
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

        # Pick the longest run and break it roughly in the middle
        longest = max(runs, key=len)
        break_point = longest[len(longest) // 2]

        # Choose a natural-sounding parenthetical insert
        inserts = [
            "(i.e.,)", "(that is,)", "(in essence,)", "(specifically,)",
        ]
        insert = self.rng.choice(inserts)

        # Reconstruct the line with the insert
        words_list = stripped.split()
        indent = text[:len(text) - len(text.lstrip())]
        result = indent + ' '.join(words_list[:break_point]) + ' ' + insert + ' ' + ' '.join(words_list[break_point:])
        self.ngram_break_count += 1
        return result

    # ================================================================
    # CITATION INSERTION (unchanged, robust)
    # ================================================================

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

        # Check nearby lines for existing citations
        if context_lines:
            for ctx_line in context_lines:
                if '\\cite{' in ctx_line:
                    return line

        cite_key = self._determine_topic_citation(line)
        if not cite_key:
            return line

        insertion = ' \\cite{' + cite_key + '}'

        # Insert before the last period
        period_match = re.search(r'\.\s*$', stripped)
        if period_match:
            insert_pos = line.rstrip().rfind('.')
            if insert_pos > 0:
                modified = line[:insert_pos] + insertion + line[insert_pos:]
                self.citation_count += 1
                self.used_cite_keys.add(cite_key)
                return modified

        # For long lines without period, add at end
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
