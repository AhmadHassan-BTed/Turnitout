# AI Prompting Guide — Resolving Dummy References

When Turnitout processes your LaTeX document, it inserts new citations to resolve Turnitin's "Not Cited or Quoted" matches. These citations use placeholder keys (e.g., `ref_thermal_modeling`) and generate a `dummy_references.bib` file.

To compile your document, you need to replace these dummy placeholder entries with **real, valid academic references**.

This guide provides a copy-pasteable AI prompt template to help you generate these BibTeX entries instantly using ChatGPT, Claude, or Gemini.

---

## 📋 The Copy-Paste AI Prompt

Copy the block below, fill in the list of keys and topics from your generated `dummy_references.bib`, and paste it into your AI assistant:

```text
I am using a LaTeX similarity reduction tool. It has generated several dummy placeholder BibTeX citations in my document. I need you to find real, highly-cited, relevant academic papers (journal articles, books, or conference papers) that match these topics, and format them as valid BibTeX entries.

For each topic, provide a real academic source. You MUST keep the exact BibTeX key I provide so that it matches my LaTeX file.

Here is the list of citation keys and the academic topics they should cover:

[PASTE YOUR KEYS AND TOPICS HERE - EXAMPLE:]
1. Key: ref_thermal_modeling
   Topic: Heat Conduction and Thermal Diffusion Modeling
2. Key: ref_wave_propagation
   Topic: Wave Propagation and Vibration Analysis
3. Key: ref_option_pricing
   Topic: Option Pricing and Financial Derivative Models

Please ensure:
- The BibTeX citation key matches my key EXACTLY (e.g., ref_thermal_modeling).
- The papers are real, published, and highly cited (articles or textbooks).
- The output is strictly formatted as valid BibTeX.
```

---

## 🔄 How to Apply the Results

Once the AI generates the BibTeX entries for you:

1. **Open your project folder** (e.g. `paper_output/Mathematics-thesis-modified/`).
2. **Open the `references.bib` file** in your text editor.
3. Scroll to the bottom where the dummy references (prefixed with `% DUMMY REFERENCES`) were automatically appended.
4. **Select and replace** those placeholder entries with the real BibTeX code provided by the AI.
5. **Save** the file.
6. Hitting compile on your LaTeX project will now link these real citations.

---

## 💡 Pro-Tip for Finding Papers Directly
If you want to choose specific papers yourself, search **Google Scholar** for the topic, click the **"Cite"** button (quotation marks icon) under the search result, select **"BibTeX"**, copy the code block, and change the key (e.g. `@article{author2020...,`) to match the placeholder key (e.g. `@article{ref_thermal_modeling,`).
