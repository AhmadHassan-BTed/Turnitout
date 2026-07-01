import pytest
from turnitout.core.modifier import TextModifier
from turnitout.core.utils import validate_latex

def test_modifier_contract():
    """Verify the TextModifier API contract and structural properties."""
    modifier = TextModifier(seed=42, aggressiveness=0.8, topic_citations={})
    
    line = "This is a simple sentence about science."
    modified = modifier.modify_line(line, 0)
    
    assert isinstance(modified, str)
    assert len(modified) > 0

def test_modifier_syntax_preservation():
    """Verify that modifier runs preserve valid LaTeX syntax (dollar signs, braces, zero nulls)."""
    # Create modifier with mock topic citations
    topic_citations = {
        ("science",): {
            "key": "ref_science",
            "topic": "General Scientific Methods"
        }
    }
    modifier = TextModifier(seed=42, aggressiveness=1.0, topic_citations=topic_citations)
    
    complex_prose = "This is some science prose wrapping a \\textbf{bold block} and inline math $a^2 + b^2 = c^2$."
    modified = modifier.modify_line(complex_prose, 0)
    
    # Contract/Syntax validations
    assert "\x00" not in modified  # Placeholder character check
    
    issues = validate_latex(modified)
    assert len(issues) == 0  # Braces, environments and dollar signs should remain balanced

def test_reorder_clauses_preservation():
    """Verify clause reordering syntax remains valid."""
    modifier = TextModifier(seed=42, aggressiveness=0.5)
    line = "The numerical convergence increases, since the spatial grid size is reduced."
    modified = modifier._reorder_clauses(line)
    
    assert isinstance(modified, str)
    assert modified.endswith(".")
    assert validate_latex(modified) == []

def test_new_transformation_stages():
    """Verify that all new transformation stages modify text and preserve syntax."""
    modifier = TextModifier(seed=42, enable_voice_transform=True, voice_transform_rate=1.0,
                            enable_sentence_fusion=True, sentence_fusion_rate=1.0,
                            enable_transition_inject=True, transition_inject_rate=1.0,
                            enable_word_reorder=True, word_reorder_rate=1.0,
                            enable_nominalization=True, nominalization_rate=1.0,
                            enable_appositive=True, appositive_rate=1.0,
                            enable_discourse_rotate=True, discourse_rotate_rate=1.0)

    # 1. Voice transform
    line_voice = "We analyzed the results of the second-order partial differential equations under various boundary conditions."
    modified_voice = modifier._transform_voice(line_voice)
    assert "were analyzed" in modified_voice.lower()
    assert validate_latex(modified_voice) == []

    # 2. Sentence fusion
    line_fuse = "The temperature increased."
    context = ["This caused expansion."]
    modified_fuse = modifier._fuse_sentences(line_fuse, context)
    assert "which" in modified_fuse or "thereby" in modified_fuse or "consequently" in modified_fuse
    assert validate_latex(modified_fuse) == []

    # 3. Transition injection
    line_transition = "The results are consistent with the model, indicating a high level of accuracy in the calculations."
    modified_transition = modifier._inject_transitions(line_transition)
    assert modified_transition != line_transition
    assert validate_latex(modified_transition) == []

    # 4. Clause word reordering
    line_reorder = "In this chapter, we present the results of our extensive numerical investigations on option pricing."
    modified_reorder = modifier._reorder_within_clause(line_reorder)
    assert "in this chapter" in modified_reorder.lower()
    assert modified_reorder != line_reorder
    assert validate_latex(modified_reorder) == []

    # 5. Nominalization
    line_nominal = "We investigated the phenomenon of thermal diffusion in a stretching sheet using numerical methods."
    modified_nominal = modifier._nominalize(line_nominal)
    assert "investigation of" in modified_nominal.lower()
    assert validate_latex(modified_nominal) == []

    # 6. Appositives
    line_appositive = "The Crank-Nicolson method is applied."
    modified_appositive = modifier._inject_appositives(line_appositive)
    assert "scheme" in modified_appositive
    assert validate_latex(modified_appositive) == []

    # 7. Discourse rotation
    line_discourse = "However, the convergence speed is slow."
    modified_discourse = modifier._rotate_discourse_markers(line_discourse)
    assert "however" not in modified_discourse.lower()
    assert validate_latex(modified_discourse) == []


def test_contraction_conversion():
    """Verify that contraction converter operates correctly and preserves syntax."""
    modifier = TextModifier(seed=42, enable_contraction=True, contraction_rate=1.0)
    
    # 1. Test compression: cannot -> can't
    line_compress = "We cannot solve this equation analytically."
    modified_compress = modifier._rotate_contractions(line_compress)
    assert "can't" in modified_compress.lower()
    assert validate_latex(modified_compress) == []

    # 2. Test expansion: don't -> do not
    line_expand = "We don't need to refine the grid further."
    modified_expand = modifier._rotate_contractions(line_expand)
    assert "do not" in modified_expand.lower()
    assert validate_latex(modified_expand) == []


