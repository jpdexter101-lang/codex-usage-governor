# Privacy

Codex Usage Governor runs locally. It does not operate a hosted service and does not send telemetry to the project author.

The governor stores normalized account-allowance readings, reset timestamps, plan type, optional user-supplied work labels, and configuration on the user's machine. It is designed not to store prompts, responses, source code, file contents, authentication tokens, or command output.

Codex itself communicates with OpenAI under the terms and privacy controls applicable to the user's OpenAI account. This project reads the allowance values exposed by the user's locally authenticated Codex installation.

Users can remove all governor-generated data by deleting the selected data directory. The default standalone location is `~/.codex/usage-governor`.
