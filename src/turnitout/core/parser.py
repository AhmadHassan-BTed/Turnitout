import re

class LaTeXZoneParser:
    """
    Parses a LaTeX file into zones: PROSE (modifiable) vs SKIP (untouchable).
    Tracks math environments, preamble, frontmatter, figures, etc.
    """

    MATH_ENVS = {
        'equation', 'equation*', 'align', 'align*',
        'gather', 'gather*', 'multline', 'multline*',
        'array', 'cases', 'matrix', 'pmatrix', 'bmatrix',
        'vmatrix', 'Vmatrix', 'split', 'eqnarray', 'eqnarray*',
        'flalign', 'flalign*',
    }

    SKIP_ENVS = {
        'figure', 'figure*', 'table', 'table*',
        'verbatim', 'lstlisting', 'titlepage',
        'thebibliography',
    }

    def parse(self, content):
        lines = content.split('\n')
        zones = []

        in_preamble = True
        in_math = False
        in_skip = False
        in_frontmatter = True
        math_env = None
        skip_env = None
        past_first_chapter = False
        env_depth = 0

        in_abstract = False
        in_conclusion = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # -- Preamble --
            if in_preamble:
                if '\\begin{document}' in line:
                    in_preamble = False
                zones.append({'idx': i, 'text': line, 'type': 'SKIP', 'reason': 'preamble'})
                continue

            # -- Track first chapter --
            if re.search(r'\\chapter\{', line) and not past_first_chapter:
                past_first_chapter = True
                in_frontmatter = False

            # -- Frontmatter (abstract, acknowledgments, TOC) --
            if in_frontmatter and not past_first_chapter:
                zones.append({'idx': i, 'text': line, 'type': 'SKIP', 'reason': 'frontmatter'})
                continue

            # -- Abstract environment tracking --
            if '\\begin{abstract}' in line:
                in_abstract = True
            elif '\\end{abstract}' in line:
                in_abstract = False

            # -- Heading tracking to update section states --
            if self._is_heading(stripped):
                is_main_heading = bool(re.match(r'\\(chapter|section)\*?\{', stripped))
                if is_main_heading:
                    title_match = re.search(r'\{([^}]+)\}', stripped)
                    title = title_match.group(1).lower() if title_match else ""
                    if "abstract" in title:
                        in_abstract = True
                        in_conclusion = False
                    elif "conclusion" in title or "future direction" in title or "future work" in title:
                        in_abstract = False
                        in_conclusion = True
                    else:
                        in_abstract = False
                        in_conclusion = False

            # -- Environment tracking --
            env_starts = re.findall(r'\\begin\{(\w+\*?)\}', line)
            env_ends = re.findall(r'\\end\{(\w+\*?)\}', line)

            for es in env_starts:
                if es in self.MATH_ENVS and not in_math:
                    in_math = True
                    math_env = es
                    env_depth = 1
                elif es == math_env and in_math:
                    env_depth += 1
                elif es in self.SKIP_ENVS and not in_skip:
                    in_skip = True
                    skip_env = es

            # -- Determine zone type --
            if in_math:
                zones.append({'idx': i, 'text': line, 'type': 'MATH', 'reason': 'env:' + str(math_env)})
            elif in_skip:
                zones.append({'idx': i, 'text': line, 'type': 'SKIP', 'reason': 'env:' + str(skip_env)})
            elif stripped == '' or stripped.startswith('%'):
                zones.append({'idx': i, 'text': line, 'type': 'SKIP', 'reason': 'empty/comment'})
            elif self._is_pure_command(stripped):
                zones.append({'idx': i, 'text': line, 'type': 'SKIP', 'reason': 'command'})
            elif self._is_math_only(stripped):
                zones.append({'idx': i, 'text': line, 'type': 'MATH', 'reason': 'inline_math'})
            elif self._is_heading(stripped):
                zones.append({'idx': i, 'text': line, 'type': 'HEADING', 'reason': 'heading'})
            else:
                reason = 'text'
                if in_abstract:
                    reason += ':abstract'
                if in_conclusion:
                    reason += ':conclusion'
                zones.append({'idx': i, 'text': line, 'type': 'PROSE', 'reason': reason})

            # -- Close environments --
            for ee in env_ends:
                if ee == math_env and in_math:
                    env_depth -= 1
                    if env_depth <= 0:
                        in_math = False
                        math_env = None
                        env_depth = 0
                elif ee == skip_env and in_skip:
                    in_skip = False
                    skip_env = None

        return zones

    def _is_pure_command(self, line):
        pure_cmds = [
            '\\begin{', '\\end{', '\\clearpage', '\\newpage',
            '\\vspace', '\\hspace', '\\vfill', '\\hfill',
            '\\centering', '\\label{', '\\caption{',
            '\\includegraphics', '\\bibliography', '\\bibliographystyle',
            '\\tableofcontents', '\\listoffigures', '\\listoftables',
            '\\pagenumbering', '\\pagestyle', '\\thispagestyle',
            '\\titleformat', '\\titlespacing', '\\geometry',
            '\\fancyhf', '\\fancyhead', '\\fancyfoot',
            '\\renewcommand', '\\newcommand', '\\setlength',
            '\\rule{', '\\maketitle',
            '\\addcontentsline',
        ]
        return any(line.startswith(cmd) for cmd in pure_cmds)

    def _is_math_only(self, line):
        clean = line.strip()
        if re.match(r'^\$[^$]+\$$', clean):
            return True
        if re.match(r'^\\\[.*\\\]$', clean):
            return True
        if re.match(r'^\\item\s+\$', clean):
            return True
        return False

    def _is_heading(self, line):
        return bool(re.match(r'\\(chapter|section|subsection|subsubsection|subhead|paragraph|subparagraph)\*?\{', line))
