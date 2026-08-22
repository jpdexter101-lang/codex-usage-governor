[CmdletBinding()]
param(
    [ValidateSet('Install', 'Remove', 'Status')]
    [string]$Action = 'Install',
    [string]$ProfilePath = $PROFILE.CurrentUserAllHosts
)

$ErrorActionPreference = 'Stop'
$BeginMarker = '# BEGIN Codex Usage Governor (managed)'
$EndMarker = '# END Codex Usage Governor (managed)'

function Remove-ManagedBlock {
    param([string]$Content)
    $Pattern = '(?ms)^' + [regex]::Escape($BeginMarker) + '.*?^' + [regex]::Escape($EndMarker) + '\r?\n?'
    return [regex]::Replace($Content, $Pattern, '')
}

$Existing = if (Test-Path -LiteralPath $ProfilePath) {
    Get-Content -Raw -LiteralPath $ProfilePath
} else {
    ''
}
$HasIntegration = $Existing.Contains($BeginMarker)

if ($Action -eq 'Status') {
    if ($HasIntegration) { "Installed: $ProfilePath" } else { "Not installed: $ProfilePath" }
    exit 0
}

$Clean = Remove-ManagedBlock $Existing
if ($Action -eq 'Remove') {
    if (Test-Path -LiteralPath $ProfilePath) {
        Set-Content -LiteralPath $ProfilePath -Value $Clean -Encoding UTF8
    }
    "Removed Codex Usage Governor shell integration from $ProfilePath"
    exit 0
}

$Block = @'
# BEGIN Codex Usage Governor (managed)
function Find-CodexGovernorLauncher {
    $roots = @(
        (Join-Path $HOME 'plugins\codex-usage-governor\scripts'),
        (Join-Path $HOME '.codex\plugins\cache')
    )
    $launchers = @()
    if (Test-Path -LiteralPath $roots[0]) {
        $launchers += Get-Item -LiteralPath (Join-Path $roots[0] 'launch-codex-governor.ps1') -ErrorAction SilentlyContinue
    }
    if (Test-Path -LiteralPath $roots[1]) {
        $launchers += Get-ChildItem -LiteralPath $roots[1] -Filter 'launch-codex-governor.ps1' -File -Recurse -ErrorAction SilentlyContinue
    }
    $launcher = $launchers | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if (-not $launcher) { throw 'Codex Usage Governor launcher was not found. Reinstall the plugin or remove its shell integration.' }
    $launcher.FullName
}

function codex-raw {
    $command = Get-Command codex.exe -ErrorAction Stop
    & $command.Source @args
}

function codex {
    $launcher = Find-CodexGovernorLauncher
    & powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $launcher -WorkingDirectory (Get-Location).Path @args
}
# END Codex Usage Governor (managed)
'@

$Parent = Split-Path -Parent $ProfilePath
if ($Parent -and -not (Test-Path -LiteralPath $Parent)) {
    New-Item -ItemType Directory -Path $Parent -Force | Out-Null
}
$NewContent = if ([string]::IsNullOrWhiteSpace($Clean)) { $Block + "`r`n" } else { $Clean.TrimEnd() + "`r`n`r`n" + $Block + "`r`n" }
Set-Content -LiteralPath $ProfilePath -Value $NewContent -Encoding UTF8
$EffectivePolicy = Get-ExecutionPolicy
if ($EffectivePolicy -eq 'Restricted') {
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
    "Changed the current-user PowerShell execution policy from Restricted to RemoteSigned so the profile can load."
}
"Installed Codex Usage Governor shell integration in $ProfilePath"
"Open a new PowerShell window, then use 'codex'. Use 'codex-raw' to bypass the Governor."
