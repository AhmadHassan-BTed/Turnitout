import re
from turnitout.core.transformers.base import BaseTransformer
from turnitout.core.rules import (
    PHRASE_REWRITES, SUBORDINATE_CONJUNCTIONS, HEDGE_WORDS, ACADEMIC_SYNONYMS
)

class PhraseRewriteTransformer(BaseTransformer):
    """Stage 1: Apply phrase-level rewrites."""
    category = "similarity_evasion"

    def __init__(self):
        self.phrase_rewrite_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
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


class ClauseReorderTransformer(BaseTransformer):
    """Stage 3: Move trailing subordinate clauses to the front of the sentence."""
    category = "similarity_evasion"

    def __init__(self):
        self.clause_reorder_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        if '\x00' in text or len(text.strip()) < 80:
            return text

        if rng.random() > 0.30:
            return text

        for conj in SUBORDINATE_CONJUNCTIONS:
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


class SplitCompoundTransformer(BaseTransformer):
    """Stage 5: Split long compound sentences at coordinating conjunctions."""
    category = "similarity_evasion"

    def __init__(self):
        self.sentence_split_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        stripped = text.strip()
        if len(stripped) < 120 or '\x00' in text:
            return text

        if rng.random() > 0.20:
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


class HedgeWordTransformer(BaseTransformer):
    """Stage 6: Insert a academic hedge word at natural boundaries."""
    category = "similarity_evasion"

    def __init__(self):
        self.hedge_insertion_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        stripped = text.strip()
        if len(stripped) < 80 or '\x00' in text:
            return text

        if rng.random() > 0.20:
            return text

        hedge = rng.choice(HEDGE_WORDS)

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


class SentenceFusionTransformer(BaseTransformer):
    """Stage 9: Combine two adjacent short sentences to vary sentence length."""
    category = "similarity_evasion"

    def __init__(self, sentence_fusion_rate=0.25, enable_sentence_fusion=True):
        self.sentence_fusion_rate = sentence_fusion_rate
        self.enable_sentence_fusion = enable_sentence_fusion
        self.sentence_fusion_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        if not self.enable_sentence_fusion:
            return text
        if '\x00' in text:
            return text
        if rng.random() > self.sentence_fusion_rate:
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
        connector = rng.choice(connectors)

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


class SentenceReorderTransformer(BaseTransformer):
    """Stage 14: Rotate sentence sequence inside a paragraph line if they are independent."""
    category = "similarity_evasion"

    def __init__(self, info_reorder_rate=0.20, enable_info_reorder=True):
        self.info_reorder_rate = info_reorder_rate
        self.enable_info_reorder = enable_info_reorder
        self.info_reorder_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        if not self.enable_info_reorder:
            return text
        if '\x00' in text:
            return text
        if rng.random() > self.info_reorder_rate:
            return text

        stripped = text.strip()
        indent = text[:len(text) - len(stripped)]

        sentences = re.split(r'(?<=[.!?])\s+', stripped)
        if len(sentences) < 3:
            return text

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
                sentences[i], sentences[i + 1] = s2, s1
                self.info_reorder_count += 1
                modified = True
                break
                
        if modified:
            return indent + ' '.join(sentences)
        return text


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
