import re
from turnitout.core.transformers.base import BaseTransformer
from turnitout.core.rules import ACADEMIC_SYNONYMS

class BreakNgramChainTransformer(BaseTransformer):
    """Stage 7: Break surviving literal word sequences with punctuation inserts."""
    category = "similarity_evasion"

    def transform(self, text: str, context, line_num: int = 0, context_lines=None) -> str:
        stripped = text.strip()
        if len(stripped) < 60 or '\x00' in text:
            return text

        if context.rng.random() > 0.15:
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
        insert = context.rng.choice(inserts)

        words_list = stripped.split()
        indent = text[:len(text) - len(text.lstrip())]
        result = indent + ' '.join(words_list[:break_point]) + ' ' + insert + ' ' + ' '.join(words_list[break_point:])
        context.ngram_break_count += 1
        return result


class SourceAwareNgramAuditTransformer(BaseTransformer):
    """Stage 16: Check window of tokens against self.source_grams and break them with synonyms or adverbials."""
    category = "similarity_evasion"

    def transform(self, text: str, context, line_num: int = 0, context_lines=None) -> str:
        if not context.enable_ngram_audit or not context.source_grams:
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

            if all(cleaned_window) and tuple(cleaned_window) in context.source_grams:
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
                            replacement = context.rng.choice(candidates)
                            if word_core[0].isupper():
                                replacement = replacement.capitalize()
                            parts[w_idx] = prefix + replacement + suffix
                            context.ngram_audit_count += 1
                            broken = True
                            modified = True
                            break

                # Option B: Insert natural adverbial qualifier
                if not broken:
                    w_idx_1 = word_indices[idx + 1]
                    qualifiers = ["notably", "indeed", "essentially", "specifically", "particularly", "clearly"]
                    qualifier = context.rng.choice(qualifiers)
                    parts[w_idx_1] = parts[w_idx_1] + " " + qualifier
                    context.ngram_audit_count += 1
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

    def transform(self, text: str, context, line_num: int = 0, context_lines=None) -> str:
        if not context.enable_conceptual_bridge:
            return text
        if '\x00' in text or len(text.strip()) < 120:
            return text
        if context.rng.random() > context.conceptual_bridge_rate:
            return text

        stripped = text.strip()
        if stripped.endswith('.'):
            bridge = context.rng.choice(self.CONCEPTUAL_BRIDGES)
            result = stripped + ' ' + bridge
            context.conceptual_bridge_count += 1
            indent = text[:len(text) - len(stripped)]
            return indent + result
        return text


class CitationShieldTransformer(BaseTransformer):
    """Stage 18: Add citations at sentence end or 5-gram boundary for risk shielding."""
    category = "similarity_evasion"

    def transform(self, text: str, context, line_num: int = 0, context_lines=None) -> str:
        stripped = text.strip()
        if context.citation_count >= context.max_citations_to_insert:
            return text
        if len(stripped) < context.min_sentence_length_for_cite:
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
                    
        cite_key = context._determine_topic_citation(text)
        if not cite_key:
            return text

        # Risk-Driven Citation Shielding
        if context.enable_risk_citation and context.source_grams:
            parts = re.split(r'(\s+)', text)
            word_indices = [i for i, part in enumerate(parts) if part.strip() and not part.startswith('\x00')]
            k = 5
            for idx in range(len(word_indices) - k + 1):
                window_parts = [parts[word_indices[idx + j]] for j in range(k)]
                cleaned_window = [re.sub(r'[^a-zA-Z]', '', w).lower() for w in window_parts]
                if all(cleaned_window) and tuple(cleaned_window) in context.source_grams:
                    w_idx = word_indices[idx + 1]
                    parts[w_idx] = parts[w_idx] + '\\cite{' + cite_key + '}'
                    context.risk_citation_count += 1
                    context.citation_count += 1
                    context.used_cite_keys.add(cite_key)
                    return ''.join(parts)

        insertion = ' \\cite{' + cite_key + '}'
        period_match = re.search(r'\.\s*$', stripped)
        if period_match:
            insert_pos = text.rstrip().rfind('.')
            if insert_pos > 0:
                modified = text[:insert_pos] + insertion + text[insert_pos:]
                context.citation_count += 1
                context.used_cite_keys.add(cite_key)
                return modified
        if len(stripped) >= context.min_sentence_length_for_cite and not stripped.endswith((',', ':', '\\\\', '{', '%')):
            modified = text.rstrip() + insertion
            context.citation_count += 1
            context.used_cite_keys.add(cite_key)
            return modified
        return text
