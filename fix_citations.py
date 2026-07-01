#!/usr/bin/env python3
"""Fix invalid citations in main.tex - only cite references that actually exist"""

import re
import os

# Read references.bib to get all valid keys
valid_keys = set()
bib_file = "paper_output/Mathematics-thesis-modified/references.bib"
if os.path.exists(bib_file):
    with open(bib_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'^@\w+\{([^,]+)', line)
            if match:
                valid_keys.add(match.group(1))

# Also add dummy_references.bib
dummy_bib = "paper_output/Mathematics-thesis-modified/dummy_references.bib"
if os.path.exists(dummy_bib):
    with open(dummy_bib, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'^@\w+\{([^,]+)', line)
            if match:
                valid_keys.add(match.group(1))

print(f"Valid reference keys: {len(valid_keys)}")
print(f"Sample valid keys: {sorted(valid_keys)[:5]}")
print()

# Read main.tex and find all cited keys
main_tex = "paper_output/Mathematics-thesis-modified/main.tex"
cited_keys = set()
invalid_citations = []

with open(main_tex, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all \cite{} commands
for match in re.finditer(r'\\cite\{([^}]+)\}', content):
    keys_str = match.group(1)
    for key in keys_str.split(','):
        key = key.strip()
        cited_keys.add(key)
        if key not in valid_keys:
            invalid_citations.append((key, match.group(0)))

# Find all \nocite{} commands
for match in re.finditer(r'\\nocite\{([^}]+)\}', content):
    keys_str = match.group(1)
    for key in keys_str.split(','):
        key = key.strip()
        cited_keys.add(key)
        if key not in valid_keys:
            invalid_citations.append((key, match.group(0)))

print(f"Total unique citations: {len(cited_keys)}")
print(f"Invalid citations (not in .bib): {len(invalid_citations)}")

if invalid_citations:
    print("\nInvalid citations found:")
    for key, citation_str in invalid_citations[:10]:
        print(f"  - {key} in {citation_str}")

    # Remove invalid citations from main.tex
    print("\nRemoving invalid citations...")
    modified = content

    for key, citation_str in invalid_citations:
        modified = modified.replace(citation_str, "")

    with open(main_tex, 'w', encoding='utf-8') as f:
        f.write(modified)

    print(f"✓ Removed {len(invalid_citations)} invalid citations from main.tex")
else:
    print("\n✓ All citations are valid!")

# Final count
final_cited = set()
with open(main_tex, 'r', encoding='utf-8') as f:
    final_content = f.read()

for match in re.finditer(r'\\cite\{([^}]+)\}', final_content):
    for key in match.group(1).split(','):
        final_cited.add(key.strip())

for match in re.finditer(r'\\nocite\{([^}]+)\}', final_content):
    for key in match.group(1).split(','):
        final_cited.add(key.strip())

print(f"\nFinal citation count: {len(final_cited)} unique references")
