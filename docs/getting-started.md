# Getting Started Guide — Turnitout

Welcome to Turnitout! This guide walks you through processing a brand-new paper from scratch using our **Zero-Configuration** workflow.

---

## 🚀 The 3-Step Workflow (No Config Needed!)

You don't need to write any configuration files or set up keyword lists. The tool automatically detects your files and performs frequency analysis on your text to extract keywords on-the-fly.

### Step 1: Copy your LaTeX Project Folder
Copy your entire LaTeX project folder (containing your `.tex` files, `.bib` bibliography file, and image folders) and paste it inside the **`paper_input/`** directory.

*For example, if your paper folder is called `MyChemistryPaper`, your path should look like:*
`paper_input/MyChemistryPaper/main.tex`

---

### Step 2: Run the Script
Open your command prompt or terminal in the project root directory, and simply run the program:

```bash
python run.py
```

#### 🔍 What happens in this step:
1. **Auto-Detection**: Python scans `paper_input/` and auto-detects your paper folder, your main `.tex` file, and your `.bib` bibliography database.
2. **Frequency Analysis**: Python reads your LaTeX document, ignores LaTeX commands and equations, and automatically extracts the top 10 most frequent scientific keywords.
3. **Paraphrasing & Citation**: The script parphrases your text, inserts `\cite{...}` commands near sentences containing those high-frequency keywords, and copies all image folders to the output folder.

---

### Step 3: Resolve Citations with AI
When the run finishes:
1. Open the generated output folder: **`paper_output/<your-project-name>-modified/`**.
2. Locate and open the file **`ai_prompt.txt`** (which Python generated for you).
3. **Copy the entire text** inside this file and paste it into ChatGPT, Claude, or Gemini.
4. Copy the AI's BibTeX output and paste it at the bottom of the **`references.bib`** file located inside your output directory (`paper_output/<your-project-name>-modified/references.bib`).
5. Open your output folder in your LaTeX compiler (Overleaf, TeXstudio, etc.) and compile `main.tex`. You are done!

---

## 🛠️ Advanced Customization (Optional JSON Config)

If you want to override the automatic settings (for example, to target specific keywords, adjust paraphrasing aggressiveness, or define custom keys), you can create an optional configuration file:

1. Go to the **`configs/`** folder.
2. Create a JSON file (e.g. `configs/my_custom_paper.json`).
3. Define your custom settings and `topic_citations` mapping:

```json
{
  "project_name": "my_custom_paper",
  "input_dir": "paper_input/MyPaperFolder",
  "tex_file": "paper_input/MyPaperFolder/main.tex",
  "bib_file": "paper_input/MyPaperFolder/references.bib",
  "output_dir": "paper_output/MyPaperFolder-modified",
  "synonym_aggressiveness": 0.60,
  "random_seed": 42,
  "min_sentence_length_for_cite": 50,
  "topic_citations": [
    {
      "keywords": ["catalyst", "reaction", "synthesis"],
      "key": "ref_organic_reaction",
      "topic": "Organic Synthesis and Catalytic Reactions"
    }
  ]
}
```
4. Run the script pointing to your custom config:
   ```bash
   python run.py --config my_custom_paper
   ```
