# LexiGen

<div align="center">

![LexiGen Logo](https://raw.githubusercontent.com/gitmichaelqiu/LexiGen/refs/heads/main/icons/Lexi.png)

基于人工智能的首字母填空生成器。

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://github.com/gitmichaelqiu/LexiGen/blob/main/LICENSE)
[![Powered by Ollama](https://img.shields.io/badge/Powered%20by-Ollama-orange)](https://ollama.com)
[![Release](https://img.shields.io/github/v/release/gitmichaelqiu/LexiGen?color=green)](https://github.com/gitmichaelqiu/LexiGen/releases/)

</div>



<img width="1318" alt="Screenshot 2025-04-16 at 21 32 15" src="https://github.com/user-attachments/assets/c85c0ce1-dd8f-40f0-975a-e581a5968373" />



## 🎯 概述

LexiGen 是一款 **开源** 的首字母填空生成器，**零成本** 使用本地 Ollama AI生成。

## 🚀 下载安装

### 前置

1. 安装 [Ollama](https://ollama.com)
2. 启动 Ollama 应用程序
3. 打开终端（Windows：按 `Windows + R`，然后输入 `cmd`），并安装一个模型（推荐 `qwen2.5:3b` 或 `qwen2.5:0.5b`（模型更小）：

  ```bash
  ollama pull qwen2.5:3b
  ```

### 安装

1. 从 [GitHub](https://github.com/yourusername/lexigen/releases) 或 [蓝奏云盘](https://wwtm.lanzouq.com/b00uyomyxe) (密码：8hpe) 下载
2. 选择您平台的对应版本
3. 启动 LexiGen

## 💡 自定义

- 自定义 `LexiGenAssets/prompt.txt` 中的prompt，`{word}` 是您输入单词的占位符

## 📂 文件结构

`LexiGenAssets` 文件夹用于存放所有外部文件：

- `LexiGenAssets/` - 主资源目录
  - `translations/` - 翻译文件（例如 zh_CN.json）
  - `prompt.txt` - 自定义提示模板文件
  - `settings.json` - 软件设置

## ⚠️ 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 无法生成句子 | 检查 Ollama 服务器是否正在运行 |
| 连接错误 | 使用“检查服务器”按钮 |
| 生成缓慢 | 检查系统资源或使用更小的模型 `qwen2.5:0.5b` |
| 模型错误 | 确认模型已安装 |

## 🤩 趣事

"Lexi" 来源于 "lexicon"（词典）。

我曾考虑过 "FibGen" 的名字 (**F**ill **I**n the **B**lank)，但因为 "fib" 意为谎言，名字被替换为 "LexiGen"。

## 🤝 贡献

欢迎您的贡献！以下是您可以帮助的方式，请遵循 [GNU 通用公共许可证 v3.0](LICENSE)：

- 在 [Issues](https://github.com/gitmichaelqiu/LexiGen/issues) 中报告错误
- 在 [Issues](https://github.com/gitmichaelqiu/LexiGen/issues) 中提出功能建议
- 提交 Pull Request

---

<div align="center">

如果您喜欢这个项目，请考虑给我一颗星，这对我意义重大 ⭐️

[![Star History Chart](https://api.star-history.com/svg?repos=gitmichaelqiu/LexiGen&type=Date)](https://star-history.com/#gitmichaelqiu/LexiGen&Date)

</div>
