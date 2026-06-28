import pytest
from turnitout.core.parser import LaTeXZoneParser

def test_parser_contract():
    """Verify that LaTeXZoneParser.parse returns a list of zones conforming to our structural contract."""
    parser = LaTeXZoneParser()
    sample_latex = """\\documentclass{report}
\\begin{document}
\\chapter{Introduction Chapter}
\\section{Introduction}
This is a prose sentence about Fourier's Law.
\\begin{equation}
q = -k \\nabla T
\\end{equation}
\\end{document}
"""
    zones = parser.parse(sample_latex)
    
    # Contract validation
    assert isinstance(zones, list)
    assert len(zones) > 0
    for zone in zones:
        assert isinstance(zone, dict)
        assert "idx" in zone
        assert "text" in zone
        assert "type" in zone
        assert "reason" in zone
        
        assert isinstance(zone["idx"], int)
        assert isinstance(zone["text"], str)
        assert zone["type"] in {"PROSE", "MATH", "SKIP", "HEADING"}

def test_parser_zone_types():
    """Verify that zones are categorized correctly according to their environment."""
    parser = LaTeXZoneParser()
    sample_latex = """\\documentclass{report}
\\begin{document}
\\chapter{First Chapter}
\\section{First Section}
This is prose.
\\begin{equation}
x = y
\\end{equation}
\\end{document}
"""
    zones = parser.parse(sample_latex)
    
    # Find matching zone types
    preamble_zones = [z for z in zones if z["reason"] == "preamble"]
    heading_zones = [z for z in zones if z["type"] == "HEADING"]
    prose_zones = [z for z in zones if z["type"] == "PROSE"]
    math_zones = [z for z in zones if z["type"] == "MATH"]
    
    assert len(preamble_zones) > 0
    assert len(heading_zones) == 2
    assert heading_zones[1]["text"] == "\\section{First Section}"
    assert len(prose_zones) == 1
    assert prose_zones[0]["text"] == "This is prose."
    assert len(math_zones) > 0
