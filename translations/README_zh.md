# LexiGen

<div align="center">

![LexiGen Logo](https://github.com/gitmichaelqiu/LexiGen/blob/main/Lexi.png?raw=true)

专注于利用本地 Ollama AI 模型的首字母填空生成器

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Powered by Ollama](https://img.shields.io/badge/Powered%20by-Ollama-orange)](https://ollama.com)
[![Release](https://img.shields.io/github/v/release/gitmichaelqiu/LexiGen?color=green)](https://github.com/gitmichaelqiu/LexiGen/releases/)

</div>

## 🎯 概述

LexiGen 是一款完全免费的首字母填空生成器，专为教育工作者和学生设计。通过本地 Ollama AI，只需点击几下即可创建首字母填空题目

## 📥 下载

- [GitHub Releases](https://github.com/gitmichaelqiu/LexiGen/releases)
- 国内用户推荐：[蓝奏云盘](https://wwtm.lanzouq.com/b00uyomyxe) (密码：8hpe)

## ✨ 主要特点

- **智能生成**：基于 Ollama AI 创建上下文恰当的句子
- **灵活输入**：支持多个单词及其变体形式
- **便捷管理**：
  - 一键复制到剪贴板
  - 单个和批量单词可见性控制
  - 显示/隐藏单词，重新生成/删除句子

## 🚀 快速开始

### 前置要求

1. 安装 [Ollama](https://ollama.com)
2. 启动 Ollama 应用程序
3. 打开终端（Windows：按 `Windows + R`，然后输入 `cmd`）并安装推荐模型：
   ```bash
   ollama pull qwen2.5:3b
   ```

### 模型选择指南

- 推荐模型：qwen2.5:3b（大小约1.9GB）
- 选择标准：模型大小应小于电脑内存/显存
- 示例：8GB内存的电脑完全可以运行 qwen2.5:3b 模型
- 可在 Ollama 中自行选择其他生成模型

### 安装步骤

1. 从上述下载链接获取最新版本
2. 运行适合您平台的安装程序
3. 启动 LexiGen
4. 使用"检查服务器"按钮验证 Ollama 连接

## 📖 使用指南

### 基本操作

1. 在输入框中输入目标单词（用逗号分隔）
2. 点击"生成"创建句子
3. 使用"显示/隐藏"按钮显示/隐藏特定单词
4. 使用"复制"按钮复制句子
5. 使用"全部删除"清除所有内容

## ⚠️ 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 无法生成句子 | 检查 Ollama 服务器是否正在运行 |
| 连接错误 | 使用"检查服务器"按钮 |
| 性能缓慢 | 检查系统资源 |
| 模型错误 | 确认模型已安装 |
| 安装或运行异常 | 可能是环境缺失，请联系开发者解决 |

## 🤝 参与贡献

欢迎参与改进 LexiGen！您可以：

- 在 GitHub 上提交 Issues 报告问题
- 发起 Pull Request 贡献代码
- 在遵循 GNU GPL3.0 协议的前提下创建自己的发行版
- 改进文档或提出建议

---

<div align="center">
为教育工作者和学习者而制作

如果这个项目对您有帮助，请考虑给 LexiGen 一个星标 ⭐️

感谢您对 LexiGen 的支持！

— [@gitmichaelqiu](https://github.com/gitmichaelqiu)
</div> 