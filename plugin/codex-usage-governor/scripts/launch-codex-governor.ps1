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
    & $Codex @CodexArguments
} else {
    $NewWindowArguments = @(
        '-w', 'new',
        'new-tab', '--title', 'Codex', '-d', $WorkingDirectory,
        $Codex
    ) + $CodexArguments + @(
        ';', 'split-pane', '--horizontal', '--size', '0.12',
        '--title', 'Usage Governor', '-d', $WorkingDirectory,
        'powershell.exe', '-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass',
        '-File', $Cug, 'bar', '-IntervalSeconds', [string]$RefreshSeconds
    )
    & wt.exe @NewWindowArguments
}
