# Architecture Overview

High-level flow:

```text
GitHub
    ↓
GitHub Client
    ↓
Skill Engine
    ↓
Repository Analyzer
    ↓
Issue Explorer
    ↓
CLI
```

This arrangement keeps the GitHub integration isolated (GitHub Client), the analysis logic in services (Skill Engine, Repository Analyzer) and the presentation in the CLI layer.
