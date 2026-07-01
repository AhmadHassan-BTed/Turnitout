import re
from collections import defaultdict

def check_bib_duplicates(file_path):
    # Regex patterns to extract keys and titles
    # Matches `@entrytype{citation_key,`
    key_pattern = re.compile(r'@\w+\s*{\s*([^,]+),')
    # Matches `title = {Some Title}` or `title = "Some Title"`
    title_pattern = re.compile(r'title\s*=\s*[{"]([^}"]+)[}"]', re.IGNORECASE)

    seen_keys = set()
    duplicate_keys = []
    
    seen_titles = defaultdict(list)

    print(f"Analyzing '{file_path}'...\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # --- 1. Find Duplicate Citation Keys ---
            keys = key_pattern.findall(content)
            for key in keys:
                clean_key = key.strip()
                if clean_key in seen_keys:
                    duplicate_keys.append(clean_key)
                else:
                    seen_keys.add(clean_key)

            # --- 2. Find Duplicate Titles (Different Keys) ---
            # Split the file by '@' to process individual entries
            entries = content.split('@')
            for entry in entries[1:]: # Skip the first empty split before the first '@'
                key_match = re.search(r'^\w+\s*{\s*([^,]+),', entry)
                title_match = re.search(r'title\s*=\s*[{"]([^}"]+)[}"]', entry, re.IGNORECASE)
                
                if key_match and title_match:
                    entry_key = key_match.group(1).strip()
                    # Normalize the title: lowercase and remove extra whitespace/newlines
                    entry_title = " ".join(title_match.group(1).lower().split())
                    seen_titles[entry_title].append(entry_key)

    except FileNotFoundError:
        print(f"Error: Could not find the file '{file_path}'.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # --- Print Results ---
    print("-" * 40)
    print("1. DUPLICATE CITATION KEYS")
    print("-" * 40)
    if duplicate_keys:
        print("WARNING: The following citation keys appear more than once. This will break LaTeX!")
        for key in set(duplicate_keys):
            # Count how many times the key appeared in total
            count = keys.count(key)
            print(f" - {key} (appears {count} times)")
    else:
        print("Awesome! No duplicate citation keys found.")

    print("\n" + "-" * 40)
    print("2. DUPLICATE TITLES (Same paper, different keys)")
    print("-" * 40)
    found_duplicate_titles = False
    for title, keys_list in seen_titles.items():
        if len(keys_list) > 1:
            found_duplicate_titles = True
            print(f"Title: {title.title()}")
            print(f" -> Found under keys: {', '.join(keys_list)}\n")
            
    if not found_duplicate_titles:
        print("Awesome! No duplicate titles found.")

if __name__ == "__main__":
    # Change 'references.bib' to the actual name of your bib file
    BIB_FILE_PATH = "paper_output/Mathematics-thesis-modified/references.bib" 
    check_bib_duplicates(BIB_FILE_PATH)