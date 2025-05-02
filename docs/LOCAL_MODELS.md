# Using Local Models in LexiGen

LexiGen now supports using local GGUF models directly, eliminating the need for an external API server. This feature allows you to:

1. Run LexiGen completely offline
2. Use different models without installing Ollama
3. Get more consistent results with fixed model parameters

## Setting Up Local Models

### Step 1: Download a GGUF Model

Download GGUF models from Hugging Face and place them in the `LexiGenAssets/models` directory.

Recommended models:
1. [Qwen2.5-3B-Instruct](https://huggingface.co/TheBloke/Qwen2.5-3B-Instruct-GGUF) (2-3GB)
2. [Phi-3-mini-4k](https://huggingface.co/TheBloke/phi-3-mini-4k-GGUF) (2-3GB)
3. [Llama-3-8B-Instruct](https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF) (4-5GB)

We recommend using the Q4_K_M quantization for a good balance of model quality and memory usage.

### Step 2: Set Up LexiGen to Use Local Models

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Launch LexiGen:
   ```bash
   python main.py
   ```

3. In the Settings panel, select "GGUF Models" from the API URL dropdown
   - The dropdown will show the two default options (Ollama API and GGUF Models)
   - If you have a custom API URL in your settings, it will also be shown as a third option

4. The model dropdown will automatically show available .gguf files from your LexiGenAssets/models directory. Select the model you want to use.

5. The first time you select a model, you'll see a loading window as the model is loaded into memory. This may take a few moments depending on the model size.

6. The Server Status should automatically show "Connected" when the model is loaded successfully.

## Troubleshooting

### Memory Requirements

GGUF models require significant memory to run:
- 4GB models typically need 8-10GB RAM
- 3GB models typically need 6-8GB RAM

### Common Issues

1. **Model fails to load**: Ensure you have enough RAM available for the model size
2. **Slow generation**: First generation with a model is slow as it loads into memory
3. **Import error for llama-cpp-python**: Try reinstalling with:
   ```bash
   pip uninstall -y llama-cpp-python
   pip install llama-cpp-python
   ```

## Advanced Configuration

For advanced users, you can modify the `api_service.py` file to change model parameters:
- `n_ctx`: Context length (default: 2048)
- `max_tokens`: Maximum tokens to generate
- Other parameters like temperature, top_p, etc.

## Notes on Performance

Local model performance depends on your hardware:
- CPU only: Generation will be slower
- CUDA/ROCm enabled builds can utilize GPU acceleration
- First generation after loading a model may take longer 