# AAC V2 Lessons Learned Archive

This file stores archived historical lessons learned that have been pruned from the active prompt context to optimize token overhead.

## Archived Lessons
- **[Learning: Performance]** Leverage git-diff driven incremental validation in validation guard to skip syntax and unit tests checks when code is untouched, optimizing validation run speed.
- **[Learning: Git & Security]** Validate GPG key imports and developer identity rotation rules locally to safeguard credentials.; Prevent applying placeholder Git profiles to local Git config when user-defined profiles are unconfigured, avoiding pollution of local Git author config; Harden git credentials tracking by explicitly ignoring git_profiles.json in configuration rules, and silence validation warnings by adding silent flags to git_api helpers.
