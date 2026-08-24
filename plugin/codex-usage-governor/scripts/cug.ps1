[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('status', 'bar', 'compact', 'today', 'week', 'history', 'watch', 'start', 'stop', 'blocks', 'codex', 'config', 'recommend', 'shell-install', 'shell-remove', 'shell-status')]
    [string]$Command = 'status',
    [string]$Model = 'unspecified',
    [string]$Reasoning = 'unspecified',
    [ValidateSet('planning', 'implementation', 'debugging', 'research', 'review', 'media', 'other', 'unspecified')]
    [string]$Category = 'unspecified',
    [ValidateSet('accepted', 'partial', 'rework', 'failed', 'unrated')]
    [string]$Outcome = 'unrated',
    [double]$TimeSavedHours,
    [string]$Note,
    [string]$Task,
    [string]$ExpectedOutcome,
    [int]$IntervalSeconds = 60,
    [string]$DataDir,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CodexArguments
)

$ErrorActionPreference = 'Stop'
$Governor = Join-Path $PSScriptRoot 'governor.py'
$ShellInstaller = Join-Path $PSScriptRoot 'install-shell-integration.ps1'
$Advisor = Join-Path $PSScriptRoot 'advisor.py'
$DataDir = if ($DataDir) { $DataDir } elseif ($env:PLUGIN_DATA) { $env:PLUGIN_DATA } else { Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex\usage-governor' }

function Invoke-Governor {
    param([string[]]$GovernorArguments)
    & python $Governor --data-dir $DataDir @GovernorArguments
    if ($LASTEXITCODE -ne 0) { throw "Codex Usage Governor exited with code $LASTEXITCODE" }
}

switch ($Command) {
    'shell-install' { & $ShellInstaller Install }
    'shell-remove'  { & $ShellInstaller Remove }
    'shell-status'  { & $ShellInstaller Status }
    'recommend' {
        Invoke-Governor @('collect')
        & python $Advisor --data-dir $DataDir --project (Get-Location).Path --task $Task --outcome $ExpectedOutcome
    }
    'status'  { Invoke-Governor @('collect'); Invoke-Governor @('report', 'status') }
    'compact' { Invoke-Governor @('collect'); Invoke-Governor @('report', 'compact') }
    'bar' {
        $Host.UI.RawUI.WindowTitle = 'Codex Usage Governor'
        do {
            & python $Governor --data-dir $DataDir collect *> $null
            $Escape = [char]27
            Write-Host "$Escape[2J$Escape[H" -NoNewline
            & python $Governor --data-dir $DataDir report bar
            & python $Advisor --data-dir $DataDir --project (Get-Location).Path --bar
            Start-Sleep -Seconds ([Math]::Max(30, $IntervalSeconds))
        } while ($true)
    }
    'today'   { Invoke-Governor @('collect'); Invoke-Governor @('report', 'today') }
    'week'    { Invoke-Governor @('collect'); Invoke-Governor @('report', 'week') }
    'history' { Invoke-Governor @('report', 'history') }
    'blocks'  { Invoke-Governor @('work', 'list') }
    'config'  { Invoke-Governor @('config') }
    'start' {
        $Arguments = @('work', 'start', '--model', $Model, '--reasoning', $Reasoning, '--category', $Category)
        if ($Note) { $Arguments += @('--note', $Note) }
        Invoke-Governor $Arguments
    }
    'stop' {
        $Arguments = @('work', 'stop', '--outcome', $Outcome)
        if ($PSBoundParameters.ContainsKey('TimeSavedHours')) { $Arguments += @('--time-saved-hours', [string]$TimeSavedHours) }
        if ($Note) { $Arguments += @('--note', $Note) }
        Invoke-Governor $Arguments
    }
    'watch' {
        do {
            Clear-Host
            Invoke-Governor @('collect')
            Invoke-Governor @('report', 'status')
            Start-Sleep -Seconds ([Math]::Max(15, $IntervalSeconds))
        } while ($true)
    }
    'codex' {
        Invoke-Governor @('collect')
        Invoke-Governor @('report', 'compact')
        & codex @CodexArguments
        Invoke-Governor @('collect')
        Invoke-Governor @('report', 'compact')
    }
}
