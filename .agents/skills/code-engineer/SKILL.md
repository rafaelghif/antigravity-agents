---
name: code-engineer
description: Universal software engineering enforcer for any programming language (TypeScript, JavaScript, Python, Go, Rust, PHP, Java, C#, Dart/Flutter, C/C++, Swift, VB6, VB.NET, ASP/ASP.NET) and scientific advanced debugging workflow. Triggers when writing new features, refactoring code, or debugging complex runtime bugs and tracebacks.
requires_core: ">=4.3.0"
---
# Code Engineer Skill

## Objective
Ensure all generated code strictly follows SOLID, DRY, Clean Code, and framework-specific idiomatic best practices across modern, enterprise, mobile, and legacy programming languages.

## 1. Universal Language & Idiomatic Adaptations
- **TypeScript / JavaScript**: Enforce ES6+ syntax, strict null checks, type safety (`interface`/`type`), and async/await error handling.
- **Python**: Enforce PEP-8, explicit type hints (`typing`), context managers (`with`), and explicit exception handling.
- **Go**: Enforce idiomatic error handling (`if err != nil`), `gofmt` compliance, and goroutine safety.
- **Rust**: Enforce memory safety, zero-cost abstractions, explicit `Result`/`Option` pattern matching, and `clippy` checks.
- **PHP**: Enforce PSR-12 coding standards, strict types (`declare(strict_types=1);`), and modern PHP 8+ features.
- **Java / Kotlin**: Enforce OOP principles, immutability, proper access modifiers, and spring/gradle best practices.
- **C# / .NET / VB.NET**: Enforce LINQ conventions, async Task patterns, proper resource disposal (`using`), and .NET coding guidelines.
- **Dart / Flutter**: Enforce null safety, widget composition, state management best practices, and `dart analyze`.
- **C / C++**: Enforce RAII, smart pointers (`std::unique_ptr`, `std::shared_ptr`), memory safety, and `valgrind`/`cppcheck`.
- **Legacy Systems (VB6, Classic ASP)**: Respect legacy syntax (`Option Explicit`), explicit object cleanup (`Set obj = Nothing`), COM error handling (`On Error GoTo`), and prevent injection vulnerabilities in dynamic SQL.

## 2. Subagent Swarm Delegation & File Locking
- **POSIX Directory Locking Gate**: Before modifying any source file, claim an explicit atomic directory lock (`mkdir -p .agents/locks/<md5_hash_of_filepath>.lock`) containing `owner.json` metadata.
- **Recursion Limit**: Check current execution depth via active task plan (`.agents/plans/<task-slug>.md`) or `audit.jsonl` traces. If depth $\ge$ `config.json -> orchestration.max_skill_depth` (default 5), **DO NOT spawn further subagents**; execute directly to prevent infinite recursive loops.
- Delegate sub-modules to worker subagents using `invoke_subagent` when mandatory swarm triggers are met (`multi_file_threshold >= 3`).



## 3. Scientific Advanced Debugging Workflow
- **Log-Driven Diagnosis**: Read raw error tracebacks before forming hypotheses. Never guess or swallow exceptions.
- **Root Cause Isolation**: Trace execution paths step-by-step; verify object initialization states to prevent NullPointer/AttributeError/NullReference crashes.
- **Traceback Justification**: Every code edit during debugging MUST be justified by an explicit error traceback or verified root cause.

## 4. Mandatory Runtime Verification (Zero-Assumption)
- NEVER mark implementation completed without running the project's build/test suite using `run_command` (`npm test`, `pytest`, `cargo test`, `go test`, `dotnet test`, `flutter test`).
- Inspect build outputs cleanly; resolve any compiler warnings or failing tests before concluding.

