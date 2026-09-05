# ADR-0004: Decentralized JSON Metadata with Build-Time BM25 Index

## Status
Accepted

## Context
`ui-ux-pro-max-skill` uses flat CSV databases (`styles.csv`, `colors.csv`) for its BM25 search engine. We evaluated whether to adopt CSV or JSON files for storing resume template metadata and role archetypes as the catalog scales from 4 to 10+ templates.

## Decision
We choose **Decentralized JSON Metadata (`src/templates/{id}/metadata.json`) for source assets** paired with a **Build-Time Aggregated BM25 Search Index**:
1. Each template maintains its own structured `metadata.json` alongside `canvas.html` and `style.css` (ensuring Locality and zero merge conflicts);
2. `search-template.py` implements a pluggable `BaseTemplateScorer` interface with `WeightedRuleScorer`, `BM25TextScorer`, and `HybridTemplateScorer` (70% rules + 30% BM25).

## Consequences
### Positive
- **High Locality & Modularity**: Adding a new template is strictly folder-scoped (drop folder with metadata.json, canvas.html, style.css);
- **Rich Schema Representation**: Full support for nested structures (`layout.sidebarRatio`, `visualStyle.palette`, `supportedRoles[]`, `customizableTokens[]`);
- **Pluggable Search Engines**: Callers can choose between rule-based, BM25 text, or hybrid retrieval.
