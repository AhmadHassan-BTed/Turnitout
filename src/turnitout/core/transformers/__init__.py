from turnitout.core.transformers.base import BaseTransformer
from turnitout.core.transformers.lexical import (
    PhraseRewriteTransformer, SynonymTransformer, DeterminerSwapTransformer,
    HedgeWordTransformer, ContractionTransformer
)
from turnitout.core.transformers.syntactic import (
    VoiceTransformTransformer, SentenceFusionTransformer, TransitionInjectTransformer,
    ClauseWordReorderTransformer, NominalizationTransformer, AppositiveInjectTransformer
)
from turnitout.core.transformers.structural import (
    ClauseReorderTransformer, SplitCompoundTransformer, SentenceReorderTransformer,
    DiscourseRotateTransformer
)
from turnitout.core.transformers.advanced import (
    BreakNgramChainTransformer, SourceAwareNgramAuditTransformer,
    ConceptualBridgeTransformer, CitationShieldTransformer
)

def get_default_pipeline(config=None):
    """Returns the ordered list of default transformation stages, configured with localized parameters."""
    config = config or {}

    return [
        PhraseRewriteTransformer(),
        SynonymTransformer(
            aggressiveness=config.get("aggressiveness", 0.55)
        ),
        ClauseReorderTransformer(),
        DeterminerSwapTransformer(),
        SplitCompoundTransformer(),
        HedgeWordTransformer(),
        BreakNgramChainTransformer(),
        VoiceTransformTransformer(
            voice_transform_rate=config.get("voice_transform_rate", 0.30),
            enable_voice_transform=config.get("enable_voice_transform", True)
        ),
        SentenceFusionTransformer(
            sentence_fusion_rate=config.get("sentence_fusion_rate", 0.25),
            enable_sentence_fusion=config.get("enable_sentence_fusion", True)
        ),
        TransitionInjectTransformer(
            transition_inject_rate=config.get("transition_inject_rate", 0.25),
            enable_transition_inject=config.get("enable_transition_inject", True)
        ),
        ClauseWordReorderTransformer(
            word_reorder_rate=config.get("word_reorder_rate", 0.20),
            enable_word_reorder=config.get("enable_word_reorder", True)
        ),
        NominalizationTransformer(
            nominalization_rate=config.get("nominalization_rate", 0.20),
            enable_nominalization=config.get("enable_nominalization", True)
        ),
        AppositiveInjectTransformer(
            appositive_rate=config.get("appositive_rate", 0.35),
            enable_appositive=config.get("enable_appositive", True)
        ),
        DiscourseRotateTransformer(
            discourse_rotate_rate=config.get("discourse_rotate_rate", 0.50),
            enable_discourse_rotate=config.get("enable_discourse_rotate", True)
        ),
        SentenceReorderTransformer(
            info_reorder_rate=config.get("info_reorder_rate", 0.20),
            enable_info_reorder=config.get("enable_info_reorder", True)
        ),
        ContractionTransformer(
            contraction_rate=config.get("contraction_rate", 0.20),
            enable_contraction=config.get("enable_contraction", True)
        ),
        SourceAwareNgramAuditTransformer(
            enable_ngram_audit=config.get("enable_ngram_audit", True),
            source_grams=config.get("source_grams", None)
        ),
        ConceptualBridgeTransformer(
            enable_conceptual_bridge=config.get("enable_conceptual_bridge", True),
            conceptual_bridge_rate=config.get("conceptual_bridge_rate", 0.20)
        ),
        CitationShieldTransformer(
            enable_risk_citation=config.get("enable_risk_citation", True),
            source_grams=config.get("source_grams", None),
            min_sentence_length_for_cite=config.get("min_sentence_length_for_cite", 60),
            max_citations_to_insert=config.get("max_citations_to_insert", 30),
            topic_citations=config.get("topic_citations", None),
            filler_words=config.get("filler_words", None)
        ),
    ]

def get_ai_evasion_pipeline(config=None):
    """Returns the pipeline of transformers designed for AI Evasion."""
    return [tf for tf in get_default_pipeline(config) if tf.category == "ai_evasion"]

def get_similarity_evasion_pipeline(config=None):
    """Returns the pipeline of transformers designed for Similarity/Plagiarism Evasion."""
    return [tf for tf in get_default_pipeline(config) if tf.category == "similarity_evasion"]
