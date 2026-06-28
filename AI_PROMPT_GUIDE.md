# AI Prompting Guide — Resolving Dummy References

When Turnitout processes your LaTeX document, it inserts new citations to resolve Turnitin's "Not Cited or Quoted" matches. These citations use placeholder keys (e.g., `ref_thermal_modeling`) and generate a `dummy_references.bib` file.

To compile your document, you need to replace these dummy placeholder entries with **real, valid academic references**.

---

## ⚡ The Automated Shortcut

To put less load on manual work, the program automatically generates a **pre-filled AI prompt** tailored specifically to the placeholders used in your run.

1. Open the generated output folder: `paper_output/Mathematics-thesis-modified/` (or your specific project folder).
2. Open the file **`ai_prompt.txt`**.
3. **Copy the entire contents of `ai_prompt.txt`** and paste it directly into ChatGPT, Claude, or Gemini.

---

## 📋 What the Generated Prompt Looks Like

The generated `ai_prompt.txt` file is pre-populated and formatted as follows:

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

---

## 🔄 How to Apply the Results

Once the AI generates the BibTeX entries for you:

1. **Open the `references.bib` file** in your output folder (`paper_output/Mathematics-thesis-modified/references.bib`).
2. Scroll to the bottom where the dummy references (prefixed with `% DUMMY REFERENCES`) were automatically appended.
3. **Select and replace** those placeholder entries with the real BibTeX code provided by the AI.
4. **Save** the file.
5. Hitting compile on your LaTeX project will now link these real citations successfully.

---

## 💡 Pro-Tip for Finding Papers Directly
If you want to choose specific papers yourself, search **Google Scholar** for the topic, click the **"Cite"** button (quotation marks icon) under the search result, select **"BibTeX"**, copy the code block, and change the key (e.g. `@article{author2020...,`) to match the placeholder key (e.g. `@article{ref_thermal_modeling,`).
