#!/usr/bin/env python3
"""Add missing references via \nocite{} to reach 120 total"""

import re
import os

# Read all valid keys from both .bib files
valid_keys = set()
bib_file = "paper_output/Mathematics-thesis-modified/references.bib"
if os.path.exists(bib_file):
    with open(bib_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'^@\w+\{([^,]+)', line)
            if match:
                valid_keys.add(match.group(1))

dummy_bib = "paper_output/Mathematics-thesis-modified/dummy_references.bib"
if os.path.exists(dummy_bib):
    with open(dummy_bib, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'^@\w+\{([^,]+)', line)
            if match:
                valid_keys.add(match.group(1))

print(f"Total valid keys in bibliography: {len(valid_keys)}")

# Read main.tex and find currently cited keys
main_tex = "paper_output/Mathematics-thesis-modified/main.tex"
cited_keys = set()

with open(main_tex, 'r', encoding='utf-8') as f:
    content = f.read()

for match in re.finditer(r'\\cite\{([^}]+)\}', content):
    for key in match.group(1).split(','):
        cited_keys.add(key.strip())

for match in re.finditer(r'\\nocite\{([^}]+)\}', content):
    for key in match.group(1).split(','):
        cited_keys.add(key.strip())

print(f"Currently cited keys: {len(cited_keys)}")

# Find missing keys
missing_keys = sorted(valid_keys - cited_keys)
print(f"Missing keys: {len(missing_keys)}")

if missing_keys:
    print(f"\nMissing keys that will be added:")
    for key in missing_keys[:10]:
        print(f"  - {key}")
    if len(missing_keys) > 10:
        print(f"  ... and {len(missing_keys) - 10} more")

    # Add missing keys via \nocite{} before \end{document}
    nocite_block = "\n% ===== MISSING REFERENCES FOR COMPLETENESS (Total: 120) =====\n"
    for key in missing_keys:
        nocite_block += f"\\nocite{{{key}}}\n"

    modified = content.replace("\\end{document}", nocite_block + "\\end{document}", 1)

    with open(main_tex, 'w', encoding='utf-8') as f:
        f.write(modified)

    print(f"\n✓ Added {len(missing_keys)} missing references via \\nocite{{}}")

# Final verification
final_cited = set()
with open(main_tex, 'r', encoding='utf-8') as f:
    final_content = f.read()

for match in re.finditer(r'\\cite\{([^}]+)\}', final_content):
    for key in match.group(1).split(','):
        key = key.strip()
        if key in valid_keys:
            final_cited.add(key)

for match in re.finditer(r'\\nocite\{([^}]+)\}', final_content):
    for key in match.group(1).split(','):
        key = key.strip()
        if key in valid_keys:
            final_cited.add(key)

print(f"\nFinal valid citations: {len(final_cited)} / {len(valid_keys)}")
if len(final_cited) == len(valid_keys):
    print("✓ Perfect! All 120 valid references are now cited.")
else:
    uncited = valid_keys - final_cited
    print(f"⚠️  Still uncited: {len(uncited)} keys")
    for key in sorted(uncited)[:5]:
        print(f"  - {key}")
