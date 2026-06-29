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
    assert "by we" in modified_voice.lower()
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

