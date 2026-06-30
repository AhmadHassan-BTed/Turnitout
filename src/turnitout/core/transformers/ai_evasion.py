import re
from turnitout.core.transformers.base import BaseTransformer
from turnitout.core.rules import (
    ACADEMIC_SYNONYMS, DETERMINER_MAP, PASSIVE_VERB_MAP, TRANSITION_PHRASES,
    VERB_NOUN_PAIRS, APPOSITIVE_MAP, DISCOURSE_MARKER_VARIANTS, CONTRACTIONS
)

CONTRACTION_PATTERNS = [
    (re.compile(r'\b' + re.escape(item[0]) + r'\b', re.IGNORECASE), item[1])
    for item in CONTRACTIONS
]

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


class VoiceTransformTransformer(BaseTransformer):
    """Stage 8: Alternate active/passive voice constructions."""
    category = "ai_evasion"

    def __init__(self, voice_transform_rate=0.30, enable_voice_transform=True):
        self.voice_transform_rate = voice_transform_rate
        self.enable_voice_transform = enable_voice_transform
        self.voice_transform_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None, force_run: bool = False) -> str:
        if not self.enable_voice_transform:
            return text
        if '\x00' in text or len(text.strip()) < 60:
            return text
        if not force_run and rng.random() > self.voice_transform_rate:
            return text

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

        # Active -> Passive
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

        # Pattern C: "Scientists have demonstrated that..."
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

        # Passive -> Active
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


class TransitionInjectTransformer(BaseTransformer):
    """Stage 10: Inject transitional logical connectors."""
    category = "ai_evasion"

    def __init__(self, transition_inject_rate=0.25, enable_transition_inject=True):
        self.transition_inject_rate = transition_inject_rate
        self.enable_transition_inject = enable_transition_inject
        self.transition_inject_count = 0
        self._last_used_transitions = []

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None) -> str:
        if not self.enable_transition_inject:
            return text
        if '\x00' in text or len(text.strip()) < 70:
            return text
        if rng.random() > self.transition_inject_rate:
            return text

        category = rng.choice(list(TRANSITION_PHRASES.keys()))
        candidates = [
            t for t in TRANSITION_PHRASES[category]
            if t not in self._last_used_transitions
        ]
        if not candidates:
            candidates = TRANSITION_PHRASES[category]
        transition = rng.choice(candidates)

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


class ClauseWordReorderTransformer(BaseTransformer):
    """Stage 11: Reorder word sequences within a clause (shifting prepositional/adverbial modifiers)."""
    category = "ai_evasion"

    def __init__(self, word_reorder_rate=0.20, enable_word_reorder=True):
        self.word_reorder_rate = word_reorder_rate
        self.enable_word_reorder = enable_word_reorder
        self.clause_word_reorder_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None, force_run: bool = False) -> str:
        if not self.enable_word_reorder:
            return text
        if '\x00' in text or len(text.strip()) < 80:
            return text
        if not force_run and rng.random() > self.word_reorder_rate:
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


class NominalizationTransformer(BaseTransformer):
    """Stage 12: Nominalize verbs or de-nominalize nouns."""
    category = "ai_evasion"

    def __init__(self, nominalization_rate=0.20, enable_nominalization=True):
        self.nominalization_rate = nominalization_rate
        self.enable_nominalization = enable_nominalization
        self.nominalization_count = 0

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None, force_run: bool = False) -> str:
        if not self.enable_nominalization:
            return text
        if '\x00' in text or len(text.strip()) < 70:
            return text
        if not force_run and rng.random() > self.nominalization_rate:
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


class AppositiveInjectTransformer(BaseTransformer):
    """Stage 13: Inject brief definitions after technical terms."""
    category = "ai_evasion"

    def __init__(self, appositive_rate=0.35, enable_appositive=True):
        self.appositive_rate = appositive_rate
        self.enable_appositive = enable_appositive
        self.appositive_count = 0
        self._used_appositives = set()

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None, force_run: bool = False) -> str:
        if not self.enable_appositive:
            return text
        if '\x00' in text:
            return text
        if not force_run and rng.random() > self.appositive_rate:
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


class DiscourseRotateTransformer(BaseTransformer):
    """Stage 14b: Replace overused discourse markers at the beginning of sentences."""
    category = "ai_evasion"

    def __init__(self, discourse_rotate_rate=0.50, enable_discourse_rotate=True):
        self.discourse_rotate_rate = discourse_rotate_rate
        self.enable_discourse_rotate = enable_discourse_rotate
        self.discourse_rotate_count = 0
        self._used_discourse_replacements = {}

    def transform(self, text: str, rng, line_num: int = 0, context_lines=None, force_run: bool = False) -> str:
        if not self.enable_discourse_rotate:
            return text
        if '\x00' in text:
            return text
        if not force_run and rng.random() > self.discourse_rotate_rate:
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

            replacement = rng.choice(available)
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
