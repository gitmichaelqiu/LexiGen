# LexiGen

[中文版](/translations/README_zh.md)

<div align="center">

![LexiGen Logo](https://github.com/gitmichaelqiu/LexiGen/blob/main/Lexi.png?raw=true)

An AI-powered desktop application for generating educational fill-in-the-blank sentences.

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Powered by Ollama](https://img.shields.io/badge/Powered%20by-Ollama-orange)](https://ollama.com)
[![Release](https://img.shields.io/github/v/release/gitmichaelqiu/LexiGen?color=green)](https://github.com/gitmichaelqiu/LexiGen/releases/)

</div>



https://github.com/user-attachments/assets/b2147a30-ac54-4e58-80f0-9409f6d978c4



## 🎯 Overview

"Lexi" comes from "lexicon".

LexiGen transforms vocabulary practice and language learning by automatically generating contextual fill-in-the-blank sentences. Leveraging Ollama's AI models, it creates engaging educational materials with just a few clicks.

## ✨ Key Features

- **Smart Generation**: AI-powered creation of contextually appropriate sentences
- **Flexible Input**: Support for multiple words and their variations
- **Easy Management**:
  - One-click copying to clipboard
  - Individual and bulk word visibility controls
  - Show/Hide words, regenerate/delete sentences

## 🚀 Quick Start

### Prerequisites

1. Install [Ollama](https://ollama.com)
2. Launch the Ollama app
3. Open the terminal (Windows: press `Windows + R`, then type `cmd`) and install a compatible model (e.g. qwen2.5:3b):
   ```bash
   ollama pull qwen2.5:3b
   ```

### Installation

1. Download LexiGen from the [releases page](https://github.com/yourusername/lexigen/releases)
2. Run the installer for your platform
3. Launch LexiGen
4. Verify Ollama connection using the 'Check Server' button

## 📖 Usage Guide

### Basic Operation

1. Enter target words (comma-separated) in the input field
2. Click "Generate" to create sentences
3. Use visibility controls to show/hide specific words
4. Copy sentences with the "Copy" button
5. Clear all content using "Delete All"

### Advanced Features

- **Bulk Operations**: Use "Show All" / "Hide All" for quick visibility changes
- **Model Selection**: Choose different AI models for varied results
- **Server Monitoring**: Check connection status anytime

## 💡 Best Practices

- Input specific, clear words for better context
- Experiment with different AI models
- Ensure stable internet connection
- Keep Ollama server running
- Use commas to separate multiple words
- Customize the prompt in `prompt.txt`, `{word}` is the placeholder for the target word

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| No sentence generation | Check if Ollama server is running |
| Connection errors | Use 'Check Server' button |
| Slow performance | Verify system resources |
| Model errors | Confirm model installation |

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

LexiGen is open source software licensed under the [GNU General Public License v3.0](LICENSE).

---

<div align="center">
Made for educators and learners

If you like this project, please consider giving me a star ⭐️
</div>
