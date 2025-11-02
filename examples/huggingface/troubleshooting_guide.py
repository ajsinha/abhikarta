"""
================================================================================
Hugging Face Models - Troubleshooting Guide
================================================================================

Copyright 2025-2030 All Rights Reserved
Author: Ashutosh Sinha
Email: ajsinha@gmail.com

================================================================================

This guide helps you resolve common issues when working with Hugging Face models.
"""

# ============================================================================
# COMMON ERRORS AND SOLUTIONS
# ============================================================================

"""
ERROR 1: Out of Memory (CUDA OOM)
================================================================================

Error Message:
    RuntimeError: CUDA out of memory. Tried to allocate X.XX GB

Causes:
    - Model too large for available GPU memory
    - Batch size too large
    - Accumulating gradients without clearing

Solutions:

1. Use 8-bit Quantization (reduces memory by 75%):
    
    from transformers import BitsAndBytesConfig
    
    config = BitsAndBytesConfig(load_in_8bit=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=config,
        device_map="auto"
    )

2. Use 4-bit Quantization (even more memory savings):
    
    config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16
    )

3. Reduce Batch Size:
    
    # Instead of batch_size=16
    generator(texts, batch_size=4)

4. Use Gradient Checkpointing:
    
    model.gradient_checkpointing_enable()

5. Clear CUDA Cache:
    
    import torch
    torch.cuda.empty_cache()

6. Use Smaller Model:
    - Llama-2-7b instead of Llama-2-13b
    - distilbert instead of bert-base
    - t5-small instead of t5-base
"""

"""
ERROR 2: Authentication/Access Denied
================================================================================

Error Message:
    HTTPError: 401 Client Error: Unauthorized
    GatedRepoError: Access to model X is restricted

Causes:
    - Not logged into Hugging Face
    - Haven't accepted model license
    - Invalid or expired token

Solutions:

1. Login to Hugging Face:
    
    # Method 1: Command line
    huggingface-cli login
    
    # Method 2: Python
    from huggingface_hub import login
    login(token="your_token_here")
    
    # Method 3: Environment variable
    export HUGGINGFACE_TOKEN="your_token_here"

2. Accept Model License:
    
    Visit the model page and click "Agree and access repository":
    - Llama 2: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
    - Llama 3: https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
    - CodeLlama: https://huggingface.co/codellama/CodeLlama-7b-Instruct-hf

3. Create Access Token:
    
    Go to: https://huggingface.co/settings/tokens
    Create new token with "Read" access

4. Verify Authentication:
    
    from huggingface_hub import HfFolder
    token = HfFolder.get_token()
    print(f"Token: {'Found' if token else 'Not found'}")
"""

"""
ERROR 3: Import Errors
================================================================================

Error Message:
    ModuleNotFoundError: No module named 'transformers'
    ImportError: cannot import name 'X' from 'transformers'

Solutions:

1. Install/Update Transformers:
    
    pip install --upgrade transformers

2. Install All Dependencies:
    
    pip install transformers torch accelerate
    pip install bitsandbytes sentencepiece protobuf

3. Check Python Version:
    
    python --version  # Should be 3.8 or higher

4. Virtual Environment:
    
    # Create new environment
    python -m venv hf_env
    source hf_env/bin/activate  # On Windows: hf_env\\Scripts\\activate
    pip install -r requirements.txt

5. Clear pip Cache:
    
    pip cache purge
    pip install --no-cache-dir transformers
"""

"""
ERROR 4: Slow Inference/Generation
================================================================================

Symptoms:
    - Generation takes several minutes
    - CPU usage at 100%
    - System freezing

Solutions:

1. Use GPU:
    
    # Check GPU availability
    import torch
    print(torch.cuda.is_available())
    
    # Force GPU usage
    model = model.to("cuda")
    # or use device_map="auto"

2. Install CUDA-enabled PyTorch:
    
    # For CUDA 11.8
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
    
    # For CUDA 12.1
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

3. Use Smaller Models:
    
    # Instead of bert-large
    model = "distilbert-base-uncased"  # 40% faster

4. Reduce max_length:
    
    # Instead of max_length=512
    outputs = model.generate(max_new_tokens=100)

5. Use Batch Processing:
    
    results = classifier(texts, batch_size=8)

6. Enable TensorFloat32 (on Ampere GPUs):
    
    torch.backends.cuda.matmul.allow_tf32 = True
"""

