import re
from turnitout.core.transformers.base import BaseTransformer
from turnitout.core.rules import (
    ACADEMIC_SYNONYMS, PHRASE_REWRITES, HEDGE_WORDS, DETERMINER_MAP, CONTRACTIONS
)

CONTRACTION_PATTERNS = [
    (re.compile(r'\b' + re.escape(item[0]) + r'\b', re.IGNORECASE), item[1])
    for item in CONTRACTIONS
]

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


class SynonymTransformer(BaseTransformer):
    """Stage 2: Apply word-level academic synonym replacement with inflected conjugation."""
    category = "ai_evasion"

    def __init__(self, aggressiveness=0.55):
        self.aggressiveness = aggressiveness
        self.replacement_count = 0
        self._last_used_synonyms = {}

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
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
                if rng.random() < self.aggressiveness:
                    candidates = ACADEMIC_SYNONYMS[lower]
                    last_used = self._last_used_synonyms.get(lower, None)
                    filtered = [c for c in candidates if c != last_used]
                    if not filtered:
                        filtered = candidates

                    replacement = rng.choice(filtered)
                    self._last_used_synonyms[lower] = replacement

                    if token[0].isupper():
                        replacement = replacement[0].upper() + replacement[1:]
                    if token.isupper() and len(token) > 1:
                        replacement = replacement.upper()

                    modified_tokens.append(replacement)
                    self.replacement_count += 1
                    continue
            
            # 2. Inflection fallback match
            replaced = False
            if rng.random() < self.aggressiveness:
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
                        base_rep = rng.choice(filtered)
                        self._last_used_synonyms[base] = base_rep
                        
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
                        base_rep = rng.choice(filtered)
                        self._last_used_synonyms[base] = base_rep
                        
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
                        base_rep = rng.choice(filtered)
                        self._last_used_synonyms[base] = base_rep
                        
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
                        base_rep = rng.choice(filtered)
                        self._last_used_synonyms[base] = base_rep
                        
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


class DeterminerSwapTransformer(BaseTransformer):
    """Stage 4: Contextually swap determiners (e.g. 'the' <-> 'this', 'a' <-> 'another')."""
    category = "ai_evasion"

    def __init__(self):
        self.determiner_swap_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None, force_run: bool = False) -> str:
        tokens = text.split()
        modified = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            lower = token.lower().rstrip('.,;:')

            if (lower in DETERMINER_MAP
                    and i + 1 < len(tokens)
                    and '\x00' not in tokens[i + 1]
                    and len(tokens[i + 1]) >= 4
                    and tokens[i + 1][0].isalpha()
                    and (force_run or rng.random() < 0.25)):

                candidates = DETERMINER_MAP[lower]
                replacement = rng.choice(candidates)

                if token[0].isupper():
                    replacement = replacement[0].upper() + replacement[1:]

                trailing = token[len(lower):]
                modified.append(replacement + trailing)
                self.determiner_swap_count += 1
            else:
                modified.append(token)
            i += 1

        return ' '.join(modified)


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


class ContractionTransformer(BaseTransformer):
    """Stage 15: Swap formal words to contractions and vice versa ( burstiness variation)."""
    category = "ai_evasion"

    def __init__(self, contraction_rate=0.20, enable_contraction=True):
        self.contraction_rate = contraction_rate
        self.enable_contraction = enable_contraction
        self.contraction_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        if not self.enable_contraction:
            return text
        if '\x00' in text:
            return text
        if rng.random() > self.contraction_rate:
            return text

        parts = re.split(r'(\x00PH\d{4}\x00)', text)
        for i in range(len(parts)):
            if not parts[i].startswith('\x00') or not parts[i].endswith('\x00'):
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
                        break

        return ''.join(parts)
