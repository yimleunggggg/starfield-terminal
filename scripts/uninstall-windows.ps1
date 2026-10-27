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
Write-Host 'Installed files retained under ~/.config/starfield-terminal. Starship unchanged.'
