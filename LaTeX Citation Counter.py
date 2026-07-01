import re
from collections import Counter

def analyze_tex_citations(tex_file_path):
    # Regex to match \cite, \citet, \citep, \autocite, \textcite, etc.
    # It ignores optional arguments in brackets [...] and captures the keys in braces {...}
    cite_pattern = re.compile(r'\\(?:cite[a-zA-Z*]*|autocite|textcite|parencite)(?:\[.*?\])*\{([^}]+)\}')
    
    citation_counts = Counter()
    
    print(f"Analyzing citations in '{tex_file_path}'...\n")
    
    try:
        with open(tex_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Remove LaTeX comments to avoid counting outed-out citations
            # This regex removes everything from a % to the end of the line
            content_no_comments = re.sub(r'%.*$', '', content, flags=re.MULTILINE)
            
            # Find all citation blocks in the clean content
            matches = cite_pattern.findall(content_no_comments)
            
            for match in matches:
                # Keys can be comma-separated like \cite{ref1, ref2}
                keys = [key.strip() for key in match.split(',')]
                for key in keys:
                    if key:  # Ensure we don't count empty strings
                        citation_counts[key] += 1
                        
    except FileNotFoundError:
        print(f"Error: Could not find the file '{tex_file_path}'.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Print out the analysis
    print("-" * 50)
    print("CITATION FREQUENCY REPORT")
    print("-" * 50)
    
    if not citation_counts:
        print("No citations found in the document.")
        return

    # Calculate summary statistics
    unique_refs = len(citation_counts)
    total_cites = sum(citation_counts.values())
    
    print(f"Total unique references cited: {unique_refs}")
    print(f"Total citation instances:      {total_cites}\n")
    
    print(f"{'Citation Key':<40} | {'Count'}")
    print("-" * 50)
    
    # Sort the output by count (highest first), then alphabetically by the key
    sorted_citations = sorted(citation_counts.items(), key=lambda item: (-item[1], item[0]))
    
    for key, count in sorted_citations:
        print(f"{key:<40} | {count}")

if __name__ == "__main__":
    # Change 'main.tex' if your main LaTeX file has a different name
    TEX_FILE_PATH = "paper_output/Mathematics-thesis-modified/main.tex"
    analyze_tex_citations(TEX_FILE_PATH)