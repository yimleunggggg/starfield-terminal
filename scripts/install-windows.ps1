# Windows Terminal / PowerShell: text-only welcome. No graphics protocol or fonts.
param([switch]$NoProfile, [switch]$WithSpinner)
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (Get-Command py -ErrorAction SilentlyContinue) {
  $PythonCommand = 'py -3'
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  $PythonCommand = 'python'
} else {
  throw 'Python 3 required. Install Python and try again.'
}
$Target = Join-Path $HOME '.config\starfield-terminal'
$Destination = Join-Path $Target 'welcome.py'
New-Item -Path $Target -ItemType Directory -Force | Out-Null
$Timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
if (Test-Path $Destination) { Copy-Item $Destination "$Destination.backup-$Timestamp" }
Copy-Item (Join-Path $Root 'src\welcome.py') $Destination -Force
$Config = Join-Path $Target 'config.json'
if (-not (Test-Path $Config)) { Copy-Item (Join-Path $Root 'examples\config.json') $Config }
if ($WithSpinner) {
  $SpinnerScript = Join-Path $Target 'claude-spinner.py'
  Copy-Item (Join-Path $Root 'scripts\claude-spinner.py') $SpinnerScript -Force
  $env:PYTHONIOENCODING = 'utf-8'
  if ($PythonCommand -eq 'py -3') {
    & py -3 $SpinnerScript --install
  } else {
    & python $SpinnerScript --install
  }
  if ($LASTEXITCODE -ne 0) { throw 'Claude Code spinner configuration failed. See the message above.' }
}
if (-not $NoProfile) {
  $ProfilePath = $PROFILE.CurrentUserCurrentHost
  $Parent = Split-Path -Parent $ProfilePath
  New-Item $Parent -ItemType Directory -Force | Out-Null
  $Previous = if (Test-Path $ProfilePath) { Get-Content $ProfilePath -Raw } else { '' }
  $Begin = '# >>> STARFIELD TERMINAL >>>'
  $End = '# <<< STARFIELD TERMINAL <<<' 
  $Call = "$PythonCommand `"`$HOME\.config\starfield-terminal\welcome.py`" --no-image"
  $Block = @"
$Begin
# Text-only PowerShell welcome
if (`$Host.Name -eq 'ConsoleHost' -and -not `$env:SSH_CONNECTION) {
  $Call
}
$End
"@
  if (Test-Path $ProfilePath) { Copy-Item $ProfilePath "$ProfilePath.backup-$Timestamp" }
  if ($Previous.Contains($Begin) -and $Previous.Contains($End)) {
    $Pattern = '(?ms)^' + [regex]::Escape($Begin) + '\r?\n.*?^' + [regex]::Escape($End)
    $Next = [regex]::Replace($Previous, $Pattern, $Block, 1)
  } else {
    $Next = $Previous.TrimEnd() + "`n`n" + $Block + "`n"
  }
  Set-Content -Path $ProfilePath -Value $Next -Encoding UTF8
}
Write-Host 'Starfield Terminal (text-only) installed for PowerShell.'
Write-Host 'No Starship configuration was modified.'
Write-Host 'Playful spinner:' $(if ($WithSpinner) { 'enabled for Claude Code' } else { 'unchanged; rerun with -WithSpinner to opt in' })
Write-Host 'Preview:' $PythonCommand $Destination '--no-image'
Write-Host 'Open a new PowerShell tab to see the greeting.'
