import os
import argparse
import requests
import tqdm
from models.config import get_assets_path

def download_file(url, destination):
    """
    Download a file from a URL with progress bar
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    
    # Download with progress bar
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    
    with open(destination, 'wb') as f, tqdm.tqdm(
        total=file_size, unit='iB', unit_scale=True, 
        desc=f"Downloading {os.path.basename(destination)}"
    ) as progress_bar:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)
    
    return destination

def main():
    # Define available models
    MODELS = {
        "qwen2.5-3b-instruct": {
            "url": "https://huggingface.co/TheBloke/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct.q4_k_m.gguf",
            "size": "2.0 GB"
        },
        "phi-3-mini-4k": {
            "url": "https://huggingface.co/TheBloke/phi-3-mini-4k-GGUF/resolve/main/phi-3-mini-4k.Q4_K_M.gguf",
            "size": "2.6 GB"
        },
        "llama3-8b-instruct": {
            "url": "https://huggingface.co/TheBloke/Llama-3-8B-Instruct-GGUF/resolve/main/llama-3-8b-instruct.Q4_K_M.gguf",
            "size": "4.7 GB"
        },
    }
    
    parser = argparse.ArgumentParser(description="Download GGUF models for LexiGen")
    parser.add_argument("--model", choices=list(MODELS.keys()), help="Model to download")
    parser.add_argument("--list", action="store_true", help="List available models")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available models:")
        for model, info in MODELS.items():
            print(f"  - {model} ({info['size']})")
        return
    
    if not args.model:
        parser.print_help()
        return
    
    model_info = MODELS[args.model]
    model_url = model_info["url"]
    model_filename = os.path.basename(model_url)
    
    # Get the models directory
    models_dir = os.path.join(get_assets_path(), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    destination = os.path.join(models_dir, model_filename)
    
    # Check if the file already exists
    if os.path.exists(destination):
        print(f"Model {model_filename} already exists. Skipping download.")
        return
    
    # Download the model
    print(f"Downloading {args.model} model ({model_info['size']})...")
    download_file(model_url, destination)
    print(f"Model downloaded to {destination}")
    print(f"You can now select this model in LexiGen settings: {model_filename}")

if __name__ == "__main__":
    main() 