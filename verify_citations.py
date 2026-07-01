#!/usr/bin/env python3
import re
import os

# Read the main.tex file
with open('paper_output/Mathematics-thesis-modified/main.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract all cited references
cited_refs = set()
for match in re.finditer(r'\\cite\{([^}]+)\}', content):
    keys = match.group(1).split(',')
    for key in keys:
        cited_refs.add(key.strip())

# Extract all \nocite references
for match in re.finditer(r'\\nocite\{([^}]+)\}', content):
    keys = match.group(1).split(',')
    for key in keys:
        cited_refs.add(key.strip())

# Read references.bib
bib_refs = set()
with open('paper_output/Mathematics-thesis-modified/references.bib', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.match(r'^@\w+\{([^,]+)', line)
        if match:
            bib_refs.add(match.group(1))

uncited = sorted(bib_refs - cited_refs)

print(f"Total references in .bib: {len(bib_refs)}")
print(f"Cited references: {len(cited_refs)}")
print(f"Uncited references: {len(uncited)}")
print()

if uncited:
    print("UNCITED REFERENCES:")
    for ref in uncited:
        print(f"  - {ref}")
else:
    print("✓ ALL REFERENCES ARE CITED!")

print()
print(f"Sample cited references:")
for ref in sorted(cited_refs)[:10]:
    print(f"  - {ref}")
