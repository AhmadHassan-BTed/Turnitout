import re
import os
from collections import defaultdict

def load_existing_bib_keys(bib_path):
    """Load existing citation keys from a .bib file."""
    keys = set()
    if os.path.exists(bib_path):
        with open(bib_path, 'r', encoding='utf-8') as f:
            content = f.read()
        for match in re.finditer(r'@\w+\{(\w+),', content):
            keys.add(match.group(1))
    return keys


def validate_latex(content):
    """Basic LaTeX validation checks to ensure structural/syntactic correctness."""
    issues = []

    # Check balanced braces
    depth = 0
    for i, ch in enumerate(content):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        if depth < 0:
            line_num = content[:i].count('\n') + 1
            issues.append("Unmatched closing brace at line " + str(line_num))
            depth = 0
    if depth != 0:
        issues.append("Unbalanced braces: " + str(depth) + " unclosed '{' remaining")

    # Check balanced dollar signs
    dollar_count = 0
    in_escape = False
    for ch in content:
        if ch == '\\':
            in_escape = True
            continue
        if ch == '$' and not in_escape:
            dollar_count += 1
        in_escape = False
    if dollar_count % 2 != 0:
        issues.append("Odd number of '$' signs (" + str(dollar_count) + ") -- possible broken inline math")

    # Check begin/end environment pairing
    begins = re.findall(r'\\begin\{(\w+\*?)\}', content)
    ends = re.findall(r'\\end\{(\w+\*?)\}', content)
    begin_counts = defaultdict(int)
    end_counts = defaultdict(int)
    for b in begins:
        begin_counts[b] += 1
    for e in ends:
        end_counts[e] += 1
    for env in set(list(begin_counts.keys()) + list(end_counts.keys())):
        if begin_counts[env] != end_counts[env]:
            issues.append("Mismatched \\begin{" + env + "} (" + str(begin_counts[env]) +
                         ") vs \\end{" + env + "} (" + str(end_counts[env]) + ")")

    return issues
