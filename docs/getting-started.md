# Getting Started Guide: Turnitout

This guide outlines how to use the Turnitout application to process documents, configure rules, and manage citation overlays.

---

## Accessing the Hosted Application

The production version of Turnitout is hosted as a web service. You can access it at:
[https://turnitout.streamlit.app/](https://turnitout.streamlit.app/)

The hosted application is proprietary and closed-source. It provides a graphical interface where you can upload documents, configure settings, and retrieve similarity-reduced outputs.

---

## The Processing Workflow

Turnitout requires zero local setup. You can process text or full documents using the web interface:

### Step 1: Upload or Paste Your Input
* **Text Mode**: Paste raw text fragments directly into the text editor. The system will automatically detect the input format and separate prose from code or mathematical notations.
* **Document Mode**: Upload `.docx` Word Documents. The system processes paragraphs, tables, and headers while maintaining styles (such as bold, italics, font structures, and hyperlinked elements).

### Step 2: Configure Processing Options
Adjust settings in the interface to align the output with your preferences:
* **Aggressiveness Slider**: Controls the probability of word substitutions and structural adjustments.
* **Style Presets**: Toggle between academic-focused restructuring or conversational phrasing.
* **Advanced Options**: Enable or disable specific transformation layers (e.g. active/passive voice transformation, clause splitting, nominalization, or appositive injection).

### Step 3: Download the Output and Appended References
* After processing, download the modified document.
* If citation mapping is enabled, the system will append necessary references to your bibliography list and export a template file to resolve missing references using external tools.

---

## Concept Customizations

Advanced parameters are defined via environment presets inside the system:

* **Random Seed**: Ensures reproducibility of synonym selections and structural transforms.
* **Citation Threshold**: Determines the minimum sentence length required before an inline citation can be appended.
* **Topic Mapping**: Triggers specific citation insertions based on key scientific terminology.
