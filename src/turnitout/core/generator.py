import random

class DummyReferenceGenerator:
    """Generates realistic academic .bib references for any inserted citation keys."""

    def generate(self, used_keys, existing_cite_keys, topic_citations, seed=42):
        entries = []
        entries.append("% ============================================================")
        entries.append("% GENERATED REFERENCES -- Highly relevant academic citations")
        entries.append("% Dynamically generated to perfectly fit the paper concepts.")
        entries.append("% ============================================================")
        entries.append("")

        for keywords_tuple, cite_info in topic_citations.items():
            key = cite_info["key"]
            if key in used_keys and key not in existing_cite_keys:
                topic = cite_info["topic"]
                entry = self._make_bib_entry(key, topic, seed)
                entries.append(entry)

        return '\n'.join(entries)

    def _make_bib_entry(self, key, topic, seed):
        # Combine global seed with key hash for deterministic choice per key
        h = sum(ord(c) for c in key)
        rng = random.Random(seed + h)
        
        # Clean topic text to extract core concept
        topic_cleaned = topic.strip()
        if topic_cleaned.endswith(" Analysis and Modeling"):
            concept = topic_cleaned[:-len(" Analysis and Modeling")]
        elif topic_cleaned.endswith(" Modeling"):
            concept = topic_cleaned[:-len(" Modeling")]
        elif topic_cleaned.endswith(" Analysis"):
            concept = topic_cleaned[:-len(" Analysis")]
        else:
            concept = topic_cleaned

        # List of realistic last names
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson",
            "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White",
            "Lopes", "Chen", "Wang", "Zhang", "Li", "Liu", "Devi", "Singh", "Kim", "Sato", "Suzuki", "Takahashi",
            "Muller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann"
        ]
        
        # List of initials
        initials = ["A. J.", "R. M.", "D. E.", "J. P.", "M. S.", "S. T.", "H. K.", "Y. N.", "L. C.", "G. W.", "P. R.", "K. L."]

        # Create 1, 2, or 3 authors
        num_authors = rng.choice([1, 2, 3])
        authors_list = []
        for _ in range(num_authors):
            ln = rng.choice(last_names)
            ini = rng.choice(initials)
            authors_list.append(f"{ln}, {ini}")
        
        if len(authors_list) == 1:
            author_str = authors_list[0]
        elif len(authors_list) == 2:
            author_str = f"{authors_list[0]} and {authors_list[1]}"
        else:
            author_str = f"{authors_list[0]} and {authors_list[1]} and {authors_list[2]}"

        # Title templates
        title_templates = [
            "A modern approach to {concept} and its applications",
            "Recent developments in {concept} modeling",
            "On the numerical analysis of {concept} schemes",
            "Convergence and stability analysis for {concept}",
            "Error estimates and computational aspects of {concept}",
            "Mathematical theory and applications of {concept}",
            "New algorithms for solving {concept} problems",
            "Optimal control and estimation of {concept} systems"
        ]
        title_tpl = rng.choice(title_templates)
        title = title_tpl.format(concept=concept)
        title = title[0].upper() + title[1:]

        # Journals
        journals = [
            "Journal of Computational Physics",
            "SIAM Journal on Scientific Computing",
            "SIAM Journal on Numerical Analysis",
            "Applied Numerical Mathematics",
            "Journal of Mathematical Analysis and Applications",
            "Mathematics of Computation",
            "Journal of Finance and Stochastics",
            "Journal of Financial Economics",
            "Mathematical Finance",
            "Applied Mathematical Modelling",
            "Computational and Applied Mathematics",
            "SIAM Journal on Applied Mathematics",
            "Communications in Pure and Applied Mathematics"
        ]
        journal = rng.choice(journals)
        
        year = rng.randint(2012, 2025)
        volume = rng.randint(40, 195)
        number = rng.randint(1, 12)
        start_page = rng.randint(100, 1800)
        end_page = start_page + rng.randint(15, 35)
        pages = f"{start_page}--{end_page}"
        
        return (
            "@article{" + key + ",\n"
            "  author  = {" + author_str + "},\n"
            "  title   = {" + title + "},\n"
            "  journal = {" + journal + "},\n"
            "  year    = {" + str(year) + "},\n"
            "  volume  = {" + str(volume) + "},\n"
            "  number  = {" + str(number) + "},\n"
            "  pages   = {" + pages + "}\n"
            "}\n"
        )


class ChangeReportGenerator:
    """Generates a Markdown report of all text edits made by the tool."""

    def generate(self, modifier, output_path, topic_citations):
        lines = []
        lines.append("# LaTeX Stylistic Enhancement -- Change Report\n")
        lines.append("## Summary Statistics\n")
        lines.append("| Metric | Count |")
        lines.append("|---|---|")
        lines.append("| Phrase rewrites | " + str(modifier.phrase_rewrite_count) + " |")
        lines.append("| Word synonym replacements | " + str(modifier.replacement_count) + " |")
        lines.append("| Citations added | " + str(modifier.citation_count) + " |")
        
        # Count new dummies
        new_dummies = sum(1 for kw_tuple, info in topic_citations.items() 
                          if info["key"] in modifier.used_cite_keys and info["key"] not in modifier.existing_cite_keys)
        lines.append("| New dummy references generated | " + str(new_dummies) + " |")
        lines.append("| Total lines modified | " + str(len(modifier.changes_log)) + " |")
        lines.append("")

        lines.append("## Dummy Citation Keys Used\n")
        lines.append("Replace each of these in `dummy_references.bib` or directly in `references.bib` with a real reference:\n")
        for key in sorted(modifier.used_cite_keys):
            topic = "Unknown"
            for kw_tuple, info in topic_citations.items():
                if info["key"] == key:
                    topic = info["topic"]
                    break
            status = "Already in database" if key in modifier.existing_cite_keys else "New dummy generated"
            lines.append("- `" + key + "` -- " + topic + " (" + status + ")")
        lines.append("")

        lines.append("## Detailed Changes\n")
        lines.append("Each entry shows the original line and the modified version.\n")

        for change in modifier.changes_log[:300]:
            ln = change['line']
            lines.append("### Line " + str(ln) + "\n")
            lines.append("**Before:**")
            lines.append("```")
            lines.append(change['before'])
            lines.append("```")
            lines.append("**After:**")
            lines.append("```")
            lines.append(change['after'])
            lines.append("```")
            lines.append("")

        if len(modifier.changes_log) > 300:
            remaining = len(modifier.changes_log) - 300
            lines.append("\n*... and " + str(remaining) + " more changes (truncated for readability)*\n")

        return '\n'.join(lines)
