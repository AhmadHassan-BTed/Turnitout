#!/usr/bin/env python3
"""Debug script to understand why not all 120 citations are being used"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from turnitout.config import load_config_json
from turnitout.core.utils import load_existing_bib_keys, load_existing_bib_topics
from turnitout.core.rules import GENERAL_ACADEMIC_TOPICS

config = load_config_json("math_thesis")
existing_cite_keys = load_existing_bib_keys(config.BIB_FILE)
bib_topics = load_existing_bib_topics(config.BIB_FILE)

print(f"Existing keys in .bib: {len(existing_cite_keys)}")
print(f"Target citations: {config.TOTAL_CITATIONS}")
print(f"Target NEW dummies: {config.TOTAL_CITATIONS - len(existing_cite_keys)}")
print()
print(f"GENERAL_ACADEMIC_TOPICS entries: {len(GENERAL_ACADEMIC_TOPICS)}")
print(f"Bib topics entries: {len(bib_topics)}")
print()
print("Sample GENERAL_ACADEMIC_TOPICS:")
for i, (key, topic) in enumerate(GENERAL_ACADEMIC_TOPICS[:5]):
    print(f"  {key}: {topic}")
print()
print(f"Total to generate: {config.TOTAL_CITATIONS - len(existing_cite_keys)}")
print(f"Available pool size: {len(GENERAL_ACADEMIC_TOPICS)}")
if len(GENERAL_ACADEMIC_TOPICS) < (config.TOTAL_CITATIONS - len(existing_cite_keys)):
    print(f"⚠️  WARNING: Base topics pool ({len(GENERAL_ACADEMIC_TOPICS)}) is SMALLER than required!")
    print(f"   This will LIMIT the number of new dummies that can be generated")
else:
    print(f"✓ Base topics pool is large enough")
