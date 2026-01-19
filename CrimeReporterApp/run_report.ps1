param(
  [string]$In = "C:\\Users\\Usuario\\Desktop\\Datos Crimenes Jamundi\\*.xlsx",
  [string]$Out = "C:\\Users\\Usuario\\Desktop\\Reporte_CrimeReporter_$(Get-Date -Format yyyyMMdd-HHmm).xlsx",
  [string]$Municipio = ""
)

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
  $py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
  if (!(Test-Path $py)) { throw "No se encontró la venv en .venv. Abre esta carpeta y crea una con: python -m venv .venv" }

  # Expandir patrones de entrada
  $files = Get-ChildItem -Path $In -ErrorAction SilentlyContinue | Where-Object { -not $_.PSIsContainer }
  if(!$files){ throw "No se encontraron archivos que coincidan con: $In" }

  $args = @('.\cli_report.py','--in') + ($files | ForEach-Object { $_.FullName }) + @('--out', $Out)
  if($Municipio){ $args += @('--municipio', $Municipio) }

  & $py $args
  if(Test-Path $Out){
    Write-Host "OK: Reporte generado -> $Out"
    exit 0
  } else {
    throw "No se generó el archivo de salida: $Out"
  }
}
catch {
  Write-Error $_.Exception.Message
  exit 1
}
finally {
  Pop-Location
}
