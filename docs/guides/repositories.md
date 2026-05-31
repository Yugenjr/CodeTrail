# Repositories

CodeTrail provides a set of commands to inspect and analyze GitHub repositories.

Commands

- `codetrail repo info [OWNER/REPO]` — shows repository metadata and a short summary.
- `codetrail repo stack [OWNER/REPO]` — inspects the repository to produce a stack: identity, language composition, frameworks, testing, developer and build tools.
- `codetrail repo structure [OWNER/REPO]` — (basic) lists top-level files and structure hints.

Repository Stack Output

Key concepts surfaced by `repo stack`:

- Repository Identity: A conservative identification of the repository's primary framework or technology based on name, description, topics, and strong evidence in manifests. If identity signals are weak, CodeTrail will return `Unknown` and fall back to `Primary Technology` (language) instead.

- Language Composition: Percent breakdown computed from GitHub's `/languages` API.

- Framework Detection: Frameworks are detected using a tiered-evidence model. Tier 1 (manifests/dependencies) is highest weight; Tier 2 (code imports and file matches) is medium; Tier 3 (README or docs mentions) is low. Matching is strict to avoid substring false positives.

- Testing Detection: Tools like `pytest`, `jest`, `go test` are identified from dependencies and imports and shown in their own category.

- Build Tools: Tools such as `setuptools`, `maven`, `cargo`, `npm` are detected and listed under build tools.

Example

```bash
codetrail repo stack facebook/react --debug
```

Sample (abridged) output:

```
Repository Identity: React (Frontend Library)
Languages: JavaScript 68.1%, TypeScript 29.0%, Other 2.9%
Frameworks:
- React — Score: 95 — sources: package.json(devDependencies)
- Jest  — Score: 85 — sources: package.json(devDependencies, README)

Testing:
- Jest — detected via devDependencies and README examples

Build Tools:
- Node.js/npm — detected via package.json and lock files
```
