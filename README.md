# Codex Usage Governor

> Public beta. I built and tested this on Windows with PowerShell.

I built this because the usage percentage by itself didn't tell me much. I wanted to know how much Codex I used today, whether my pace would last until reset, and which model gave me the best value for the work.

The Governor puts a small live bar under Codex in Windows Terminal:

```text
Codex 91% left | Today 7.0/12.6% | gpt-5.6-sol | [HIGH] | 2.21%/h | out Sun 5:05 PM
```

It reads the allowance data from your signed-in Codex install and keeps a small local history. It leaves your commands and model choices alone.

## Quick start on Windows

You'll need the Codex CLI signed in with ChatGPT, Python 3, Windows Terminal, and Windows PowerShell.

```powershell
git clone https://github.com/jpdexter101-lang/codex-usage-governor.git
cd .\codex-usage-governor
.\plugin\codex-usage-governor\scripts\cug.cmd status
```

Keep a live view open:

```powershell
.\plugin\codex-usage-governor\scripts\cug.cmd watch
```

Launch Codex with the decision bar pinned underneath it in Windows Terminal:

```powershell
.\plugin\codex-usage-governor\scripts\launch-codex-governor.cmd
```

For the normal workflow, install the managed PowerShell integration once:

```powershell
.\plugin\codex-usage-governor\scripts\cug.cmd shell-install
```

Open a new PowerShell window after setup. Type `codex` like you usually would. Codex stays in the current tab and the Governor opens underneath it. Use `codex-raw` when you want the original CLI without the bar. Remove the shortcut with `cug.cmd shell-remove`.

The bar refreshes once a minute. It shows your remaining allowance, today's use and budget, active model, pace, burn rate, and projected exhaustion or reset time.

The Governor can't bypass, reset, or increase your account limits.

## Project layout

- `plugin/codex-usage-governor/`: installable Codex plugin
- `PROJECT.md`: product and engineering notes
- `STATE.md`: current status and known constraints
- `TODO.md`: work list
- `DECISIONS.md`: architecture notes
- `CHANGELOG.md`: release history

## What it tracks

- Reads rate-limit values from Codex App Server and uses local session data as a fallback.
- Keeps allowance history without prompts or responses.
- Calculates today's budget, recent burn rate, and projected exhaustion.
- Samples usage through Codex session hooks after you install and trust the plugin.

## Pace labels

- `SAFE`: below 75% of today's sustainable allowance budget and not projected to run out early.
- `PACE`: at least 75% of today's sustainable budget, but still projected to last until reset.
- `HIGH`: the recency-weighted burn rate projects exhaustion before the account reset.

The burn estimate needs 15 minutes of observations. It uses a 45-minute half-life, so recent work counts more than older work. Treat the labels as forecasts.

## Development usage

From the project root:

```powershell
python .\plugin\codex-usage-governor\scripts\governor.py --data-dir .\.local-data collect
python .\plugin\codex-usage-governor\scripts\governor.py --data-dir .\.local-data report status
python -m unittest discover -s tests -v
```

PowerShell development examples:

```powershell
.\plugin\codex-usage-governor\scripts\cug.ps1 status
.\plugin\codex-usage-governor\scripts\cug.ps1 start -Model gpt-5.6-sol -Reasoning ultra -Category implementation
.\plugin\codex-usage-governor\scripts\cug.ps1 stop -Outcome accepted -TimeSavedHours 2
```

If Windows blocks direct PowerShell script execution, use the included launcher:

```powershell
.\plugin\codex-usage-governor\scripts\cug.cmd status
```

The command wrapper applies `ExecutionPolicy Bypass` to its child PowerShell process. The optional shell installer may set your current-user policy to `RemoteSigned` so PowerShell can load your profile.

The development data directory above stays local to the project. An installed plugin receives its writable directory through `PLUGIN_DATA`.

## A couple of limits

Codex reports the account percentage without tying each jump to a model or action. Model comparisons need labeled work blocks and a decent sample size.

The collector uses a Codex App Server endpoint from the current CLI. A future Codex release may need a compatibility update.

## Privacy

Your data stays on your machine. See [PRIVACY.md](PRIVACY.md). Git ignores personal usage history and experiment files.

## License

MIT
