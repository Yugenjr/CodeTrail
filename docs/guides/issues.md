# Issues

CodeTrail can discover and inspect issues in GitHub repositories.

Commands

- `codetrail issues list [OWNER/REPO]` — list open issues for a repository (supports pagination).
- `codetrail issues show [OWNER/REPO] [ISSUE_NUMBER]` — show issue details. Use `--full` to show the full body and timestamps.
- `codetrail issues search [OWNER/REPO] --query "text"` — search issue titles and bodies.
- `codetrail issues filter [OWNER/REPO] --label bug` — filter issues by label.

Examples

```bash
codetrail issues list microsoft/playwright
codetrail issues show microsoft/playwright 40969 --full
codetrail issues search vercel/next.js --query "regression"
codetrail issues filter your-org/your-repo --label "good first issue"
```

Notes

- `issues list` supports `--limit` and `--page` for pagination.
- `issues show` will, by default, print a concise summary; add `--full` to include the whole issue body and created/updated timestamps.
