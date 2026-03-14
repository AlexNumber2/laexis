$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
