# AI Prompting Guide — Step-by-Step Workflow

Follow these simple, step-by-step instructions to automatically resolve the placeholder citations in your processed document using AI.

---

### Step 1: Run the Similarity Reduction Tool
Run the pipeline to process your paper. This automatically scans your LaTeX file, applies rewrites, inserts citations, and creates your output folder.
```bash
python run.py --config math_thesis
```
*(Replace `math_thesis` with your specific configuration name if processing a different paper).*

---

### Step 2: Open your Pre-Filled AI Prompt
1. Navigate to your output directory: **`paper_output/<your-project-modified>/`**.
2. Open the file named **`ai_prompt.txt`**.
3. **Copy the entire text** inside this file. 
   *(This prompt is generated automatically by Python and is already pre-filled with your document's specific citation keys and topics, so you don't have to write or format anything manually).*

---

### Step 3: Query the AI Assistant
1. Open ChatGPT, Claude, or Gemini.
2. Paste the copied text directly into the chat and submit.
3. The AI will output a set of real, highly-cited academic references formatted as valid BibTeX entries, matching your document's keys exactly.

---

### Step 4: Update your Bibliography
1. Open the file **`references.bib`** inside your output directory:
   📂 `paper_output/<your-project-modified>/references.bib`
2. Scroll to the very bottom to find the placeholder entries (under the `% DUMMY REFERENCES` header).
3. **Highlight and delete** the placeholder entries, and **paste** the real BibTeX entries provided by the AI in their place.
4. **Save** the file.

---

### Step 5: Compile your Document
1. Upload/open the **`paper_output/<your-project-modified>/`** folder in your LaTeX editor (e.g., Overleaf, TeXpage, TeXstudio).
2. Open `main.tex` and compile. All citations will now successfully render and link to real scientific papers.

---

## 📋 Example of what `ai_prompt.txt` contains:
```text
I am using a LaTeX similarity reduction tool. It has generated several dummy placeholder BibTeX citations in my document. I need you to find real, highly-cited, relevant academic papers (journal articles, books, or conference papers) that match these topics, and format them as valid BibTeX entries.

For each topic, provide a real academic source. You MUST keep the exact BibTeX key I provide so that it matches my LaTeX file.

Here is the list of citation keys and the academic topics they should cover:

1. Key: ref_thermal_modeling
   Topic: Heat Conduction and Thermal Diffusion Modeling
2. Key: ref_wave_propagation
   Topic: Wave Propagation and Vibration Analysis
...

Please ensure:
- The BibTeX citation key matches my key EXACTLY (e.g., ref_thermal_modeling).
- The papers are real, published, and highly cited (articles or textbooks).
- The output is strictly formatted as valid BibTeX.
```
