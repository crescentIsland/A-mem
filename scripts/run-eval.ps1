param(
    [string]$Model = 'deepseek-flash',
    [ValidateRange(1, 1000)][int]$RetrieveK = 10,
    [ValidateRange(0.001, 1.0)][double]$Ratio = 0.1,
    [int]$Seed = 42,
    [ValidateRange(0,3)][int]$Round = 0,
    [switch]$RequireCache,
    [switch]$Resume
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$env:HF_HOME = Join-Path $projectRoot '.cache\huggingface'
$env:HF_HUB_DISABLE_XET = '1'
$env:NLTK_DATA = Join-Path $projectRoot '.cache\nltk_data'
$env:NLTK_ALLOW_PROXIED_URLOPEN = '1'
$env:PYTHONUTF8 = '1'
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
Push-Location $projectRoot
try {
    New-Item -ItemType Directory -Force results | Out-Null
    $output = if ($Round -gt 0) {
        'results/round{0}_k{1}_seed{2}.json' -f $Round, $RetrieveK, $Seed
    } else {
        'results/k{0}_seed{1}_{2}.json' -f $RetrieveK, $Seed, (Get-Date -Format 'yyyyMMdd_HHmmss')
    }
    if (Test-Path -LiteralPath $output) { throw "Result already exists; refusing to overwrite $output" }
    $datasetHash = (Get-FileHash 'data/locomo10.json' -Algorithm SHA256).Hash.ToLower()
    if ($RequireCache) {
        $cacheRoot = Join-Path $projectRoot ('cached_memories_robust_openai_{0}_{1}' -f $Model, $datasetHash.Substring(0,12))
        foreach ($name in @('memory_cache_sample_0.pkl','memory_cache_sample_0.pkl.version','retriever_cache_sample_0.pkl','retriever_cache_embeddings_sample_0.npy')) {
            if (-not (Test-Path -LiteralPath (Join-Path $cacheRoot $name))) { throw "Required memory cache missing: $name" }
        }
    }
    $env:AMEM_USAGE_LOG = Join-Path $projectRoot ($output -replace '\.json$', '_usage.jsonl')
    $manifest = [ordered]@{
        started_at = (Get-Date).ToString('o')
        process_id = $PID
        model = $Model
        provider = 'DeepSeek (configured in .env)'
        retrieve_k = $RetrieveK
        ratio = $Ratio
        seed = $Seed
        round = $Round
        dataset_sha256 = $datasetHash
        upstream_commit = (git rev-parse HEAD)
        thinking = 'disabled for api.deepseek.com'
        output = $output
        usage_log = $env:AMEM_USAGE_LOG
    }
    $manifestPath = $output -replace '\.json$', '_manifest.json'
    if ($Resume) {
        if (-not (Test-Path -LiteralPath $manifestPath)) { throw 'Cannot resume without original manifest.' }
        $oldManifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        if ($oldManifest.model -ne $Model -or $oldManifest.retrieve_k -ne $RetrieveK -or $oldManifest.seed -ne $Seed -or $oldManifest.dataset_sha256 -ne $datasetHash -or $oldManifest.round -ne $Round -or $oldManifest.ratio -ne $Ratio) { throw 'Resume settings differ from original manifest.' }
        $checkpointPath = $output -replace '\.json$', '_checkpoint.json'
        if (-not (Test-Path -LiteralPath $checkpointPath)) { throw 'Cannot resume without a verified checkpoint.' }
        $oldManifest | Add-Member -NotePropertyName resumed_at -NotePropertyValue (Get-Date).ToString('o') -Force
        $oldManifest | ConvertTo-Json | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    } else {
        if (Test-Path -LiteralPath $manifestPath) { throw 'Existing manifest requires an explicit resume.' }
        $manifest | ConvertTo-Json | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    }
    Write-Output "Run manifest: $manifestPath"
    & $python -m dotenv run -- $python test_advanced_robust.py --backend openai --model $Model --ratio $Ratio --retrieve_k $RetrieveK --seed $Seed --dataset data/locomo10.json --output $output
    if ($LASTEXITCODE -ne 0) { throw "Evaluation failed with exit code $LASTEXITCODE" }
} finally {
    Pop-Location
}
