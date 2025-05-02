# 在LexiGen中使用本地模型

LexiGen现在支持直接使用本地GGUF模型，无需外部API服务器。这个功能允许您：

1. 完全离线运行LexiGen
2. 不安装Ollama也能使用不同模型
3. 使用固定的模型参数获得更一致的结果

## 设置本地模型

### 步骤一：下载GGUF模型

从Hugging Face下载GGUF模型并放置在`LexiGenAssets/models`目录中。

推荐模型：
1. [Qwen2.5-3B-Instruct](https://huggingface.co/TheBloke/Qwen2.5-3B-Instruct-GGUF) (2-3GB)
2. [Phi-3-mini-4k](https://huggingface.co/TheBloke/phi-3-mini-4k-GGUF) (2-3GB)
3. [Llama-3-8B-Instruct](https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF) (4-5GB)

我们推荐使用Q4_K_M量化版本，它在模型质量和内存使用方面有良好的平衡。

### 步骤二：设置LexiGen使用本地模型

1. 安装必需的依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 启动LexiGen：
   ```bash
   python main.py
   ```

3. 在设置面板中，从API URL下拉菜单中选择"GGUF Models"
   - 下拉菜单将显示两个默认选项（Ollama API和GGUF Models）
   - 如果您的设置中有自定义API URL，它也会作为第三个选项显示

4. 模型下拉菜单将自动显示LexiGenAssets/models目录中可用的.gguf文件。选择您想要使用的模型。

5. 首次选择模型时，您会看到一个加载窗口，因为模型正在加载到内存中。根据模型大小，这可能需要几分钟时间。

6. 模型成功加载后，服务器状态应自动显示为"已连接"。

## 故障排除

### 内存要求

GGUF模型需要大量内存才能运行：
- 4GB模型通常需要8-10GB RAM
- 3GB模型通常需要6-8GB RAM

### 常见问题

1. **模型无法加载**：确保您有足够的RAM可用于模型大小
2. **生成速度慢**：模型首次加载到内存中时生成速度较慢
3. **llama-cpp-python导入错误**：尝试重新安装：
   ```bash
   pip uninstall -y llama-cpp-python
   pip install llama-cpp-python
   ```

## 高级配置

对于高级用户，您可以修改`api_service.py`文件来更改模型参数：
- `n_ctx`：上下文长度（默认：2048）
- `max_tokens`：生成的最大令牌数
- 其他参数如temperature、top_p等

## 性能说明

本地模型性能取决于您的硬件：
- 仅CPU：生成速度较慢
- 启用CUDA/ROCm的构建可以利用GPU加速
- 加载模型后的首次生成可能需要更长时间 