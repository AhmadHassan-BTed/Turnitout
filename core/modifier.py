import re
import random
from core.rules import ACADEMIC_SYNONYMS, PHRASE_REWRITES, PROTECTED_TERMS

class TextModifier:
    """
    Core engine that applies synonym replacement, phrase rewriting,
    and citation insertion to prose text while protecting LaTeX elements.
    """

    def __init__(self, seed=42, aggressiveness=0.55, topic_citations=None, existing_cite_keys=None, min_sentence_length_for_cite=60):
        self.rng = random.Random(seed)
        self.aggressiveness = aggressiveness
        self.topic_citations = topic_citations or {}
        self.existing_cite_keys = existing_cite_keys or set()
        self.min_sentence_length_for_cite = min_sentence_length_for_cite
        
        self.replacement_count = 0
        self.phrase_rewrite_count = 0
        self.citation_count = 0
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

        # Step 4: Restore LaTeX elements (loop recursively to handle nesting)
        modified_line = self._restore_latex(protected_line, placeholders)

        # Step 5: Add citation if appropriate
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
