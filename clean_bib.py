import re
import os
import sys

def main():
    bib_path = r"paper_output\Mathematics-thesis-modified\references.bib"
    if not os.path.exists(bib_path):
        # Fallback to checking paper_output folders
        if os.path.exists(r"paper_output"):
            for sub in os.listdir(r"paper_output"):
                candidate = os.path.join(r"paper_output", sub, "references.bib")
                if os.path.exists(candidate):
                    bib_path = candidate
                    break

    if not os.path.exists(bib_path):
        print(f"Error: Could not find references.bib at {bib_path}")
        sys.exit(1)

    print(f"Cleaning bibliography database: {bib_path}")
    
    with open(bib_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Deduplicate entries by key, keeping the first occurrence
    entries = []
    seen_keys = set()
    current_entry = []
    current_key = None
    in_entry = False
    removed_count = 0
    duplicate_keys = []

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
                        key_lower = current_key.lower()
                        if key_lower not in seen_keys:
                            seen_keys.add(key_lower)
                            entries.append(entry_str)
                        else:
                            removed_count += 1
                            duplicate_keys.append(current_key)
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
                removed_count += 1
                duplicate_keys.append(current_key)
        else:
            entries.append(entry_str)

    if removed_count > 0:
        cleaned_content = "".join(entries)
        with open(bib_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        print(f"Success: Removed {removed_count} duplicate bibliography entries!")
        print(f"Duplicate keys removed: {', '.join(duplicate_keys)}")
    else:
        print("No duplicate entries found in the bibliography database.")

if __name__ == "__main__":
    main()
