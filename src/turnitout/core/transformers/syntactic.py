import re
from turnitout.core.transformers.base import BaseTransformer
from turnitout.core.rules import (
    PASSIVE_VERB_MAP, TRANSITION_PHRASES, VERB_NOUN_PAIRS, APPOSITIVE_MAP
)

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
