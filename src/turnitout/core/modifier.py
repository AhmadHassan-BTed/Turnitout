import re
import random
from turnitout.core.rules import PROTECTED_TERMS, ACADEMIC_SYNONYMS
from turnitout.core.transformers import (
    get_default_pipeline, get_ai_evasion_pipeline, get_similarity_evasion_pipeline
)

class TextModifier:
    """
    Core engine that coordinates the stylistic enhancement and document
    modification pipeline. Protects LaTeX elements, chains modular 
    transformers, guarantees structural diversity, and adds topic citations.
    """

    FILLER_WORDS = {
        # Basic prepositions and conjunctions
        'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'by', 'for', 'from', 'in', 'into', 'of', 'off', 'on', 'onto', 'out', 'over', 'to', 'up', 'with', 'under', 'above', 'below', 'between', 'among',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'can', 'could', 'should', 'would', 'will', 'shall', 'may', 'might', 'must',
        'i', 'me', 'my', 'myself', 'we', 'us', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
        'this', 'that', 'these', 'those', 'such', 'what', 'which', 'who', 'whom', 'whose', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'now', 'also', 'here',
        'we', 'our', 'show', 'paper', 'chapter', 'section', 'thesis', 'study', 'results', 'equations', 'equation', 'method', 'methods', 'solutions', 'solution', 'using', 'used', 'obtain', 'pde', 'pdes', 'ode', 'odes', 'specifically', 'notably', 'clearly', 'indeed', 'essentially',
        # Common general academic verbs
        'explore', 'substitute', 'replace', 'evaluate', 'calculate', 'analyze', 'reformulate', 'examine', 'provide', 'solve', 'determine', 'compare', 'consider', 'propose', 'apply', 'formulate', 'derive', 'obtain', 'show', 'illustrate', 'present', 'discuss', 'explain', 'suggest', 'identify', 'indicate', 'recommend', 'achieve', 'perform', 'verify', 'validate', 'simulate', 'compute', 'price', 'pricing',
        # General adjectives & numbers
        'one', 'two', 'three', 'four', 'five', 'first', 'second', 'third', 'certain', 'current', 'new', 'given', 'particular', 'relevant', 'related', 'different', 'various', 'several', 'many', 'some', 'any', 'every', 'each', 'another', 'own', 'same', 'similar', 'previous', 'aforementioned', 'stipulated', 'designated', 'prescribed', 'specified',
        # General adverbs
        'subsequently', 'obviously', 'manifestly', 'inherently', 'especially', 'particularly', 'consequently', 'therefore', 'thus', 'hence', 'however', 'moreover', 'furthermore', 'accordingly', 'additionally', 'similarly', 'alternatively', 'meanwhile', 'finally', 'originally', 'lately', 'recently', 'generally', 'chiefly', 'mainly', 'principally', 'truly', 'really', 'pretty', 'extremely', 'highly', 'relatively', 'comparatively',
        # General nouns/concepts/units
        'per', 'joule', 'meter', 'second', 'time', 'value', 'values', 'parameters', 'parameter', 'coefficients', 'coefficient', 'variables', 'variable', 'results', 'result', 'data', 'information', 'research', 'work', 'paper', 'thesis', 'approach', 'framework', 'concept', 'concepts', 'aspect', 'aspects', 'view', 'point', 'points', 'fact', 'facts', 'case', 'cases', 'example', 'examples', 'figure', 'figures', 'table', 'tables', 'graph', 'graphs', 'plot', 'plots', 'chart', 'charts', 'illustration', 'illustrations', 'scheme', 'schemes', 'paradigm', 'paradigms', 'strategy', 'strategies', 'tactic', 'tactics', 'procedure', 'procedures', 'technique', 'techniques', 'system', 'systems', 'model', 'models', 'methodology', 'methodologies', 'analysis', 'analyses', 'investigation', 'investigations'
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
        self.existing_cite_keys = existing_cite_keys or set()
        self.min_sentence_length_for_cite = min_sentence_length_for_cite
        self.max_citations_to_insert = max_citations_to_insert
        self.source_grams = source_grams or set()
        self.enable_ngram_audit = enable_ngram_audit

        # Counters for self
        self.structural_guarantee_count = 0
        self.changes_log = []

        # Construct unified config block for pipeline initialization
        config = {
            "aggressiveness": aggressiveness,
            "enable_voice_transform": enable_voice_transform,
            "voice_transform_rate": voice_transform_rate,
            "enable_sentence_fusion": enable_sentence_fusion,
            "sentence_fusion_rate": sentence_fusion_rate,
            "enable_transition_inject": enable_transition_inject,
            "transition_inject_rate": transition_inject_rate,
            "enable_word_reorder": enable_word_reorder,
            "word_reorder_rate": word_reorder_rate,
            "enable_nominalization": enable_nominalization,
            "nominalization_rate": nominalization_rate,
            "enable_appositive": enable_appositive,
            "appositive_rate": appositive_rate,
            "enable_discourse_rotate": enable_discourse_rotate,
            "discourse_rotate_rate": discourse_rotate_rate,
            "enable_info_reorder": enable_info_reorder,
            "info_reorder_rate": info_reorder_rate,
            "enable_contraction": enable_contraction,
            "contraction_rate": contraction_rate,
            "enable_ngram_audit": enable_ngram_audit,
            "source_grams": self.source_grams,
            "enable_conceptual_bridge": enable_conceptual_bridge,
            "conceptual_bridge_rate": conceptual_bridge_rate,
            "enable_risk_citation": enable_risk_citation,
            "min_sentence_length_for_cite": min_sentence_length_for_cite,
            "max_citations_to_insert": max_citations_to_insert,
            "topic_citations": topic_citations or {},
            "filler_words": self.FILLER_WORDS
        }

        # Pipelines
        self.pipeline = get_default_pipeline(config)
        self.ai_pipeline = get_ai_evasion_pipeline(config)
        self.similarity_pipeline = get_similarity_evasion_pipeline(config)

        # O(1) transformer lookup mapping
        self._transformers = {tf.__class__.__name__: tf for tf in self.pipeline}

    # ==================================================================
    # Dynamic Property Delegation for Telemetry Counters & Config maps
    # ==================================================================
    @property
    def replacement_count(self):
        return self._transformers['SynonymTransformer'].replacement_count
    @replacement_count.setter
    def replacement_count(self, value):
        self._transformers['SynonymTransformer'].replacement_count = value

    @property
    def phrase_rewrite_count(self):
        return self._transformers['PhraseRewriteTransformer'].phrase_rewrite_count
    @phrase_rewrite_count.setter
    def phrase_rewrite_count(self, value):
        self._transformers['PhraseRewriteTransformer'].phrase_rewrite_count = value

    @property
    def determiner_swap_count(self):
        return self._transformers['DeterminerSwapTransformer'].determiner_swap_count
    @determiner_swap_count.setter
    def determiner_swap_count(self, value):
        self._transformers['DeterminerSwapTransformer'].determiner_swap_count = value

    @property
    def hedge_insertion_count(self):
        return self._transformers['HedgeWordTransformer'].hedge_insertion_count
    @hedge_insertion_count.setter
    def hedge_insertion_count(self, value):
        self._transformers['HedgeWordTransformer'].hedge_insertion_count = value

    @property
    def contraction_count(self):
        return self._transformers['ContractionTransformer'].contraction_count
    @contraction_count.setter
    def contraction_count(self, value):
        self._transformers['ContractionTransformer'].contraction_count = value

    @property
    def voice_transform_count(self):
        return self._transformers['VoiceTransformTransformer'].voice_transform_count
    @voice_transform_count.setter
    def voice_transform_count(self, value):
        self._transformers['VoiceTransformTransformer'].voice_transform_count = value

    @property
    def sentence_fusion_count(self):
        return self._transformers['SentenceFusionTransformer'].sentence_fusion_count
    @sentence_fusion_count.setter
    def sentence_fusion_count(self, value):
        self._transformers['SentenceFusionTransformer'].sentence_fusion_count = value

    @property
    def transition_inject_count(self):
        return self._transformers['TransitionInjectTransformer'].transition_inject_count
    @transition_inject_count.setter
    def transition_inject_count(self, value):
        self._transformers['TransitionInjectTransformer'].transition_inject_count = value

    @property
    def clause_word_reorder_count(self):
        return self._transformers['ClauseWordReorderTransformer'].clause_word_reorder_count
    @clause_word_reorder_count.setter
    def clause_word_reorder_count(self, value):
        self._transformers['ClauseWordReorderTransformer'].clause_word_reorder_count = value

    @property
    def nominalization_count(self):
        return self._transformers['NominalizationTransformer'].nominalization_count
    @nominalization_count.setter
    def nominalization_count(self, value):
        self._transformers['NominalizationTransformer'].nominalization_count = value

    @property
    def appositive_count(self):
        return self._transformers['AppositiveInjectTransformer'].appositive_count
    @appositive_count.setter
    def appositive_count(self, value):
        self._transformers['AppositiveInjectTransformer'].appositive_count = value

    @property
    def discourse_rotate_count(self):
        return self._transformers['DiscourseRotateTransformer'].discourse_rotate_count
    @discourse_rotate_count.setter
    def discourse_rotate_count(self, value):
        self._transformers['DiscourseRotateTransformer'].discourse_rotate_count = value

    @property
    def info_reorder_count(self):
        return self._transformers['SentenceReorderTransformer'].info_reorder_count
    @info_reorder_count.setter
    def info_reorder_count(self, value):
        self._transformers['SentenceReorderTransformer'].info_reorder_count = value

    @property
    def ngram_break_count(self):
        return self._transformers['BreakNgramChainTransformer'].ngram_break_count
    @ngram_break_count.setter
    def ngram_break_count(self, value):
        self._transformers['BreakNgramChainTransformer'].ngram_break_count = value

    @property
    def ngram_audit_count(self):
        return self._transformers['SourceAwareNgramAuditTransformer'].ngram_audit_count
    @ngram_audit_count.setter
    def ngram_audit_count(self, value):
        self._transformers['SourceAwareNgramAuditTransformer'].ngram_audit_count = value

    @property
    def conceptual_bridge_count(self):
        return self._transformers['ConceptualBridgeTransformer'].conceptual_bridge_count
    @conceptual_bridge_count.setter
    def conceptual_bridge_count(self, value):
        self._transformers['ConceptualBridgeTransformer'].conceptual_bridge_count = value

    @property
    def clause_reorder_count(self):
        return self._transformers['ClauseReorderTransformer'].clause_reorder_count
    @clause_reorder_count.setter
    def clause_reorder_count(self, value):
        self._transformers['ClauseReorderTransformer'].clause_reorder_count = value

    @property
    def sentence_split_count(self):
        return self._transformers['SplitCompoundTransformer'].sentence_split_count
    @sentence_split_count.setter
    def sentence_split_count(self, value):
        self._transformers['SplitCompoundTransformer'].sentence_split_count = value

    @property
    def citation_count(self):
        return self._transformers['CitationShieldTransformer'].citation_count
    @citation_count.setter
    def citation_count(self, value):
        self._transformers['CitationShieldTransformer'].citation_count = value

    @property
    def risk_citation_count(self):
        return self._transformers['CitationShieldTransformer'].risk_citation_count
    @risk_citation_count.setter
    def risk_citation_count(self, value):
        self._transformers['CitationShieldTransformer'].risk_citation_count = value

    @property
    def used_cite_keys(self):
        return self._transformers['CitationShieldTransformer'].used_cite_keys
    @used_cite_keys.setter
    def used_cite_keys(self, value):
        self._transformers['CitationShieldTransformer'].used_cite_keys = value

    @property
    def topic_citations(self):
        return self._transformers['CitationShieldTransformer'].topic_citations
    @topic_citations.setter
    def topic_citations(self, value):
        self._transformers['CitationShieldTransformer'].topic_citations = value

    # ==================================================================
    # Core Pipeline Orchestration
    # ==================================================================
    def modify_line(self, line, line_num, context_lines=None):
        original = line
        stripped = line.strip()
        if len(stripped) < 15:
            return line

        # Step 1: Protect LaTeX elements with placeholders
        protected_line, placeholders = self._protect_latex(line)

        # Run first 15 stages
        struct_changes = 0
        
        for idx in range(15):
            tf = self.pipeline[idx]
            prev_text = protected_line
            protected_line = tf.transform(protected_line, self.rng, line_num, context_lines)
            if idx in [2, 3, 7, 10, 11, 12, 13] and protected_line != prev_text:
                struct_changes += 1

        # Structural Diversity Guarantee: For sentences > 60 chars, ensure at least 2 structural transformations are applied.
        if len(stripped) > 60 and struct_changes < 2:
            fallbacks = [
                self._transformers['DeterminerSwapTransformer'],
                self._transformers['VoiceTransformTransformer'],
                self._transformers['ClauseWordReorderTransformer'],
                self._transformers['NominalizationTransformer'],
                self._transformers['AppositiveInjectTransformer'],
                self._transformers['DiscourseRotateTransformer']
            ]
            self.rng.shuffle(fallbacks)
            for tf in fallbacks:
                if struct_changes >= 2:
                    break
                prev_text = protected_line
                protected_line = tf.transform(protected_line, self.rng, line_num, context_lines, force_run=True)
                if protected_line != prev_text:
                    struct_changes += 1
                    self.structural_guarantee_count += 1

        # Run remaining pipeline steps (Contraction, N-gram Auditing, Conceptual Bridge)
        for idx in range(15, len(self.pipeline) - 1):
            tf = self.pipeline[idx]
            protected_line = tf.transform(protected_line, self.rng, line_num, context_lines)

        # Restore LaTeX elements
        modified_line = self._restore_latex(protected_line, placeholders)

        # Run the final pipeline step: Citation Shielding (operates on restored LaTeX)
        citation_transformer = self.pipeline[-1]
        modified_line = citation_transformer.transform(modified_line, self.rng, line_num, context_lines)

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
                            self._transformers['SourceAwareNgramAuditTransformer'].ngram_audit_count += 1
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
                    self._transformers['SourceAwareNgramAuditTransformer'].ngram_audit_count += 1
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
        return self._transformers['ClauseReorderTransformer'].transform(text, self.rng)

    def _swap_determiners(self, text):
        return self._transformers['DeterminerSwapTransformer'].transform(text, self.rng)

    def _split_compound_sentences(self, text):
        return self._transformers['SplitCompoundTransformer'].transform(text, self.rng)

    def _insert_hedge_words(self, text):
        return self._transformers['HedgeWordTransformer'].transform(text, self.rng)

    def _break_ngram_chains(self, text):
        return self._transformers['BreakNgramChainTransformer'].transform(text, self.rng)

    def _transform_voice(self, text):
        return self._transformers['VoiceTransformTransformer'].transform(text, self.rng)

    def _fuse_sentences(self, text, context_lines):
        return self._transformers['SentenceFusionTransformer'].transform(text, self.rng, context_lines=context_lines)

    def _inject_transitions(self, text):
        return self._transformers['TransitionInjectTransformer'].transform(text, self.rng)

    def _reorder_within_clause(self, text):
        return self._transformers['ClauseWordReorderTransformer'].transform(text, self.rng)

    def _nominalize(self, text):
        return self._transformers['NominalizationTransformer'].transform(text, self.rng)

    def _inject_appositives(self, text):
        return self._transformers['AppositiveInjectTransformer'].transform(text, self.rng)

    def _rotate_discourse_markers(self, text):
        return self._transformers['DiscourseRotateTransformer'].transform(text, self.rng)

    def _rotate_contractions(self, text):
        return self._transformers['ContractionTransformer'].transform(text, self.rng)

    def _source_aware_ngram_audit(self, text):
        return self._transformers['SourceAwareNgramAuditTransformer'].transform(text, self.rng)

    def _reorder_sentences(self, text):
        return self._transformers['SentenceReorderTransformer'].transform(text, self.rng)

    def _insert_conceptual_bridge(self, text):
        return self._transformers['ConceptualBridgeTransformer'].transform(text, self.rng)

    def _maybe_add_citation(self, line, line_num, context_lines=None):
        return self._transformers['CitationShieldTransformer'].transform(line, self.rng, line_num, context_lines)
