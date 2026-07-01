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
    """
    Robustly parse and deduplicate BibTeX entries by citation key AND normalized title.
    Uses brace-depth tracking for reliable entry boundary detection.
    Keeps the first occurrence; silently drops all later duplicates.
    """
    seen_keys: set = set()
    seen_titles: set = set()
    result_parts: list = []
    i = 0
    lines = content.splitlines(keepends=True)
    n = len(lines)

    while i < n:
        line = lines[i]
        entry_match = re.match(r'^\s*@(\w+)\{\s*([\w\-:\.]+)\s*,', line)
        if not entry_match:
            result_parts.append(line)
            i += 1
            continue

        key = entry_match.group(2)
        key_lower = key.lower()

        # Collect the full entry via brace-depth tracking (reliable vs. endswith heuristic)
        brace_depth = 0
        entry_lines = []
        while i < n:
            l = lines[i]
            brace_depth += l.count('{') - l.count('}')
            entry_lines.append(l)
            i += 1
            if brace_depth <= 0:
                break

        entry_str = "".join(entry_lines)

        # Normalize title for title-based deduplication
        title_normalized = None
        title_match = re.search(
            r'(?i)title\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}',
            entry_str, re.DOTALL
        )
        if title_match:
            raw = title_match.group(1)
            raw = re.sub(r'[\{\}\\]', '', raw)
            title_normalized = re.sub(r'\s+', ' ', raw).lower().strip()

        is_dup_key = key_lower in seen_keys
        is_dup_title = (title_normalized is not None) and (title_normalized in seen_titles)

        if not is_dup_key and not is_dup_title:
            seen_keys.add(key_lower)
            if title_normalized:
                seen_titles.add(title_normalized)
            result_parts.append(entry_str)
        # else: duplicate — silently drop

    return "".join(result_parts)


def check_overlap(cand_key, cand_topic, existing_topics):
    """Check if a candidate key or topic name overlaps with any of the existing topics."""
    def get_clean_words(text):
        if not text:
            return set()
        text = text.lower().replace('_', ' ').replace('-', ' ')
        words = re.findall(r'[a-z]+', text)
        stopwords = {
            'ref', 'and', 'or', 'of', 'in', 'for', 'to', 'with', 'on', 'at', 'by', 'an', 'the', 'its', 'their', 'his', 'her',
            'modeling', 'model', 'models', 'methods', 'method', 'solutions', 'solution', 
            'analysis', 'scheme', 'schemes', 'pricing', 'algorithms', 'algorithm', 
            'framework', 'frameworks', 'theory', 'theories', 'processes', 'process', 
            'study', 'studies', 'investigation', 'investigations', 'approach', 'approaches',
            'techniques', 'technique', 'discretization', 'computation', 'computational', 
            'numerical', 'applied', 'approximation', 'approximations', 'equations', 'equation',
            'science', 'research', 'work', 'paper', 'chapter', 'section', 'thesis', 'results',
            'result', 'applications', 'application', 'modern', 'basic', 'fundamental', 'fundamentals',
            'introduction', 'introductory', 'overview', 'review', 'perspective', 'perspectives',
            'aspect', 'aspects', 'case', 'cases', 'problem', 'problems', 'system', 'systems',
            'linear', 'nonlinear', 'first', 'second', 'third', 'order', 'high', 'low', 'general',
            'generalized', 'some', 'new', 'recent', 'developments', 'development', 'advanced',
            'estimation', 'control', 'optimal', 'optimization', 'rate', 'rates', 'variable', 'variables',
            'classical', 'classic', 'element', 'elements', 'volume', 'volumes', 'difference', 'differences',
            'course', 'one', 'two', 'three', 'four', 'five'
        }
        return {w for w in words if w not in stopwords and len(w) > 2}

    cand_words = get_clean_words(cand_key).union(get_clean_words(cand_topic))
    if not cand_words:
        return False

    for exist_key, exist_topic in existing_topics:
        exist_words = get_clean_words(exist_key).union(get_clean_words(exist_topic))
        # Check if they share any word or highly similar word
        for cw in cand_words:
            for ew in exist_words:
                if cw == ew:
                    return True
                # Singular/plural match
                if cw + 's' == ew or ew + 's' == cw:
                    return True
                if cw + 'es' == ew or ew + 'es' == cw:
                    return True
                # Prefix match for words of length >= 4
                if len(cw) >= 4 and len(ew) >= 4:
                    min_len = min(len(cw), len(ew))
                    prefix_len = 0
                    for i in range(min_len):
                        if cw[i] == ew[i]:
                            prefix_len += 1
                        else:
                            break
                    if prefix_len >= 4:
                        return True
    return False


def load_existing_bib_topics(bib_path):
    """Load existing citation keys and their titles/topics from a .bib file."""
    topics = []
    if not os.path.exists(bib_path):
        return topics
        
    with open(bib_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    pos = 0
    pattern = re.compile(r'@\w+\{\s*([\w\-:\.]+)\s*,', re.IGNORECASE)
    while True:
        match = pattern.search(content, pos)
        if not match:
            break
        key = match.group(1)
        start_idx = match.end()
        
        # Find matching closing brace for the entry
        brace_depth = 1
        i = start_idx
        while i < len(content) and brace_depth > 0:
            if content[i] == '{':
                brace_depth += 1
            elif content[i] == '}':
                brace_depth -= 1
            i += 1
        entry_content = content[start_idx:i]
        pos = i
        
        # Extract title
        title_match = re.search(r'title\s*=\s*[\{\"\'](.*?)[\}\"\']\s*(?:,|$)', entry_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1)
            # Remove braces/backslashes
            title = re.sub(r'[\{\}\\]', '', title)
            title = ' '.join(title.split())
            topics.append((key, title))
        else:
            topics.append((key, key.replace('_', ' ').replace('-', ' ')))
            
    return topics

