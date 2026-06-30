import re
from turnitout.core.transformers.base import BaseTransformer
from turnitout.core.rules import ACADEMIC_SYNONYMS

class BreakNgramChainTransformer(BaseTransformer):
    """Stage 7: Break surviving literal word sequences with punctuation inserts."""
    category = "similarity_evasion"

    def __init__(self):
        self.ngram_break_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        stripped = text.strip()
        if len(stripped) < 60 or '\x00' in text:
            return text

        if rng.random() > 0.15:
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
        insert = rng.choice(inserts)

        words_list = stripped.split()
        indent = text[:len(text) - len(text.lstrip())]
        result = indent + ' '.join(words_list[:break_point]) + ' ' + insert + ' ' + ' '.join(words_list[break_point:])
        self.ngram_break_count += 1
        return result


class SourceAwareNgramAuditTransformer(BaseTransformer):
    """Stage 16: Check window of tokens against source_grams and break them with synonyms or adverbials."""
    category = "similarity_evasion"

    def __init__(self, enable_ngram_audit=True, source_grams=None):
        self.enable_ngram_audit = enable_ngram_audit
        self.source_grams = source_grams or set()
        self.ngram_audit_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        if not self.enable_ngram_audit or not self.source_grams:
            return text

        parts = re.split(r'(\s+)', text)
        word_indices = [i for i, part in enumerate(parts) if part.strip() and not part.startswith('\x00')]

        if len(word_indices) < 5:
            return text

        modified = False
        k = 5
        idx = 0
        while idx <= len(word_indices) - k:
            window_parts = [parts[word_indices[idx + j]] for j in range(k)]
            cleaned_window = [re.sub(r'[^a-zA-Z]', '', w).lower() for w in window_parts]

            if all(cleaned_window) and tuple(cleaned_window) in self.source_grams:
                broken = False
                
                # Option A: Try synonym replacement
                for j in range(k):
                    w_idx = word_indices[idx + j]
                    w = parts[w_idx]
                    match = re.match(r'^([^a-zA-Z]*)([a-zA-Z]+)([^a-zA-Z]*)$', w)
                    if match:
                        prefix, word_core, suffix = match.groups()
                        lower_core = word_core.lower()
                        if lower_core in ACADEMIC_SYNONYMS:
                            candidates = ACADEMIC_SYNONYMS[lower_core]
                            replacement = rng.choice(candidates)
                            if word_core[0].isupper():
                                replacement = replacement.capitalize()
                            parts[w_idx] = prefix + replacement + suffix
                            self.ngram_audit_count += 1
                            broken = True
                            modified = True
                            break

                # Option B: Insert natural adverbial qualifier
                if not broken:
                    w_idx_1 = word_indices[idx + 1]
                    qualifiers = ["notably", "indeed", "essentially", "specifically", "particularly", "clearly"]
                    qualifier = rng.choice(qualifiers)
                    parts[w_idx_1] = parts[w_idx_1] + " " + qualifier
                    self.ngram_audit_count += 1
                    broken = True
                    modified = True

                if broken:
                    text_rebuilt = ''.join(parts)
                    parts = re.split(r'(\s+)', text_rebuilt)
                    word_indices = [i for i, part in enumerate(parts) if part.strip() and not part.startswith('\x00')]
                    continue

            idx += 1

        return ''.join(parts)


class ConceptualBridgeTransformer(BaseTransformer):
    """Stage 17: Insert general academic conceptual bridge sentences at paragraph boundaries."""
    category = "similarity_evasion"

    CONCEPTUAL_BRIDGES = [
        "This approach provides a robust framework for further analysis.",
        "These aspects are crucial for establishing the validity of the model.",
        "This relation plays a key role in the subsequent computations.",
        "The underlying assumptions remain valid under standard conditions.",
        "These observations are consistent with existing theoretical benchmarks.",
        "This formulation simplifies the implementation of the numerical scheme."
    ]

    def __init__(self, enable_conceptual_bridge=True, conceptual_bridge_rate=0.20):
        self.enable_conceptual_bridge = enable_conceptual_bridge
        self.conceptual_bridge_rate = conceptual_bridge_rate
        self.conceptual_bridge_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        if not self.enable_conceptual_bridge:
            return text
        if '\x00' in text or len(text.strip()) < 120:
            return text
        if rng.random() > self.conceptual_bridge_rate:
            return text

        stripped = text.strip()
        if stripped.endswith('.'):
            bridge = rng.choice(self.CONCEPTUAL_BRIDGES)
            result = stripped + ' ' + bridge
            self.conceptual_bridge_count += 1
            indent = text[:len(text) - len(stripped)]
            return indent + result
        return text


