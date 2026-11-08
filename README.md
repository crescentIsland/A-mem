# Agentic Memory 🧠

## FTEC5660 reproduction — Project No. 9

This fork studies how answer-stage retrieval quantity affects A-MEM QA quality and token usage. Three paired rounds compare k=10 with k=5 using DeepSeek Flash, the same 419-note memory and the same 199 LoCoMo questions. These are partial reproduction results under a different model and evaluation setup from the paper.

FTEC5660 reproduction: see [REPRODUCTION.md](REPRODUCTION.md) for the Windows environment, pinned dependencies, and evaluation commands.

Completed three-round measurements: [THREE_ROUND_RESULTS.md](THREE_ROUND_RESULTS.md).
English report: [submission/REPORT_DRAFT.md](submission/REPORT_DRAFT.md). See also the [metric definitions](submission/F1_AND_CATEGORY5.md) and [error-case analysis](ERROR_CASE_ANALYSIS.md).

Replay the packaged, real experiment outputs without an API request:

```powershell
python -X utf8 scripts/demo-results.py --presentation
```

This is saved-result replay, not live model inference. The portable measured data are in `submission/data/` and `submission/measurements.json`.

### Install and run a new evaluation

The measured environment is Windows, Python 3.12 and CPU-based PyTorch. In PowerShell:

```powershell
git clone https://github.com/crescentIsland/A-mem.git
cd A-mem
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
Copy-Item .env.example .env
```

Edit the local `.env`: set `OPENAI_API_KEY` to your own DeepSeek API key and `OPENAI_BASE_URL=https://api.deepseek.com`. Never commit that file. Then prepare resources and run:

```powershell
.\.venv\Scripts\python.exe scripts/check-environment.py
.\scripts\run-eval.ps1 -Model deepseek-flash -Ratio 0.1 -RetrieveK 10 -Seed 42
.\scripts\run-eval.ps1 -Model deepseek-flash -Ratio 0.1 -RetrieveK 5 -Seed 42 -RequireCache
```

These commands download model/NLTK resources and make paid API requests. The first evaluation constructs memory; the second requires the existing cache. New outputs go to `results/`. Rebuilding memory and remote-model generation are stochastic, so new answers can differ from the saved measurements. See [REPRODUCTION.md](REPRODUCTION.md) for the three-round design, configuration details and validation commands.

### Changes and measured outcome

- DeepSeek integration, dataset-specific cache isolation and API-usage measurement.
- Atomic answer checkpoints and recovery tests for interrupted evaluations.
- Six saved QA result sets, quality/cost summaries, error cases and API-free replay.

Lower k reduced QA tokens by a mean paired **50.38%**, with an overall F1 difference of **−0.86 percentage points** and an answerable-question F1 difference of **−3.28 percentage points**. This is an observed quality-resource trade-off on one fixed-memory conversation, not a universal optimum. Full means and sample standard deviations are in [THREE_ROUND_RESULTS.md](THREE_ROUND_RESULTS.md).

## Upstream project description

A novel agentic memory system for LLM agents that can dynamically organize memories in an agentic way.

