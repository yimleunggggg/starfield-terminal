$ErrorActionPreference = 'Stop'
$ProfilePath = $PROFILE.CurrentUserCurrentHost
if (Test-Path $ProfilePath) {
  $Old = Get-Content $ProfilePath -Raw
  $Begin = '# >>> STARFIELD TERMINAL >>>'
  $End = '# <<< STARFIELD TERMINAL <<<' 
  $Pattern = '(?ms)^' + [regex]::Escape($Begin) + '\r?\n.*?^' + [regex]::Escape($End) + '\r?\n?'
  $New = [regex]::Replace($Old, $Pattern, '', 1)
  if ($Old -ne $New) {
    Copy-Item $ProfilePath "$ProfilePath.backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Set-Content -Path $ProfilePath -Value $New -Encoding UTF8
    Write-Host 'Removed Starfield startup block from PowerShell profile.'
  }
}
$Target = Join-Path $HOME '.config\starfield-terminal'
$SpinnerScript = Join-Path $Target 'claude-spinner.py'
if (Test-Path $SpinnerScript) {
  if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $SpinnerScript --remove
  } elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $SpinnerScript --remove
  } else {
    Write-Host 'Python not found; Claude Code spinner settings left untouched.'
  }
}
Write-Host 'Installed files retained under ~/.config/starfield-terminal. Starship unchanged.'
