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

LexiGen 是一款 **开源** 的首字母填空生成器，**零成本** 使用本地 Ollama AI。

## 🤩 功能

### 生成句子

输入单词，逗号分隔:

- 点按"生成"或使用"Ctrl/Cmd + Enter"清空已生成句子并生成新句子
- 点按"添加"或使用"Enter"保留已生成句子并添加新句子

### 显示/隐藏答案

点按"显示/隐藏"，"显示/隐藏全部"或"Ctrl/Cmd + /"以显示/隐藏句子答案

### 重新生成句子

对生成的句子不满意？使用"↻"重新生成

### 句子菜单

点击句子旁的"⋮"以展开菜单，你可以:

- **上移/下移**: 调整句子顺序
- **分析**: 分析单词在句子中的成分作用
- **编辑**: 手动编辑句子
- **指定**: 指定句子的时态/语气, 支持:
  - [现在，过去，将来，过去将来] x [一般时，进行时，完成式，完成进行时]
  - 虚拟语气 [现在, 过去]
  - 条件句 [零条件句, 第一条件句, 第二条件句, 第三条件句]
  - 祈使句

## 🚀 下载安装

### 前置

1. 安装 [Ollama](https://ollama.com)
2. 启动 Ollama 应用程序
3. 打开终端 (Windows：按 `Windows + R`，然后输入 `cmd`)，并安装一个模型 (推荐 `qwen2.5:3b`(质量更高，占用1.3GB) 或 `qwen2.5:0.5b` (模型更小，占用500MB)):

  ```bash
  ollama pull qwen2.5:3b
  ```

### 替代方案: 使用本地GGUF模型

LexiGen 现在支持直接使用本地GGUF模型，无需安装Ollama:

1. 安装Python依赖: `pip install -r requirements.txt`
2. 使用内置模型下载器: `python utils/model_downloader.py --model qwen2.5-3b-instruct`
3. 启动LexiGen并:
   - 将API URL下拉菜单设置为"GGUF Models"（默认选项之一）
   - 从下拉菜单中选择您下载的模型

详细说明请参见 [本地模型指南](docs/LOCAL_MODELS_zh.md).

### 安装

1. 从 [GitHub](https://github.com/gitmichaelqiu/LexiGen/releases/) 或 [蓝奏云盘](https://wwtm.lanzouq.com/b00uyomyxe) (密码：8hpe) 下载
2. 选择您平台的对应版本
3. 启动 LexiGen

注意，云盘的更新可能比较慢，所以优先从 GitHub Releases 中下载。

## 💡 自定义

你可以自定义提示词！查看指南 [自定义提示词](https://gitmichaelqiu.github.io/my-projects/lexigen/customize-prompts-zh/)。

## 📂 文件结构

`LexiGenAssets` 文件夹用于存放所有外部文件：

- `LexiGenAssets/` - 主资源目录
  - `translations/` - 翻译文件（例如 zh_CN.json）
  - `prompt.txt` - 自定义提示模板文件
  - `settings.yaml` - 软件设置

## ⚠️ 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 无法生成句子 | 检查 Ollama 服务器是否正在运行 |
| 连接错误 | 使用"检查服务器"按钮 |
| 生成缓慢 | 检查系统资源或使用更小的模型 `qwen2.5:0.5b` |
| 模型错误 | 确认模型已安装 |

## 🤫 趣事

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
