import re
import os
from collections import Counter

FILLER_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'by', 'for', 'from', 'in', 'into', 'of', 'off', 'on', 'onto', 'out', 'over', 'to', 'up', 'with', 'under', 'above', 'below', 'between', 'among',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'can', 'could', 'should', 'would', 'will', 'shall', 'may', 'might', 'must',
    'i', 'me', 'my', 'myself', 'we', 'us', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    'this', 'that', 'these', 'those', 'such', 'what', 'which', 'who', 'whom', 'whose', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'now', 'also', 'here',
    'we', 'our', 'show', 'paper', 'chapter', 'section', 'thesis', 'study', 'results', 'equations', 'equation', 'method', 'methods', 'solutions', 'solution', 'using', 'used', 'obtain', 'pde', 'pdes', 'ode', 'odes'
}

def extract_prose_words(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Strip comments
    content = re.sub(r'%.*', '', content)
    # Strip inline math
    content = re.sub(r'\$[^\$]+\$', ' ', content)
    # Strip display math environments
    content = re.sub(r'\\\[.*?\\\]', ' ', content, flags=re.DOTALL)
    for env in ['equation', 'equation*', 'align', 'align*', 'gather', 'gather*']:
        content = re.sub(r'\\begin\{' + env + r'\}.*?\\end\{' + env + r'\}', ' ', content, flags=re.DOTALL)
    
    # Strip LaTeX commands
    content = re.sub(r'\\[a-zA-Z]+(?:\*)?(?:\[[^\]]*\])?(?:\{[^}]*\})*', ' ', content)
    
    # Strip non-alpha characters and split
    content = re.sub(r'[^a-zA-Z\s]', ' ', content)
    return [w.lower() for w in content.split() if len(w) > 0]

def is_valid_phrase(words):
    if words[0] in FILLER_WORDS or words[-1] in FILLER_WORDS:
        return False
    if any(len(w) < 2 for w in words):
        return False
    return True

def main():
    tex_path = r'paper_input\Mathematics-thesis\main.tex'
    if not os.path.exists(tex_path):
        # Auto-detect if folder has different name or find any .tex file inside paper_input
        input_root = "paper_input"
        found = False
        if os.path.exists(input_root):
            for root, dirs, files in os.walk(input_root):
                for file in files:
                    if file.endswith('.tex'):
                        tex_path = os.path.join(root, file)
                        found = True
                        break
                if found:
                    break
    
    print("=" * 65)
    print("  Turnitout -- Paper Topic and Frequency Analysis Utility")
    print("=" * 65)
    print(f"Scanning paper file: {tex_path}")
    
    words = extract_prose_words(tex_path)
    if not words:
        print("Error: Could not find or read any prose words from the LaTeX paper.")
        return
        
    print(f"Parsed {len(words)} prose words (math and formatting excluded).\n")
    
    # Single-word frequencies (excluding stop words)
    single_words = [w for w in words if w not in FILLER_WORDS and len(w) > 2]
    single_counts = Counter(single_words).most_common(30)
    
    # 2-word phrase frequencies
    bi_grams = []
    for i in range(len(words) - 1):
        phrase = (words[i], words[i+1])
        if is_valid_phrase(phrase):
            bi_grams.append(" ".join(phrase))
    bi_counts = Counter(bi_grams).most_common(20)
    
    # 3-word phrase frequencies
    tri_grams = []
    for i in range(len(words) - 2):
        phrase = (words[i], words[i+1], words[i+2])
        if is_valid_phrase(phrase):
            tri_grams.append(" ".join(phrase))
    tri_counts = Counter(tri_grams).most_common(15)
    
    print("TOP TECHNICAL KEYWORDS:")
    for word, count in single_counts[:15]:
        print(f"  - {word}: {count}")
        
    print("\nTOP TECHNICAL KEY-PHRASES (2-WORD):")
    for phrase, count in bi_counts[:12]:
        print(f"  - {phrase}: {count}")
        
    print("\nTOP TECHNICAL KEY-PHRASES (3-WORD):")
    for phrase, count in tri_counts[:8]:
        print(f"  - {phrase}: {count}")
        
    # Generate the prompt for copy-pasting
    print("\n" + "=" * 65)
    print("  COPY-PASTE THE FOLLOWING PROMPT TO CHATGPT/CLAUDE")
    print("=" * 65)
    
    prompt = f"""I am configuring the citation shielding module for "Turnitout", a LaTeX document processor that evades similarity detection. The program injects citations at matching n-gram boundaries based on keywords.

Here is the term frequency analysis of my LaTeX academic document:
- Top single terms: {", ".join([f"{w} ({c})" for w, c in single_counts[:20]])}
- Top 2-word phrases: {", ".join([f"{p} ({c})" for p, c in bi_counts[:15]])}
- Top 3-word phrases: {", ".join([f"{p} ({c})" for p, c in tri_counts[:10]])}

Please generate highly relevant academic topic citations that perfectly fit my paper's content. Format the output exactly as a JSON list matching the following schema. Ensure keys are in format `ref_topic_name` (lowercase, underscores) and keywords contain actual variations from the frequency list:

[
  {{
    "keywords": ["heat equation", "thermal conduction", "diffusion equation", "temperature distribution"],
    "key": "ref_thermal_modeling",
    "topic": "Heat Conduction and Thermal Diffusion Modeling"
  }}
]

Generate only valid JSON, and include 15-20 distinct topics covering all the technical concepts shown in the frequency report. Do not explain the output."""
    
    print(prompt)
    print("=" * 65)
    
if __name__ == '__main__':
    main()
