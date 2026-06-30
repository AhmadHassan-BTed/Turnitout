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
        PhraseRewriteTransformer(),      # Step 2: Stage 1
        SynonymTransformer(),           # Step 3: Stage 2
        ClauseReorderTransformer(),     # Step 4: Stage 3
        DeterminerSwapTransformer(),    # Step 5: Stage 4
        SplitCompoundTransformer(),     # Step 6: Stage 5
        HedgeWordTransformer(),         # Step 7: Stage 6
        BreakNgramChainTransformer(),   # Step 8: Stage 7
        VoiceTransformTransformer(),    # Step 9: Stage 8
        SentenceFusionTransformer(),    # Step 10: Stage 9
        TransitionInjectTransformer(),  # Step 11: Stage 10
        ClauseWordReorderTransformer(), # Step 12: Stage 11
        NominalizationTransformer(),    # Step 13: Stage 12
        AppositiveInjectTransformer(),  # Step 14: Stage 13
        DiscourseRotateTransformer(),   # Step 15: Stage 14
        SentenceReorderTransformer(),   # Step 15b: Stage 14b
        ContractionTransformer(),       # Step 16: Stage 15
        SourceAwareNgramAuditTransformer(), # Step 17: Stage 16
        ConceptualBridgeTransformer(),  # Step 17b: Stage 17
        CitationShieldTransformer(),    # Step 19: Stage 18
    ]
