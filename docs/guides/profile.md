# Profile

CodeTrail can analyze your GitHub profile and surface language and skill summaries.

Commands

- `codetrail profile` — shows basic account info and language composition across accessible repos.
- `codetrail profile --skills` — runs the Skill Analysis engine and reports detected frameworks, tools, and scores.

Example

```text
$ codetrail profile --skills
User: alice (github.com/alice)
Languages:
- Python: 72.4%
- Shell: 12.3%
- Markdown: 8.6%

Detected Skills:
- Frameworks: Flask (score: 95), Click (score: 82)
- Testing: pytest (score: 78)
```

How it works

- Language Analysis: CodeTrail requests GitHub's language byte counts for repositories and computes percentages to show which languages dominate a portfolio.
- Framework Detection: Analyzes manifests (requirements.txt, pyproject.toml, package.json, go.mod, Cargo.toml, pom.xml, etc.) and source hints. Evidence is tiered (manifests > import/code > README mentions) to reduce false positives.
- Skill Scoring: Each detected technology is accumulated with weighted evidence. Strong manifest/dependency signals carry the most weight; README mentions are low-weight.
