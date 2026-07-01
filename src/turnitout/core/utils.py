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

    # Check balanced braces (ignoring escaped \{ and \})
    depth = 0
    in_escape = False
    for i, ch in enumerate(content):
        if ch == '\\':
            in_escape = not in_escape
            continue
        if ch == '{':
            if not in_escape:
                depth += 1
        elif ch == '}':
            if not in_escape:
                depth -= 1
        if depth < 0:
            line_num = content[:i].count('\n') + 1
            issues.append("Unmatched closing brace at line " + str(line_num))
            depth = 0
        in_escape = False
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


def deduplicate_bib_content(content: str) -> str:
    """Robustly parse and deduplicate BibTeX entries by key, keeping the first occurrence."""
    entries = []
    seen_keys = set()
    current_entry = []
    current_key = None
    in_entry = False
    
    for line in content.splitlines(keepends=True):
        if not in_entry:
            match = re.match(r'^\s*@(\w+)\{\s*([\w\-:\.]+)\s*,', line)
            if match:
                in_entry = True
                current_key = match.group(2)
                current_entry = [line]
            else:
                entries.append(line)
        else:
            current_entry.append(line)
            if line.rstrip().endswith('}'):
                entry_str = "".join(current_entry)
                open_braces = entry_str.count('{')
                close_braces = entry_str.count('}')
                if open_braces == close_braces:
                    in_entry = False
                    if current_key:
                        # Case insensitive key check
                        key_lower = current_key.lower()
                        if key_lower not in seen_keys:
                            seen_keys.add(key_lower)
                            entries.append(entry_str)
                    else:
                        entries.append(entry_str)
                    current_key = None
                    current_entry = []
                    
    if current_entry:
        entry_str = "".join(current_entry)
        if current_key:
            key_lower = current_key.lower()
            if key_lower not in seen_keys:
                seen_keys.add(key_lower)
                entries.append(entry_str)
        else:
            entries.append(entry_str)
            
    return "".join(entries)
