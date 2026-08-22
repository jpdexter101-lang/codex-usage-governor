[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$WorkingDirectory = (Get-Location).Path,
    [int]$RefreshSeconds = 60,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CodexArguments
)

$ErrorActionPreference = 'Stop'
$Cug = Join-Path $PSScriptRoot 'cug.ps1'
$Codex = (Get-Command codex.exe -ErrorAction Stop).Source
$PreferencePath = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex\usage-governor\launch-preference.json'
$RecommendedArguments = @()
if (Test-Path -LiteralPath $PreferencePath) {
    try {
        $Preference = Get-Content -Raw -LiteralPath $PreferencePath | ConvertFrom-Json
        if ($Preference.model -in @('gpt-5.6-sol', 'gpt-5.6-terra', 'gpt-5.6-luna')) {
            $RecommendedArguments += @('--model', [string]$Preference.model)
        }
        if ($Preference.reasoning -in @('low', 'medium', 'high', 'xhigh', 'max')) {
            $RecommendedArguments += @('-c', ('model_reasoning_effort="{0}"' -f $Preference.reasoning))
        }
    } catch { }
}
$EffectiveCodexArguments = $RecommendedArguments + $CodexArguments

$GovernorPaneArguments = @(
    '-w', '0',
    'split-pane', '--horizontal', '--size', '0.12',
    '--title', 'Usage Governor', '-d', $WorkingDirectory,
    'powershell.exe', '-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass',
    '-File', $Cug, 'bar', '-IntervalSeconds', [string]$RefreshSeconds,
    ';', 'move-focus', 'up'
)

if ($env:WT_SESSION) {
    & wt.exe @GovernorPaneArguments
    & $Codex @EffectiveCodexArguments
} else {
    $NewWindowArguments = @(
        '-w', 'new',
        'new-tab', '--title', 'Codex', '-d', $WorkingDirectory,
        $Codex
    ) + $EffectiveCodexArguments + @(
        ';', 'split-pane', '--horizontal', '--size', '0.12',
        '--title', 'Usage Governor', '-d', $WorkingDirectory,
        'powershell.exe', '-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', $Cug, 'bar', '-IntervalSeconds', [string]$RefreshSeconds
    )
    & wt.exe @NewWindowArguments
}
