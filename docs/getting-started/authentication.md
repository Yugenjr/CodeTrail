# Authentication

CodeTrail uses GitHub API calls for many features. For higher rate limits and access to private repositories, you should authenticate with a GitHub Personal Access Token (PAT).

Commands

- `codetrail login` — prompts for a PAT and stores it locally.
- `codetrail logout` — removes stored credentials.

Creating a PAT

1. Visit https://github.com/settings/tokens
2. Click **Generate new token** and select scopes: `repo` (for private repo access) and `read:org` if you need org-level repo lists. For public-only analysis you can select minimal scopes.

Storage location

CodeTrail stores the token in a local configuration file in your home directory under `~/.codetrail/config.json` (Windows: `%USERPROFILE%\\.codetrail\\config.json`). The file is created with restrictive permissions when possible.

Security considerations

- Treat the PAT like a password. Do not commit it to source control.
- Use a token with the least privileges required for your workflow.
- To revoke access, remove the token from GitHub and run `codetrail logout` locally.
