import os
os.environ["HF_TOKEN"] = "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"
from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-27b-it", add_bos_token=False)

print(tokenizer.apply_chat_template([{"role": "user", "content": "123"}], tokenize=False))

print(tokenizer.eos_token)