def test_ngram_audit():
    """Verify that surviving n-grams matching the source document are forcefully broken."""
    source_grams = {("solve", "this", "equation", "analytically", "now")}
    modifier = TextModifier(seed=42, enable_ngram_audit=True, source_grams=source_grams)
    
    line = "We solve this equation analytically now using custom methods."
    audited = modifier._source_aware_ngram_audit(line)
    
    # Verify that the matching 5-gram is broken (does not exist in audited tokens)
    audited_grams = modifier._get_kgrams(audited, k=5)
    for gram in audited_grams:
        assert gram != ("solve", "this", "equation", "analytically", "now")
        
    assert validate_latex(audited) == []


def test_structural_diversity():
    """Verify that sentences > 60 chars receive at least 2 structural transformations under guarantee."""
    modifier = TextModifier(
        seed=42,
        enable_voice_transform=True, voice_transform_rate=0.0, # disabled normally
        enable_word_reorder=True, word_reorder_rate=0.0,
        enable_nominalization=True, nominalization_rate=0.0,
        enable_appositive=True, appositive_rate=0.0,
        enable_discourse_rotate=True, discourse_rotate_rate=0.0
    )
    
    # A long sentence that matches multiple structural rules
    line = "In this study, we analyzed the results of the second-order partial differential equations under various boundary conditions."
    modified = modifier.modify_line(line, 0)
    
    # The guarantee should have forced at least two structural adjustments, changing the line
    assert modified != line
    total_struct = (modifier.voice_transform_count + modifier.clause_word_reorder_count + 
                    modifier.nominalization_count + modifier.appositive_count + 
                    modifier.discourse_rotate_count + modifier.clause_reorder_count + 
                    modifier.determiner_swap_count)
    assert total_struct >= 2
    assert validate_latex(modified) == []


def test_sentence_reorder():
    """Verify that independent adjacent sentences within a prose paragraph are reordered."""
    modifier = TextModifier(seed=42, enable_info_reorder=True, info_reorder_rate=1.0)
    
    # 3 sentences, where sentence 2 and 3 are independent
    line = "First sentence here. Second sentence starts. Third sentence starts."
    modified = modifier._reorder_sentences(line)
    
    assert modified != line
    assert "second" in modified.lower()
    assert "third" in modified.lower()
    assert modifier.info_reorder_count >= 1
    assert validate_latex(modified) == []


def test_conceptual_bridging():
    """Verify that generic connecting sentences are appended to long paragraph blocks to dilute similarity."""
    modifier = TextModifier(seed=42, enable_conceptual_bridge=True, conceptual_bridge_rate=1.0)
    
    line = "We present a comprehensive formulation of the thermal conduction and mathematical diffusion processes that can model the heat flow across any multi-layered physical material under realistic boundary conditions."
    modified = modifier._insert_conceptual_bridge(line)
    
    assert modified != line
    assert any(bridge in modified for bridge in TextModifier.CONCEPTUAL_BRIDGES)
    assert modifier.conceptual_bridge_count >= 1
    assert validate_latex(modified) == []


def test_overlap_detection_and_resolution():
    """Verify that overlap detection correctly identifies semantic overlaps and CitationShieldTransformer maps them."""
    from turnitout.core.utils import check_overlap
    from turnitout.core.transformers.similarity_evasion import CitationShieldTransformer

    # 1. Direct test of check_overlap
    existing = [
        ("ref_thermal_modeling", "Heat Conduction and Thermal Diffusion Modeling"),
        ("ref_wave_propagation", "Wave Propagation and Vibration Analysis")
    ]
    # Candidate that overlaps (conduction, heat)
    assert check_overlap("ref_heat_conduction_modeling", "Heat Conduction Modeling and Heat Transfer", existing) is True
    # Candidate that overlaps (wave, acoustic, propagation)
    assert check_overlap("ref_wave_equation_propagation", "Wave Equation and Acoustic Propagation", existing) is True
    # Candidate that does NOT overlap
    assert check_overlap("ref_option_pricing", "Option Pricing and Financial Derivative Models", existing) is False

    # 2. Test mapping inside CitationShieldTransformer
    topic_citations = {
        ("heat", "conduction", "thermal"): {
            "key": "ref_thermal_modeling",
            "topic": "Heat Conduction and Thermal Diffusion Modeling"
        }
    }
    transformer = CitationShieldTransformer(topic_citations=topic_citations)
    # This line has "heat transfer" which should not match "conduction" in the keyword loop,
    # but the phrase extractor will find "heat transfer", which overlaps with "Heat Conduction and Thermal Diffusion Modeling" (word "heat").
    # It should map it back to "ref_thermal_modeling".
    key = transformer._determine_topic_citation("The system undergoes heat transfer across the boundary.")
    assert key == "ref_thermal_modeling"


