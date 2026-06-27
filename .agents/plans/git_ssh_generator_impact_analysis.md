# Pre-Implementation Impact Analysis: Auto-SSH Key Generator Wizard

## 1. Explore Options

We evaluate two approaches to implement SSH key pair generation within our profile manager CLI command.

### Option A: Subprocess Execution of System `ssh-keygen`
Utilize Python's `subprocess` to call the native `ssh-keygen` binary already installed on the system (included with OpenSSH on Linux/macOS and standard Git on Windows).
- Command: `ssh-keygen -t ed25519 -C "<email>" -f "<path>" -N ""`

### Option B: Pure-Python Cryptography Library Generation
Use Python's third-party `cryptography` package to generate and serialize the key pair completely in-memory.

---

## 2. Trade-offs Matrix

| Criteria | Option A: Native `ssh-keygen` (Recommended) | Option B: Pure-Python Cryptography |
|---|---|---|
| **Dependency Footprint** | **None**: Relies on tools already installed on any developer machine that has Git. | **High**: Requires `pip install cryptography`, adding external library installation step during bootstrapping. |
| **Simplicity** | **High**: Directly calls standard, well-tested OpenSSH commands. | **Medium**: Requires writing Python cryptography code to format public keys in OpenSSH structure. |
| **Portability** | **High**: `ssh-keygen` is in the PATH for OpenSSH on Linux/macOS and Git Bash on Windows. | **High**: Runs on any system with Python, but requires C compiler/rust compiler for compile steps of cryptography dependencies on some environments. |
| **Maintainability** | **Low**: Standard shell invocation with zero dependencies. | **Medium**: Cryptography library APIs can change, requiring updates to serialization code. |

---

## 3. Recommendation

We choose **Option A** because it is zero-dependency, extremely lightweight, and utilizes standard cryptography tools already guaranteed to exist in a developer's Git environment.
