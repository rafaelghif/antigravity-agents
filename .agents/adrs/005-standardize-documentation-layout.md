# ADR-005: Standardize Documentation Layout

- **Date**: 2026-06-16
- **Status**: Accepted

## Context
The workspace contained documentation in two different locations: hidden inside '.agents/docs/' and in the root 'docs/' directory. This was redundant and confusing for developers who expect documentation to be standardized at the root 'docs/' folder of the repository. Additionally, some links in README.md pointed to '.agents/docs/'.

## Decision
We will move all modular documentation files from '.agents/docs/' into the root 'docs/' directory, delete '.agents/docs/' entirely, and update README.md and all references to point to the new 'docs/' paths. We will delete any duplicate files (such as the outdated CHANGELOG.md under '.agents/docs/') and keep 'CHANGELOG.md' at the root.

## Consequences
All project documentation is now centralized at the root 'docs/' directory. The '.agents/' directory is kept strictly for agent-specific configurations, schemas, locks, adrs, and memory ledgers. Links in README.md are standardized and fully functional.
