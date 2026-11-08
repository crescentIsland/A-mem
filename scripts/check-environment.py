"""Download runtime resources and verify setup without calling an LLM API."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('HF_HOME', str(ROOT / '.cache' / 'huggingface'))
os.environ.setdefault('NLTK_DATA', str(ROOT / '.cache' / 'nltk_data'))
# This machine uses a configured proxy for the official NLTK resource host.
os.environ.setdefault('NLTK_ALLOW_PROXIED_URLOPEN', '1')
sys.path.insert(0, str(ROOT))

import nltk
import torch
from sentence_transformers import SentenceTransformer
from load_dataset import load_locomo_dataset

print('Python:', sys.version.split()[0], flush=True)
print('Torch:', torch.__version__, 'CUDA available:', torch.cuda.is_available(), flush=True)
for resource in ('punkt', 'punkt_tab', 'wordnet', 'omw-1.4'):
    if not nltk.download(resource, download_dir=os.environ['NLTK_DATA'], quiet=True):
        raise RuntimeError(f'Could not download NLTK resource: {resource}')
print('NLTK resources ready', flush=True)
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(['A-MEM environment check', 'Agentic memory retrieval'])
if embeddings.shape != (2, 384):
    raise RuntimeError(f'Unexpected embedding shape: {embeddings.shape}')
print('Embedding check:', embeddings.shape, flush=True)
samples = load_locomo_dataset(str(ROOT / 'data' / 'locomo10.json'))
if len(samples) != 10:
    raise RuntimeError(f'Unexpected conversation count: {len(samples)}')
print('Dataset:', len(samples), 'conversations,', sum(len(x.qa) for x in samples), 'questions', flush=True)
import memory_layer
import memory_layer_robust
import llm_text_parsers
print('Memory module imports OK; no LLM API calls made.', flush=True)
