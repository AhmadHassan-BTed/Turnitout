class DummyReferenceGenerator:
    """Generates dummy .bib reference templates for any inserted citation keys."""

    def generate(self, used_keys, existing_cite_keys, topic_citations):
        entries = []
        entries.append("% ============================================================")
        entries.append("% DUMMY REFERENCES -- Replace each entry with a real reference")
        entries.append("% The 'note' field describes what topic the reference should cover.")
        entries.append("% ============================================================")
        entries.append("")

        for keywords_tuple, cite_info in topic_citations.items():
            key = cite_info["key"]
            if key in used_keys and key not in existing_cite_keys:
                topic = cite_info["topic"]
                entry = self._make_bib_entry(key, topic)
                entries.append(entry)

        return '\n'.join(entries)

    def _make_bib_entry(self, key, topic):
        return (
            "@article{" + key + ",\n"
            "  author = {PLACEHOLDER -- Replace with real author},\n"
            "  title  = {" + topic + "},\n"
            "  journal = {PLACEHOLDER -- Replace with real journal},\n"
            "  year   = {20XX},\n"
            "  volume = {X},\n"
            "  pages  = {XX--XX},\n"
            "  note   = {DUMMY REFERENCE: Replace this entire entry with a real\n"
            "            reference that covers: " + topic + ".\n"
            "            Search Google Scholar for this topic to find a suitable source.}\n"
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
