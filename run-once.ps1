param([switch]$NoNotify)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path 'config.yaml')) {
  Copy-Item 'config.example.yaml' 'config.yaml'
  Write-Host '已创建 config.yaml。请按 README 配置 llm 段和环境变量中的密钥。'
}

python -m pip install -r requirements.txt
$env:PYTHONPATH = 'src'
if ($NoNotify) {
  python -m radar.cli --no-notify
} else {
  python -m radar.cli
}

Write-Host '报告已生成。运行：python -m http.server 8000，然后打开 http://localhost:8000'