"""
ERROR 5: Model Not Found
================================================================================

Error Message:
    OSError: Model 'X' not found
    RepositoryNotFoundError

Solutions:

1. Check Model Name:
    
    # Correct format: "organization/model-name"
    ✓ "meta-llama/Llama-2-7b-chat-hf"
    ✗ "llama-2-7b-chat"

2. Search Hugging Face Hub:
    
    Visit: https://huggingface.co/models
    Search for the model

3. Check Model Availability:
    
    from huggingface_hub import model_info
    info = model_info("model-name")
    print(info)

4. Use Alternative Model:
    
    # If model removed/renamed
    # Similar models:
    - "gpt2" → "gpt2-medium" or "gpt2-large"
    - "bert-base-uncased" → "roberta-base"
"""

"""
ERROR 6: Connection/Download Errors
================================================================================

Error Message:
    requests.exceptions.ConnectionError
    OSError: We couldn't connect to 'https://huggingface.co'

Solutions:

1. Check Internet Connection:
    
    ping huggingface.co

2. Use Proxy:
    
    export HTTP_PROXY="http://proxy.example.com:8080"
    export HTTPS_PROXY="http://proxy.example.com:8080"

3. Download Model Manually:
    
    from huggingface_hub import snapshot_download
    snapshot_download(
        "model-name",
        cache_dir="./models"
    )

4. Use Offline Mode:
    
    from transformers import AutoModel
    model = AutoModel.from_pretrained(
        "model-name",
        local_files_only=True,
        cache_dir="./models"
    )

5. Increase Timeout:
    
    from huggingface_hub import HfFolder
    HfFolder.save_token_timeout(600)  # 10 minutes
"""

"""
ERROR 7: Token Mismatch/Encoding Errors
================================================================================

Error Message:
    ValueError: Asking to pad but the tokenizer does not have a padding token
    KeyError: 'token_type_ids'

Solutions:

1. Set Padding Token:
    
    tokenizer.pad_token = tokenizer.eos_token
    # or
    tokenizer.padding_side = "left"

2. Add Padding:
    
    inputs = tokenizer(
        text,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

3. Handle Missing Keys:
    
    # Don't assume token_type_ids exists
    outputs = model(**{k: v for k, v in inputs.items() if k in model.forward.__code__.co_varnames})
"""

"""
ERROR 8: Generation Issues
================================================================================

Symptoms:
    - Repetitive output
    - Nonsensical text
    - Incomplete generation

Solutions:

1. Adjust Generation Parameters:
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.7,          # 0.1-1.0, higher = more creative
        top_p=0.9,                # Nucleus sampling
        top_k=50,                 # Top-k sampling
        repetition_penalty=1.2,   # Penalize repetition
        do_sample=True,           # Enable sampling
        no_repeat_ngram_size=3    # Prevent n-gram repetition
    )

2. Use Proper Prompt Format:
    
    # For Llama 2 chat
    prompt = f"<s>[INST] {user_message} [/INST]"
    
    # For Llama 3
    messages = [
        {"role": "user", "content": user_message}
    ]
    inputs = tokenizer.apply_chat_template(messages, return_tensors="pt")

3. Set Stopping Criteria:
    
    from transformers import StoppingCriteria
    
    class StopOnTokens(StoppingCriteria):
        def __call__(self, input_ids, scores, **kwargs):
            stop_ids = [tokenizer.eos_token_id]
            return input_ids[0][-1] in stop_ids
"""

"""
ERROR 9: Version Conflicts
================================================================================

Error Message:
    AttributeError: module 'transformers' has no attribute 'X'
    TypeError: __init__() got an unexpected keyword argument 'X'

Solutions:

1. Update All Packages:
    
    pip install --upgrade transformers torch accelerate

2. Check Versions:
    
    import transformers
    import torch
    print(f"Transformers: {transformers.__version__}")
    print(f"PyTorch: {torch.__version__}")

3. Use Compatible Versions:
    
    # requirements.txt
    transformers==4.35.0
    torch==2.0.1
    accelerate==0.24.1

4. Clean Install:
    
    pip uninstall transformers torch accelerate
    pip install transformers torch accelerate
"""

