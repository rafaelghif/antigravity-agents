# Pre-Implementation Impact Analysis: Interactive Profile Registration Wizard for CLI profile add

We evaluate options to implement a developer registration wizard.

## Option A: Inline Interactive Wizard inside `profile.py` (Recommended)
Embed the `run_interactive_wizard` routine within `profile.py`. If `args` are empty when calling `profile add`, launch the wizard step-by-step to prompt the developer.
- **Pros**: Maintains a clean, singular entrypoint, leverages existing helper validations and helper functions (`generate_ssh_key`, validation loops), and works on all platforms.
- **Cons**: None.

## Option B: Separate wizard script
Create a separate script (e.g. `register_profile.py`).
- **Pros**: None.
- **Cons**: Fragmented developer experience, code duplication for profile saving/loading/generation.

### Downstream Impacts
- Modifies `.agents/scripts/cli/commands/profile.py` to add `run_interactive_wizard` and branch on empty `args` in `handle_add`.
- Modifies `.agents/tests/test_profile.py` to add tests for the interactive wizard paths.

**Decision**: **Option A** is selected.
