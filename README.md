# LexiGen

[中文版](/README_zh.md)

<div align="center">

![LexiGen Logo](https://raw.githubusercontent.com/gitmichaelqiu/LexiGen/refs/heads/main/icons/Lexi.png)

An AI-powered desktop application for generating educational fill-in-the-blank sentences.

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://github.com/gitmichaelqiu/LexiGen/blob/main/LICENSE)
[![Powered by Ollama](https://img.shields.io/badge/Powered%20by-Ollama-orange)](https://ollama.com)
[![Release](https://img.shields.io/github/v/release/gitmichaelqiu/LexiGen?color=green)](https://github.com/gitmichaelqiu/LexiGen/releases/)

</div>

<img width="1318" alt="Screenshot 2025-05-01 at 19 16 55" src="https://github.com/user-attachments/assets/0065f2a2-f1d0-4fa2-8a85-f36ca215c9b8" />

## 🎯 Overview

LexiGen is an **open-source** fill-in-the-blank problems generator using local AI with **Zero Cost**.

## 🤩 Feature

### Generate Sentences

Enter your words:

- Press "Generate" or use "Ctrl/Cmd + Enter" to **clean** the generated sentences and replace them with new ones
- Press "Append" or use "Enter" to append new sentences under the generated ones

### Show/Hide Blanks

Press Show/Hide, Show/Hide All or pressing "Ctrl/Cmd + /" to show/hide blanks in sentences.

### Regenerate Sentences

Not satisfy with the sentences? Press "↻" to regenerate.

### Sentence Menu

Press "⋮" next to the sentences to browse the menu:

- **Move Up/Down**: Move the current sentence upward or downward to order sentences.
- **Analyze**: Pop up a new window to analyze the function of the given word in the sentence
- **Edit**: Edit the sentence by yourself
- **Designate**: Designate a tense/mood to regenerate the sentence, supporting:
  - [Present, Past, Future, Past Future] x [Simple, Continuous, Perfect, Perfect Continuous]
  - Subjunctive Mood [Preeent, Past]
  - Conditional [Zero, First, Second, Third]
  - Imperative Mood

### Export to Word

Want to share the sentence set? Press "Menu -> Export to Word" or "Ctrl/Cmd + E" to export all your sentences to a docx. You can choose to generate analysis.

**Answer Key** will be automatically appended to the last pages of the document.

### Designate Context

Want your sentences generated under a certain context? Press "Context" or "Ctrl/Cmd + T" to add a context to all **New Sentences**. When you close the context window by the keyboard shortcut, the context will be automatically saved.

### Save/Load History

Press "Menu -> Save/Load" or "Ctrl/Cmd + S"/"Ctrl/Cmd + O" to save/load all current data, including words, sentences, analyses, and context to/from an external YAML file.

You can share YAML files with your friends/students/teachers!

## 🚀 Quick Start

### Prerequisites

If you do **NOT** want to download Ollama and use terminal to download models, go to "Alternative: Using Local GGUF Models".

1. Install [Ollama](https://ollama.com)
2. Launch the Ollama app
3. Open the terminal (Windows: press `Windows + R`, then type `cmd`) and install a model (suggesting `qwen2.5:3b` or `qwen2.5:0.5b` (smaller)):

   ```bash
   ollama pull qwen2.5:3b
   ```

### Alternative: Using Local GGUF Models

LexiGen now supports using local GGUF models directly, without requiring Ollama:

1. Download a GGUF model from Hugging Face and place it in the `LexiGenAssets/models` directory
2. Launch LexiGen and:
   - Set the API URL dropdown to "GGUF Models" (one of the default options)
   - Select your downloaded model from the dropdown

"LexiGen_Version_GGUF_System.zip" packages in [Releases]((https://github.com/gitmichaelqiu/LexiGen/releases/)) already contains `qwen2.5-1.5b-instruct-q4_k_m.gguf`, under `Apache 2.0 License`.

### Installation

1. Download LexiGen from the [Releases](https://github.com/gitmichaelqiu/LexiGen/releases/)
2. Run the installer for your platform
3. Launch LexiGen

## Hotkeys

- **Generate**: Shift + Enter
- **Append**: Enter
- **Show/Hide All**: Ctrl/Cmd + /
- **Export to Word**: Ctrl/Cmd + E

## 💡 Customization

You can customize your prompts! Check the guide [Customize Prompts](https://gitmichaelqiu.github.io/my-projects/lexigen/customize-prompts/).

## 📂 File Structure

LexiGen uses a dedicated `LexiGenAssets` folder for all external files:

- `LexiGenAssets/` - The main assets directory
  - `translations/` - Translation files (e.g., zh_CN.json)
  - `prompt.txt` - Custom prompt template file
  - `settings.yaml` - Application settings

This structure separates application code from user data, making it easier to manage and backup your settings.

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| No sentence generation | Check if Ollama server is running |
| Connection errors | Use 'Check Server' button |
| Slow performance | Verify system resources or use a smaller model `qwen2.5:0.5b` |
| Model errors | Confirm model installation |

## 🤫 Fun Facts

"Lexi" comes from "lexicon".

I considered the name "FibGen" (**F**ill **I**n the **B**lank). However, because "fib" means lie, this name was discarded.

## 🤝 Contributing

Contributions are welcome! Here's how you can help under [GNU General Public License v3.0](LICENSE):

- Report bugs in [Issues](https://github.com/gitmichaelqiu/LexiGen/issues)
- Suggest features in [Issues](https://github.com/gitmichaelqiu/LexiGen/issues)
- Post your POV to this project in [Discussions](https://github.com/gitmichaelqiu/LexiGen/discussions)
- Submit pull requests

---

<div align="center">
Made for educators and learners

If you like this project, please consider giving me a star ⭐️

[![Star History Chart](https://api.star-history.com/svg?repos=gitmichaelqiu/LexiGen&type=Date)](https://star-history.com/#gitmichaelqiu/LexiGen&Date)

</div>