"""
ERROR 10: Permission/File Access Errors
================================================================================

Error Message:
    PermissionError: [Errno 13] Permission denied
    OSError: [Errno 28] No space left on device

Solutions:

1. Check Disk Space:
    
    df -h  # On Unix/Linux
    # Models can be 10-50GB each

2. Change Cache Directory:
    
    import os
    os.environ['TRANSFORMERS_CACHE'] = '/path/to/cache'
    os.environ['HF_HOME'] = '/path/to/cache'

3. Clear Cache:
    
    # Location: ~/.cache/huggingface
    rm -rf ~/.cache/huggingface/hub
    
    # Or in Python:
    from huggingface_hub import scan_cache_dir
    scan_cache_dir().delete_revisions("revision-hash")

4. Run with Proper Permissions:
    
    sudo chmod -R 755 /path/to/cache
"""

# ============================================================================
# DEBUGGING TIPS
# ============================================================================

"""
GENERAL DEBUGGING STRATEGIES
================================================================================

1. Enable Verbose Logging:
    
    import logging
    logging.basicConfig(level=logging.INFO)
    
    import transformers
    transformers.logging.set_verbosity_info()

2. Check System Info:
    
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Device count: {torch.cuda.device_count()}")
    
    if torch.cuda.is_available():
        print(f"Device name: {torch.cuda.get_device_name(0)}")
        print(f"Memory allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
        print(f"Memory cached: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")

3. Test with Smaller Model First:
    
    # Test pipeline with small model
    test = pipeline("text-generation", model="distilgpt2")
    print(test("Hello"))

4. Isolate the Problem:
    
    # Test each component separately
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("Tokenizer loaded ✓")
    
    model = AutoModel.from_pretrained(model_name)
    print("Model loaded ✓")
    
    inputs = tokenizer("test", return_tensors="pt")
    print("Tokenization works ✓")
    
    outputs = model(**inputs)
    print("Inference works ✓")

5. Check Model Card:
    
    # Visit model page for specific requirements
    # https://huggingface.co/[model-name]
    # Check "Files and versions" for model size
    # Check "Model card" for usage instructions
"""

# ============================================================================
# PERFORMANCE OPTIMIZATION
# ============================================================================

"""
OPTIMIZATION CHECKLIST
================================================================================

✓ Use GPU (if available)
✓ Enable mixed precision (fp16)
✓ Use quantization (8-bit or 4-bit)
✓ Batch processing
✓ Reduce max_length
✓ Use gradient checkpointing
✓ Enable TensorFloat32 (Ampere GPUs)
✓ Use smaller models
✓ Cache repeated computations
✓ Use pipeline API when possible

Example Optimized Setup:

from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# Configuration
config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0
)

# Load model
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    quantization_config=config,
    device_map="auto",
    torch_dtype=torch.float16,
    token=True
)

# Enable optimizations
if torch.cuda.is_available():
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

# Use with batching
texts = ["prompt 1", "prompt 2", "prompt 3"]
for text in texts:
    # Process in batch
    pass
"""

# ============================================================================
# GETTING HELP
# ============================================================================

"""
WHERE TO GET HELP
================================================================================

1. Official Documentation:
   - Transformers: https://huggingface.co/docs/transformers
   - Hub: https://huggingface.co/docs/hub

2. Community:
   - Forum: https://discuss.huggingface.co
   - Discord: https://discord.com/invite/hugging-face

3. GitHub Issues:
   - https://github.com/huggingface/transformers/issues

4. Stack Overflow:
   - Tag: [huggingface-transformers]

5. Model-Specific Issues:
   - Check model card: https://huggingface.co/[model-name]
   - Check model discussions tab

When Asking for Help, Include:
- Python version
- transformers version
- torch version
- CUDA version (if using GPU)
- Complete error traceback
- Minimal reproducible example
- What you've already tried

Contact:
Email: ajsinha@gmail.com
"""

print("""
================================================================================
TROUBLESHOOTING GUIDE LOADED
================================================================================

This module contains solutions to common issues. Import it for reference:

    import troubleshooting_guide
    
Or read the docstrings for specific errors.

Copyright 2025-2030 - Ashutosh Sinha (ajsinha@gmail.com)
================================================================================
""")
