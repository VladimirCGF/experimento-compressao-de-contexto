# Script facilitador para rodar o benchmark no Windows (PowerShell)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Iniciando Experimento de Compressao LLMLingua" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Verifica se existe um ambiente virtual ativo ou tenta usar o Python global
$PythonCmd = "python"

Write-Host "Executando benchmark.py..." -ForegroundColor Yellow
& $PythonCmd scripts/benchmark.py

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Fim da Execução! Verifique a pasta 'outputs/'" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
