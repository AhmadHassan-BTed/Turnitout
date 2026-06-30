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

def get_default_pipeline():
    """Returns the ordered list of default transformation stages in the pipeline."""
    return [
        PhraseRewriteTransformer(),      # Step 2: Stage 1 (similarity)
        SynonymTransformer(),           # Step 3: Stage 2 (ai)
        ClauseReorderTransformer(),     # Step 4: Stage 3 (similarity)
        DeterminerSwapTransformer(),    # Step 5: Stage 4 (ai)
        SplitCompoundTransformer(),     # Step 6: Stage 5 (similarity)
        HedgeWordTransformer(),         # Step 7: Stage 6 (similarity)
        BreakNgramChainTransformer(),   # Step 8: Stage 7 (similarity)
        VoiceTransformTransformer(),    # Step 9: Stage 8 (ai)
        SentenceFusionTransformer(),    # Step 10: Stage 9 (similarity)
        TransitionInjectTransformer(),  # Step 11: Stage 10 (ai)
        ClauseWordReorderTransformer(), # Step 12: Stage 11 (ai)
        NominalizationTransformer(),    # Step 13: Stage 12 (ai)
        AppositiveInjectTransformer(),  # Step 14: Stage 13 (ai)
        DiscourseRotateTransformer(),   # Step 15: Stage 14 (ai)
        SentenceReorderTransformer(),   # Step 15b: Stage 14b (similarity)
        ContractionTransformer(),       # Step 16: Stage 15 (ai)
        SourceAwareNgramAuditTransformer(), # Step 17: Stage 16 (similarity)
        ConceptualBridgeTransformer(),  # Step 17b: Stage 17 (similarity)
        CitationShieldTransformer(),    # Step 19: Stage 18 (similarity)
    ]

def get_ai_evasion_pipeline():
    """Returns the pipeline of transformers designed for AI Evasion."""
    return [tf for tf in get_default_pipeline() if tf.category == "ai_evasion"]

def get_similarity_evasion_pipeline():
    """Returns the pipeline of transformers designed for Similarity/Plagiarism Evasion."""
    return [tf for tf in get_default_pipeline() if tf.category == "similarity_evasion"]
