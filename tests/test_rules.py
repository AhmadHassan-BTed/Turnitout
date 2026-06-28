import pytest
from turnitout.core.rules import (
    ACADEMIC_SYNONYMS, PHRASE_REWRITES, PROTECTED_TERMS,
    HEDGE_WORDS, DETERMINER_MAP, SUBORDINATE_CONJUNCTIONS
)

def test_rules_contracts():
    """Verify that the loaded rules databases adhere to expected types and structures."""
    
    # synonyms
    assert isinstance(ACADEMIC_SYNONYMS, dict)
    assert len(ACADEMIC_SYNONYMS) > 0
    for key, val in ACADEMIC_SYNONYMS.items():
        assert isinstance(key, str)
        assert isinstance(val, list)
        assert all(isinstance(x, str) for x in val)
        
    # phrase rewrites
    assert isinstance(PHRASE_REWRITES, list)
    assert len(PHRASE_REWRITES) > 0
    for item in PHRASE_REWRITES:
        assert isinstance(item, tuple)
        assert len(item) == 2
        assert isinstance(item[0], str)
        assert isinstance(item[1], str)
        
    # protected terms
    assert isinstance(PROTECTED_TERMS, set)
    assert len(PROTECTED_TERMS) > 0
    assert all(isinstance(x, str) for x in PROTECTED_TERMS)

    # hedge words
    assert isinstance(HEDGE_WORDS, list)
    assert len(HEDGE_WORDS) > 0
    assert all(isinstance(x, str) for x in HEDGE_WORDS)

    # determiners
    assert isinstance(DETERMINER_MAP, dict)
    assert len(DETERMINER_MAP) > 0
    for key, val in DETERMINER_MAP.items():
        assert isinstance(key, str)
        assert isinstance(val, list)
        assert all(isinstance(x, str) for x in val)

    # conjunctions
    assert isinstance(SUBORDINATE_CONJUNCTIONS, list)
    assert len(SUBORDINATE_CONJUNCTIONS) > 0
    assert all(isinstance(x, str) for x in SUBORDINATE_CONJUNCTIONS)
