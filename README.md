# LexiGen

[中文版](/LexiGenAssets/translations/README_zh.md)

<div align="center">

![LexiGen Logo](https://raw.githubusercontent.com/gitmichaelqiu/LexiGen/refs/heads/main/icons/Lexi.png)

An AI-powered desktop application for generating educational fill-in-the-blank sentences.

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://github.com/gitmichaelqiu/LexiGen/blob/main/LICENSE)
[![Powered by Ollama](https://img.shields.io/badge/Powered%20by-Ollama-orange)](https://ollama.com)
[![Release](https://img.shields.io/github/v/release/gitmichaelqiu/LexiGen?color=green)](https://github.com/gitmichaelqiu/LexiGen/releases/)

</div>


<img width="1318" alt="Screenshot 2025-04-16 at 21 32 15" src="https://github.com/user-attachments/assets/c85c0ce1-dd8f-40f0-975a-e581a5968373" />


## 🎯 Overview

LexiGen is an **open-source** fill-in-the-blank problems generator using local AI with **Zero Cost**.

## 🚀 Quick Start

### Prerequisites

1. Install [Ollama](https://ollama.com)
2. Launch the Ollama app
3. Open the terminal (Windows: press `Windows + R`, then type `cmd`) and install a model (suggesting `qwen2.5:3b` or `qwen2.5:0.5b` (smaller)):

   ```bash
   ollama pull qwen2.5:3b
   ```

### Installation

1. Download LexiGen from the [releases page](https://github.com/gitmichaelqiu/LexiGen/releases/)
2. Run the installer for your platform
3. Launch LexiGen

## 💡 Best Practices

- Customize the prompt in `LexiGenAssets/prompt.txt`, `{word}` is the placeholder for the target word

## 📂 File Structure

LexiGen now uses a dedicated `LexiGenAssets` folder for all external files:

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

## 🤩 Fun Facts

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
