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
