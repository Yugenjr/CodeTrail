# Repository Analysis

Repository analysis is performed by the `Repository Analyzer` component and includes:

- Repository Resolver — determines if a repository is local or remote and normalizes identifiers.
- Language Analyzer — fetches GitHub language byte counts and computes percentages.
- Repository Identity Analyzer — analyzes name, description and topics to conservatively determine primary identity (guarded by a strength threshold to avoid invented frameworks).
- Framework Detection — inspects manifests (tier 1 evidence), code imports and files (tier 2), and README mentions (tier 3) to build weighted scores for detected technologies.

Design notes: evidence is tiered and matching is strict to reduce false positives.
