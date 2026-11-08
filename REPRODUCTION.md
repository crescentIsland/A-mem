# FTEC5660 A-MEM reproduction

## Source and scope

- Fork: https://github.com/crescentIsland/A-mem
- Upstream: https://github.com/WujiangXu/A-mem
- Starting commit: `f9a173dec325d84fcc97e7828775c7b241c33466`
- Setup date: 2026-11-07
- Local environment: Windows, Python 3.12, project-local `.venv`.
- Dataset: author's `data/locomo10.json`.
- Planned experiment: fixed LoCoMo subset, compare retrieval k=10 and k=5 with the same model and QA protocol.

Three paired k=10/k=5 rounds have completed. See [THREE_ROUND_RESULTS.md](THREE_ROUND_RESULTS.md) and [submission/REPORT_DRAFT.md](submission/REPORT_DRAFT.md). The latest upstream includes a robust text-only evaluation path and corrections relative to the original paper evaluation; a model swap and this newer evaluation must not be presented as an exact reproduction of the paper's numbers.

## Validated setup

- Python 3.12.0, PyTorch 2.15.0+cpu; CUDA unavailable in this environment.
- Author requirements installed; `pip check` passes.
- NLTK punkt, punkt_tab, wordnet, and omw-1.4 downloaded.
- `all-MiniLM-L6-v2` downloaded and produced a `(2, 384)` embedding array for two inputs.
- Dataset loader read 10 conversations and 1,986 questions.
- Original and robust memory modules imported successfully.
- The local `.env` launcher and provider connection were validated; credentials remain local. Completed experiments and the HTTP402 recovery are documented in the results report.

## Windows setup

Run from this repository in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
Copy-Item .env.example .env
```

Edit `.env` locally: put your **DeepSeek API key** in `OPENAI_API_KEY` and set `OPENAI_BASE_URL=https://api.deepseek.com`. The variable name is required by the author's OpenAI-compatible backend; requests go to DeepSeek. The launcher loads this file. Do not put keys in source files or Git commits.

## Evaluation

The commands below run a new paid evaluation. To inspect the completed experiment without installing model dependencies or calling an API, use standard Python from the repository root:

```powershell
python -X utf8 scripts/demo-results.py --verify
python -X utf8 scripts/demo-results.py --presentation
```

The replay verifies six saved result hashes and paired questions. It does not regenerate answers. Summary measurements are in `submission/measurements.json` and `submission/run-metrics.csv`.

DeepSeek calls explicitly disable thinking mode, keep the upstream 1000 output-token cap, and use a 120-second timeout with up to three attempts via the author's retry wrapper. Successful calls are logged to a run-specific `_usage.jsonl` file. Failures may incur provider charges not represented in this client usage log. Dataset-content hashes isolate memory caches between small functional checks and the full dataset; retrieval-k comparisons reuse a cache for the same dataset. These are integration/observability changes shared by both experimental conditions.

```powershell
.\scripts\run-eval.ps1 -Model deepseek-flash -Ratio 0.1 -RetrieveK 10 -Seed 42
.\scripts\run-eval.ps1 -Model deepseek-flash -Ratio 0.1 -RetrieveK 5 -Seed 42
```

`--ratio 0.1` selects the first conversation out of ten, including its history and questions; it does not randomly select 10% of QA pairs. Memory construction can therefore still involve many API calls. Results go to `results/`, upstream logs to `logs/`, and downloaded models/NLTK resources to `.cache/`.

For the measured study, both k settings reused one constructed memory in three rounds, in orders 10/5, 5/10 and 10/5. After the first successful full run has built the cache, use `-RequireCache` on subsequent `run-eval.ps1` invocations to prevent accidental reconstruction. Record file hashes before and after the comparison. Raw logs and binary memory/model caches are local artifacts and are not included in this public package. A fresh memory build is stochastic, so rerunning the code is not expected to reproduce the saved answers exactly; the committed answer sets support offline inspection of the reported results.

The robust upstream path uses plain-text prompts rather than the original JSON schemas. Its category-5 scoring defaults to the correct unanswerable reference; upstream offers `--legacy_c5_reference` for comparison with its original scoring. The launcher keeps the corrected default. Its seed controls category-5 option ordering; it does not guarantee deterministic remote-model responses or memory construction. Repeated measurements must document whether memory caches were reused.

The launcher defaults to `deepseek-flash`, as listed in the [DeepSeek API documentation](https://api-docs.deepseek.com/) checked on 2026-11-07. Override with `-Model` if needed. Record provider, resolved model version, temperature and other decoding parameters in the final report; model aliases can change over time. This model substitution makes the experiment different from the paper's original setup. ChatGPT subscriptions do not supply an API key or API credit.

## Environment validation

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/check-environment.py
$env:HF_HOME = Join-Path $PWD '.cache\huggingface'
$env:NLTK_DATA = Join-Path $PWD '.cache\nltk_data'
.\.venv\Scripts\python.exe test_advanced_robust.py --help
```

The upstream evaluation imports download/initialize an embedding model even when showing help. BERTScore may download a separate, larger scoring model during evaluation.

The resource check and launcher enable NLTK's documented proxy opt-in within their process because this machine routes downloads through a configured proxy. Use these scripts only with a trusted proxy. The setting does not change global Windows proxy or NLTK configuration.
