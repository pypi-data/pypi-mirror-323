# Vastify - Effortlessly Run GPU-Intensive Workloads on vast.ai 🚀

Vastify is a Python library designed to simplify running GPU-heavy workloads on vast.ai instances. With features like decorator-based execution, dynamic code deployment, and smart file management, Vastify allows you to focus on your code while it handles the infrastructure.

## 🌟 Key Features

- **Decorator-Based Execution**: Use a simple decorator to execute your Python functions remotely on vast.ai.
- **Smart Instance Management**: Automatically find and launch GPU instances that match your specifications.
- **Dynamic Code Packaging**: Vastify packages your function, dependencies, and additional files at runtime—no need to bake them into Docker images.
- **Efficient File Management**: Sync large files to the instance efficiently, avoiding redundant transfers.
- **Per-File Optimization**: Transfers only missing or outdated files to the instance.
- **Cost Efficiency**: Instances automatically shut down after a configurable idle time to avoid unnecessary costs.

---

## ⚠️ Important Note
This is an internally used project. Maintenance, support and updates are not guaranteed. Use at your own risk.

## 🛠️ Installation

Install Vastify via PyPI:

```bash
pip install vastify
```

#### Set Up Your Vast.ai API Key

Vastify uses your Vast.ai API key to manage GPU instances. You must set the environment variable `VASTAI_API_KEY` before running your code. Here are multiple ways to do this:

1. **Set it Temporarily in Your Shell**:  
   Run this in your terminal before executing your script:  
   ```bash
   export VASTAI_API_KEY="your_api_key_here"
   ```

2. **Add it to Your Shell Configuration**:  
   Add the following line to your `~/.bashrc` or `~/.zshrc` file for a permanent setup:  
   ```bash
   export VASTAI_API_KEY="your_api_key_here"
   ```  
   Then, reload your shell:  
   ```bash
   source ~/.bashrc
   ```

3. **Use a `.env` File**:  
   Create a `.env` file in your project directory with this content:  
   ```.env
   VASTAI_API_KEY=your_api_key_here
   ```
   Then, use a library like `python-dotenv` to load the variable:  
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

4. **Set it Programmatically**:  
   Set the variable directly in your Python script:  
   ```python
   import os
   os.environ["VASTAI_API_KEY"] = "your_api_key_here"
   ```  


---

## 🚀 Quick Start

### 1. Set Up Your Environment

Before using Vastify:
- Ensure you have a [vast.ai account](https://vast.ai) and API key.
- Optionally, store large files in a supported cloud storage provider.

### 2. Write Your Vastify Function

Annotate your Python function with the `@run_on_vastai` decorator to run it on vast.ai:

```python
from vastify import run_on_vastai

@run_on_vastai(
    gpu_name="RTX_2080_Ti", 
    price=0.5, 
    include_files=["./model.pt", "./config.json"]
)
def train_model():
    import torch
    print("Training a model on a vast.ai instance!")
    # Your GPU-intensive logic here
    # You can even return a value from the function (for example the trained model)
    return trained_model

if __name__ == "__main__":
    # The return value will be transferred back from the remote execution to your local environment automagically
    result = train_model()
```

### 3. Run Your Code

When you call the decorated function:
1. Vastify searches for an available vast.ai instance that matches your specifications.
2. It packages your code, dependencies, and specified files.
3. The function runs on the GPU instance, and the result is returned to your local environment.

---

## ⚙️ Advanced Usage

### Specify GPU Requirements

Customize the instance configuration directly in the decorator:

```python
@run_on_vastai(gpu_name="A100", price=1.0, disk=200, regions=["Europe", "North_America"])
def perform_inference():
    # Perform GPU-intensive inference here
    pass
```

### Include Large Files and Directories

Specify files or directories to be uploaded to the vast.ai instance. Files are transferred individually, ensuring efficiency by skipping files that already exist on the remote instance.

```python
@run_on_vastai(
    gpu_name="RTX_3090", 
    include_files=["/path/to/dataset", "/path/to/model_weights.pt"]
)
def analyze_data():
    # Function logic here
    pass
```

---

## 🏗️ How It Works

### 1. **Dynamic Code Packaging**
Vastify packages:
- Your Python code.
- Dependencies (collected automatically).
- Additional files or directories specified in the `include_files` parameter.

### 2. **Smart File Transfer**
- Uses per-file checks to avoid transferring files that already exist on the instance.
- Files are compressed before transfer and decompressed on the instance.

### 3. **Vast.ai Instance Management**
- Vastify uses your provided API key to find or start a GPU instance that matches your specifications.
- Instances detect inactivity and shut down automatically after a configurable idle time.

---

## 🧰 Requirements

- Python 3.8+
- Vast.ai account with API key
- Paramiko and other Python dependencies (installed automatically with Vastify)

---

## 📖 Documentation

- [Full Documentation](https://yourdocslink.com)
- [Examples](https://yourdocslink.com/examples)
- [API Reference](https://yourdocslink.com/api)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](https://github.com/yourrepo/vastify/blob/main/CONTRIBUTING.md) for guidelines.

---

## 🚨 Troubleshooting

### Common Issues

- **Instance Not Found**:
   - Check if your GPU and memory requirements are too strict.
   - Increase your price cap to include more instances.
   - Expand the `regions` parameter to include more geographical locations.

- **File Transfer Issues**:
   - Ensure the paths in `include_files` are correct and accessible.
   - Verify that remote files are not corrupted by inspecting the remote logs.

- **API Key Issues**:
   - Ensure your vast.ai API key is valid and properly set in the environment.

For further assistance, open an issue on [GitHub](https://github.com/yourrepo/vastify/issues).

