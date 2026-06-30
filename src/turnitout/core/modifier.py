import re
import random
from turnitout.core.rules import PROTECTED_TERMS, ACADEMIC_SYNONYMS
from turnitout.core.transformers import get_default_pipeline

class TextModifier:
    """
    Core engine that coordinates the stylistic enhancement and document
    modification pipeline. Protects LaTeX elements, chains modular 
    transformers, guarantees structural diversity, and adds topic citations.
    """

    FILLER_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'by', 'for', 'from', 'in', 'into', 'of', 'off', 'on', 'onto', 'out', 'over', 'to', 'up', 'with', 'under', 'above', 'below', 'between', 'among',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'can', 'could', 'should', 'would', 'will', 'shall', 'may', 'might', 'must',
        'i', 'me', 'my', 'myself', 'we', 'us', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'this', 'that', 'these', 'those', 'such', 'what', 'which', 'who', 'whom', 'whose', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'now', 'also', 'here',
        'we', 'our', 'show', 'paper', 'chapter', 'section', 'thesis', 'study', 'results', 'equations', 'equation', 'method', 'methods', 'solutions', 'solution', 'using', 'used', 'obtain', 'pde', 'pdes', 'ode', 'odes', 'specifically', 'notably', 'clearly', 'indeed', 'essentially'
    }

    CONCEPTUAL_BRIDGES = [
        "This approach provides a robust framework for further analysis.",
        "These aspects are crucial for establishing the validity of the model.",
        "This relation plays a key role in the subsequent computations.",
        "The underlying assumptions remain valid under standard conditions.",
        "These observations are consistent with existing theoretical benchmarks.",
        "This formulation simplifies the implementation of the numerical scheme."
    ]

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
        
        # Telemetry counters
        self.replacement_count = 0
        self.phrase_rewrite_count = 0
        self.citation_count = 0
        self.clause_reorder_count = 0
        self.determiner_swap_count = 0
        self.hedge_insertion_count = 0
        self.ngram_break_count = 0
        self.sentence_split_count = 0
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

        # Tracking state
        self._used_appositives = set()
        self._used_discourse_replacements = {}
        self._last_used_transitions = []
        self.changes_log = []
        self.used_cite_keys = set()
        self._last_used_synonyms = {}

        # Pipeline steps
        self.pipeline = get_default_pipeline()

    def modify_line(self, line, line_num, context_lines=None):
        original = line
        stripped = line.strip()
        if len(stripped) < 15:
            return line

        # Step 1: Protect LaTeX elements with placeholders
        protected_line, placeholders = self._protect_latex(line)

        # Execute default sequential pipeline (Stages 1 - 14b)
        # Note: the pipeline has 19 steps (indexed 0 to 18)
        # We run steps 0 to 14 first
        struct_changes = 0
        
        for idx in range(15):
            tf = self.pipeline[idx]
            prev_text = protected_line
            protected_line = tf.transform(protected_line, self, line_num, context_lines)
            if idx in [2, 3, 7, 10, 11, 12, 13] and protected_line != prev_text:
                struct_changes += 1

        # Structural Diversity Guarantee: For sentences > 60 chars, ensure at least 2 structural transformations are applied.
        if len(stripped) > 60 and struct_changes < 2:
            from turnitout.core.transformers.lexical import DeterminerSwapTransformer
            from turnitout.core.transformers.syntactic import (
                VoiceTransformTransformer, ClauseWordReorderTransformer,
                NominalizationTransformer, AppositiveInjectTransformer
            )
            from turnitout.core.transformers.structural import DiscourseRotateTransformer

            fallbacks = [
                DeterminerSwapTransformer(),
                VoiceTransformTransformer(),
                ClauseWordReorderTransformer(),
                NominalizationTransformer(),
                AppositiveInjectTransformer(),
                DiscourseRotateTransformer()
            ]
            self.rng.shuffle(fallbacks)
            self.force_run = True
            try:
                for tf in fallbacks:
                    if struct_changes >= 2:
                        break
                    prev_text = protected_line
                    protected_line = tf.transform(protected_line, self, line_num, context_lines)
                    if protected_line != prev_text:
                        struct_changes += 1
                        self.structural_guarantee_count += 1
            finally:
                self.force_run = False

        # Run remaining pipeline steps (Contraction, N-gram Auditing, Conceptual Bridge)
        for idx in range(15, len(self.pipeline) - 1):
            tf = self.pipeline[idx]
            protected_line = tf.transform(protected_line, self, line_num, context_lines)

        # Restore LaTeX elements
        modified_line = self._restore_latex(protected_line, placeholders)

        # Run the final pipeline step: Citation Shielding (operates on restored LaTeX)
        citation_transformer = self.pipeline[-1]
        modified_line = citation_transformer.transform(modified_line, self, line_num, context_lines)

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
        text = re.sub(r'\\(/subhead|pd|pdd|pdmix|od|odd|laplacian|grad|divop|'
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

    def _normalize_tokens(self, text):
        clean = re.sub(r'\x00PH\d{4}\x00', ' ', text)
        clean = re.sub(r'\\[a-zA-Z]+(?:\*)?(?:\[[^\]]*\])?(?:\{[^}]*\})*', ' ', clean)
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

    def audit_document_ngrams(self, zones):
        """Document-level post-pass to scan and eliminate remaining overlapping 5-grams across line boundaries."""
        if not self.enable_ngram_audit or not self.source_grams:
            return

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

                # Option B: Insert a natural adverbial qualifier
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

        for zi in modified_zones:
            parts, placeholders = zone_parts[zi]
            restored = self._restore_latex(''.join(parts), placeholders)
            zones[zi]['text'] = restored

    # ==================================================================
    # Backward Compatibility Pass-through Wrappers for Unit Tests
    # ==================================================================
    def _reorder_clauses(self, text):
        from turnitout.core.transformers.structural import ClauseReorderTransformer
        return ClauseReorderTransformer().transform(text, self)

    def _swap_determiners(self, text):
        from turnitout.core.transformers.lexical import DeterminerSwapTransformer
        return DeterminerSwapTransformer().transform(text, self)

    def _split_compound_sentences(self, text):
        from turnitout.core.transformers.structural import SplitCompoundTransformer
        return SplitCompoundTransformer().transform(text, self)

    def _insert_hedge_words(self, text):
        from turnitout.core.transformers.lexical import HedgeWordTransformer
        return HedgeWordTransformer().transform(text, self)

    def _break_ngram_chains(self, text):
        from turnitout.core.transformers.advanced import BreakNgramChainTransformer
        return BreakNgramChainTransformer().transform(text, self)

    def _transform_voice(self, text):
        from turnitout.core.transformers.syntactic import VoiceTransformTransformer
        return VoiceTransformTransformer().transform(text, self)

    def _fuse_sentences(self, text, context_lines):
        from turnitout.core.transformers.syntactic import SentenceFusionTransformer
        return SentenceFusionTransformer().transform(text, self, context_lines=context_lines)

    def _inject_transitions(self, text):
        from turnitout.core.transformers.syntactic import TransitionInjectTransformer
        return TransitionInjectTransformer().transform(text, self)

    def _reorder_within_clause(self, text):
        from turnitout.core.transformers.syntactic import ClauseWordReorderTransformer
        return ClauseWordReorderTransformer().transform(text, self)

    def _nominalize(self, text):
        from turnitout.core.transformers.syntactic import NominalizationTransformer
        return NominalizationTransformer().transform(text, self)

    def _inject_appositives(self, text):
        from turnitout.core.transformers.syntactic import AppositiveInjectTransformer
        return AppositiveInjectTransformer().transform(text, self)

    def _rotate_discourse_markers(self, text):
        from turnitout.core.transformers.structural import DiscourseRotateTransformer
        return DiscourseRotateTransformer().transform(text, self)

    def _rotate_contractions(self, text):
        from turnitout.core.transformers.lexical import ContractionTransformer
        return ContractionTransformer().transform(text, self)

    def _source_aware_ngram_audit(self, text):
        from turnitout.core.transformers.advanced import SourceAwareNgramAuditTransformer
        return SourceAwareNgramAuditTransformer().transform(text, self)

    def _reorder_sentences(self, text):
        from turnitout.core.transformers.structural import SentenceReorderTransformer
        return SentenceReorderTransformer().transform(text, self)

    def _insert_conceptual_bridge(self, text):
        from turnitout.core.transformers.advanced import ConceptualBridgeTransformer
        return ConceptualBridgeTransformer().transform(text, self)

    def _maybe_add_citation(self, line, line_num, context_lines=None):
        from turnitout.core.transformers.advanced import CitationShieldTransformer
        return CitationShieldTransformer().transform(line, self, line_num, context_lines)
