import re
from turnitout.core.transformers.base import BaseTransformer
from turnitout.core.rules import (
    SUBORDINATE_CONJUNCTIONS, DISCOURSE_MARKER_VARIANTS
)

class ClauseReorderTransformer(BaseTransformer):
    """Stage 3: Move trailing subordinate clauses to the front of the sentence."""
    category = "similarity_evasion"

    def transform(self, text: str, context, line_num: int = 0, context_lines=None) -> str:
        if '\x00' in text or len(text.strip()) < 80:
            return text

        if context.rng.random() > 0.30:
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
                context.clause_reorder_count += 1
                return reordered

        return text


class SplitCompoundTransformer(BaseTransformer):
    """Stage 5: Split long compound sentences at coordinating conjunctions."""
    category = "similarity_evasion"

    def transform(self, text: str, context, line_num: int = 0, context_lines=None) -> str:
        stripped = text.strip()
        if len(stripped) < 120 or '\x00' in text:
            return text

        if context.rng.random() > 0.20:
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
                    context.sentence_split_count += 1
                    return result

        return text


class SentenceReorderTransformer(BaseTransformer):
    """Stage 14: Rotate sentence sequence inside a paragraph line if they are independent."""
    category = "similarity_evasion"

    def transform(self, text: str, context, line_num: int = 0, context_lines=None) -> str:
        if not context.enable_info_reorder:
            return text
        if '\x00' in text:
            return text
        if context.rng.random() > context.info_reorder_rate:
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
                context.info_reorder_count += 1
                modified = True
                break
                
        if modified:
            return indent + ' '.join(sentences)
        return text


class DiscourseRotateTransformer(BaseTransformer):
    """Stage 14b: Replace overused discourse markers at the beginning of sentences."""
    category = "ai_evasion"

    def transform(self, text: str, context, line_num: int = 0, context_lines=None) -> str:
        if not context.enable_discourse_rotate:
            return text
        if '\x00' in text:
            return text
        if not getattr(context, 'force_run', False) and context.rng.random() > context.discourse_rotate_rate:
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

            used = context._used_discourse_replacements.get(marker, [])
            available = [v for v in variants if v not in used]
            if not available:
                available = variants

            replacement = context.rng.choice(available)
            context._used_discourse_replacements.setdefault(marker, []).append(replacement)

            original_word = m.group(1)
            if original_word[0].isupper():
                replacement = replacement[0].upper() + replacement[1:]
            else:
                replacement = replacement[0].lower() + replacement[1:]

            separator = m.group(2)
            rest = stripped[m.end():]
            new_stripped = replacement + separator + rest
            context.discourse_rotate_count += 1
            return indent + new_stripped

        return text