> **Note:** This repository is specifically designed to reproduce the results presented in our paper. If you want to use the A-Mem system in building your agents, please refer to our official implementation at: [A-mem-sys](https://github.com/WujiangXu/A-mem-sys)

For more details, please refer to our paper: [A-Mem: Agentic Memory for LLM Agents](https://arxiv.org/pdf/2502.12110)

> 🔥 **News (Oct 2026):** We provide a stronger version of A-Mem, **FlexA-Mem: Budget-Adaptive Agentic Memory for LLM Agents** ([paper](https://arxiv.org/html/2610.33274v1), [code](https://github.com/WujiangXu/Flex-Amem)). FlexA-Mem keeps A-Mem's linked notes but uses them as the compressed history itself: at every step, the agent sees the whole history as a timeline of notes, and the notes most relevant to the current step are expanded in place into their raw content or excerpts, so the prompt fits any token budget. It is evaluated on LongMemEval-S, LoCoMo, SWE-bench Verified and AppWorld.

## Introduction 🌟

Large Language Model (LLM) agents have demonstrated remarkable capabilities in handling complex real-world tasks through external tool usage. However, to effectively leverage historical experiences, they require sophisticated memory systems. Traditional memory systems, while providing basic storage and retrieval functionality, often lack advanced memory organization capabilities.

Our project introduces an innovative **Agentic Memory** system that revolutionizes how LLM agents manage and utilize their memories:

<div align="center">
  <img src="Figure/intro-a.jpg" alt="Traditional Memory System" width="600"/>
  <img src="Figure/intro-b.jpg" alt="Our Proposed Agentic Memory" width="600"/>
  <br>
  <em>Comparison between traditional memory system (top) and our proposed agentic memory (bottom). Our system enables dynamic memory operations and flexible agent-memory interactions.</em>
</div>

## Key Features ✨

- 🔄 Dynamic memory organization based on Zettelkasten principles
- 🔍 Intelligent indexing and linking of memories
- 📝 Comprehensive note generation with structured attributes
- 🌐 Interconnected knowledge networks
- 🔄 Continuous memory evolution and refinement
- 🤖 Agent-driven decision making for adaptive memory management

## Framework 🏗️

<div align="center">
  <img src="Figure/framework.jpg" alt="Agentic Memory Framework" width="800"/>
  <br>
  <em>The framework of our Agentic Memory system showing the dynamic interaction between LLM agents and memory components.</em>
</div>

## How It Works 🛠️

When a new memory is added to the system:
1. Generates comprehensive notes with structured attributes
2. Creates contextual descriptions and tags
3. Analyzes historical memories for relevant connections
4. Establishes meaningful links based on similarities
5. Enables dynamic memory evolution and updates

## Results 📊

Empirical experiments conducted on six foundation models demonstrate superior performance compared to existing SOTA baselines.

## Getting Started 🚀

1. Clone the repository:
```bash
git clone https://github.com/WujiangXu/AgenticMemory.git
cd AgenticMemory
```

2. Install dependencies:
Option 1: Using venv (Python virtual environment)
```bash
# Create and activate virtual environment
python -m venv a-mem
source a-mem/bin/activate  # Linux/Mac
a-mem\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

Option 2: Using Conda
```bash
# Create and activate conda environment
conda create -n myenv python=3.9
conda activate myenv

# Install dependencies
pip install -r requirements.txt
```

3. Run the experiments in LoCoMo dataset:

**Option A — Original evaluation (requires OpenAI JSON schema support):**
```bash
python test_advanced.py
```

**Option B — Robust evaluation (recommended, works with any LLM backend):**

The robust evaluation (`test_advanced_robust.py`) removes the JSON schema dependency and supports OpenAI API, vLLM, and Ollama backends.

```bash
# OpenAI models
python test_advanced_robust.py --backend openai --model gpt-4o-mini \
    --dataset data/locomo10.json --output results_robust_gpt-4o-mini.json

# vLLM-served open-source models (start vLLM server first)
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-3B-Instruct --port 30000 \
    --dtype float16 --enforce-eager --max-model-len 8192
python test_advanced_robust.py --backend vllm --model Qwen/Qwen2.5-3B-Instruct \
    --dataset data/locomo10.json --output results_robust_qwen3b.json \
    --sglang_port 30000

# Ollama models
python test_advanced_robust.py --backend ollama --model qwen2.5:3b \
    --dataset data/locomo10.json --output results_robust_ollama_qwen3b.json
```

Key arguments:
- `--retrieve_k`: Number of memories to retrieve per query (default: 10). Tune this per model for best results.
- `--ratio`: Fraction of dataset to evaluate (e.g., `--ratio 0.1` for 10% quick test).
- `--backend`: One of `openai`, `vllm`, `ollama`.
- `--sglang_port`: Port for vLLM/SGLang server (default: 30000).

4. Run the full k-sweep to find optimal retrieval k per model:
```bash
bash run_k_sweep.sh
```

**Note:** To achieve the optimal performance reported in our paper, please adjust the hyperparameter `k` value accordingly. Memories are cached after the first run, so subsequent k-sweep evaluations only re-run the QA answering step.

**Categories Information:** The LoCoMo dataset contains the following categories:
* Category 1: Multi-hop
* Category 2: Temporal
* Category 3: Open-domain
* Category 4: Single-hop
* Category 5: Adversarial

For more details about the categories, please refer to [this GitHub issue](https://github.com/snap-research/locomo/issues/6). 

## Citation 📚

If you use this code in your research, please cite our series of works on agentic memory:

```bibtex
@inproceedings{xu2025amem,
  title={A-Mem: Agentic memory for llm agents},
  author={Xu, Wujiang and Liang, Zujie and Mei, Kai and Gao, Hang and Tan, Juntao and Zhang, Yongfeng},
  booktitle={Advances in Neural Information Processing Systems},
  year={2025}
}

@article{xu2026flexamem,
  title={FlexA-Mem: Budget-Adaptive Agentic Memory for LLM Agents},
  author={Xu, Wujiang and Han, Jiaojiao and Zhu, Xi and Zhang, Qizheng and Liang, Kaiqu and Yin, Yutong and Mei, Kai and Metaxas, Dimitris N.},
  journal={arXiv preprint arXiv:2610.33274},
  year={2026}
}
```

## License 📄

This project is licensed under the MIT License. See LICENSE for details.