class CitationShieldTransformer(BaseTransformer):
    """Stage 18: Add citations at sentence end or 5-gram boundary for risk shielding."""
    category = "similarity_evasion"

    def __init__(self, enable_risk_citation=True, source_grams=None, min_sentence_length_for_cite=60,
                 max_citations_to_insert=30, topic_citations=None, filler_words=None):
        self.enable_risk_citation = enable_risk_citation
        self.source_grams = source_grams or set()
        self.min_sentence_length_for_cite = min_sentence_length_for_cite
        self.max_citations_to_insert = max_citations_to_insert
        self.topic_citations = topic_citations or {}
        self.filler_words = filler_words or set()
        self.citation_count = 0
        self.risk_citation_count = 0
        self.used_cite_keys = set()

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
            if all(w not in self.filler_words for w in (phrase[0], phrase[-1])) and all(len(w) > 2 for w in phrase):
                return " ".join(phrase)
                
        # 2-gram candidates
        for i in range(len(words) - 1):
            phrase = (words[i], words[i+1])
            if all(w not in self.filler_words for w in (phrase[0], phrase[-1])) and all(len(w) > 2 for w in phrase):
                return " ".join(phrase)
                
        # 1-word candidates
        candidates = [w for w in words if w not in self.filler_words and len(w) > 4]
        if candidates:
            return max(candidates, key=len)
            
        return None

    def _determine_topic_citation(self, line):
        lower = line.lower()
        for keywords_tuple, cite_info in self.topic_citations.items():
            for keyword in keywords_tuple:
                if keyword.lower() in lower:
                    return cite_info["key"]
                    
        phrase = self._extract_sentence_keywords(line)
        if phrase:
            key_suffix = phrase.replace(" ", "_")
            key = f"ref_{key_suffix}"
            topic = phrase.title() + " and Related Research"
            keywords_tuple = tuple(phrase.split())
            
            if keywords_tuple not in self.topic_citations:
                self.topic_citations[keywords_tuple] = {
                    "key": key,
                    "topic": topic
                }
            return key
            
        fallback_key = "ref_numerical_study"
        fallback_tuple = ("numerical", "study")
        if fallback_tuple not in self.topic_citations:
            self.topic_citations[fallback_tuple] = {
                "key": fallback_key,
                "topic": "Numerical Investigation and Analysis"
            }
        return fallback_key

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        stripped = text.strip()
        if self.citation_count >= self.max_citations_to_insert:
            return text
        if len(stripped) < self.min_sentence_length_for_cite:
            return text
        if '\\cite{' in text:
            return text
        if stripped.startswith('\\item') and len(stripped) < 80:
            return text
        if stripped.startswith(('\\noindent', '\\vspace', '\\hspace')):
            return text
        if context_lines:
            for ctx_line in context_lines:
                if '\\cite{' in ctx_line:
                    return text
                    
        cite_key = self._determine_topic_citation(text)
        if not cite_key:
            return text

        # Risk-Driven Citation Shielding
        if self.enable_risk_citation and self.source_grams:
            parts = re.split(r'(\s+)', text)
            word_indices = [i for i, part in enumerate(parts) if part.strip() and not part.startswith('\x00')]
            k = 5
            for idx in range(len(word_indices) - k + 1):
                window_parts = [parts[word_indices[idx + j]] for j in range(k)]
                cleaned_window = [re.sub(r'[^a-zA-Z]', '', w).lower() for w in window_parts]
                if all(cleaned_window) and tuple(cleaned_window) in self.source_grams:
                    w_idx = word_indices[idx + 1]
                    parts[w_idx] = parts[w_idx] + '\\cite{' + cite_key + '}'
                    self.risk_citation_count += 1
                    self.citation_count += 1
                    self.used_cite_keys.add(cite_key)
                    return ''.join(parts)

        insertion = ' \\cite{' + cite_key + '}'
        period_match = re.search(r'\.\s*$', stripped)
        if period_match:
            insert_pos = text.rstrip().rfind('.')
            if insert_pos > 0:
                modified = text[:insert_pos] + insertion + text[insert_pos:]
                self.citation_count += 1
                self.used_cite_keys.add(cite_key)
                return modified
        if len(stripped) >= self.min_sentence_length_for_cite and not stripped.endswith((',', ':', '\\\\', '{', '%')):
            modified = text.rstrip() + insertion
            self.citation_count += 1
            self.used_cite_keys.add(cite_key)
            return modified
        return text
