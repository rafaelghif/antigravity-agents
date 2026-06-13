#!/usr/bin/env bash
# Antigravity Agent Core Helper Script
set -euo pipefail

MEMORY_FILE=".agents/memory.md"
LOCKS_DIR=".agents/locks"
ARCHIVE_DIR=".agents/archive"

show_help() {
    echo "Usage: \$0 [command] [args]"
    echo ""
    echo "Commands:"
    echo "  init [name] [stack] [arch] Initialize the workspace interactively or with parameters"
    echo "  recon             Run autonomous codebase stack and directory structure detection"
    echo "  validate          Perform security audit, lock checks, and memory size validation"
    echo "  doctor            Diagnose workspace health and verify system executables"
    echo "  commit            Verify code tests, run security checks, and execute conventional commit"
    echo "  sync-git          Synchronize Git branch and last commit hash with memory.md"
    echo "  lock [module]     Acquire a lock on a module"
    echo "  unlock [module]   Release a lock on a module"
    echo "  archive           Archive completed sprint tasks and reset memory.md checklist"
    echo "  migrate           Migrate workspace from older agent versions to version 1.4.0"
    echo "  build             Run monorepo-aware project compilation/build commands"
    echo "  lint              Run monorepo-aware linter validations on modified folders"
    echo "  test              Run monorepo-aware testing runner suites on modified folders"
    echo "  sync-api          Synchronize API contracts and generate typed TypeScript client"
    echo "  help              Show this help message"
}

cmd_sync_git() {
    if [ ! -f "$MEMORY_FILE" ]; then
        echo "Error: Memory file $MEMORY_FILE not found." >&2
        exit 1
    fi
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    local commit
    commit=$(git log -n 1 --format="%h" 2>/dev/null || echo "none")

    # Update memory.md using sed
    sed -i -E "s|- \*\*Active Branch\*\*: .*|- **Active Branch**: $branch|" "$MEMORY_FILE"
    sed -i -E "s|- \*\*Last Commit Reference\*\*: .*|- **Last Commit Reference**: $commit|" "$MEMORY_FILE"
    echo "Synchronized: Branch=$branch, Commit=$commit in $MEMORY_FILE"
}

cmd_lock() {
    local module="${1:-}"
    if [ -z "$module" ]; then
        echo "Error: Please specify a module name to lock." >&2
        exit 1
    fi
    mkdir -p "$LOCKS_DIR"
    # Replace slashes with underscores for nested monorepo paths
    local lock_name="${module//\//_}"
    local lockfile="$LOCKS_DIR/$lock_name.lock"
    if [ -f "$lockfile" ]; then
        echo "Error: Module '$module' is already locked!" >&2
        cat "$lockfile" >&2
        exit 1
    fi

    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    cat << INNER_EOF > "$lockfile"
Branch: $branch
Owner: Agent
Timestamp: $timestamp
INNER_EOF
    echo "Acquired lock for module '$module' at $lockfile"
}

cmd_unlock() {
    local module="${1:-}"
    if [ -z "$module" ]; then
        echo "Error: Please specify a module name to unlock." >&2
        exit 1
    fi
    # Replace slashes with underscores for nested monorepo paths
    local lock_name="${module//\//_}"
    local lockfile="$LOCKS_DIR/$lock_name.lock"
    if [ ! -f "$lockfile" ]; then
        echo "Warning: Module '$module' is not locked." >&2
        exit 0
    fi
    rm -f "$lockfile"
    echo "Released lock for module '$module'"
}

cmd_build() {
    local subprojects_file=".agents/subprojects.sh"
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        echo "Monorepo detected. Running build compilation..."
        local failed=0
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local build_cmd=$(echo "$sp" | cut -d'|' -f3)
            echo "  Building $path ($build_cmd)..."
            if ! (cd "$path" && eval "$build_cmd"); then
                echo "  [FAIL] Build failed in $path" >&2
                failed=1
            fi
        done
        return $failed
    else
        # Fallback to project_rules build command
        local build_line=$(grep "Build validation" .agents/project_rules.md || echo "")
        local build_cmd=$(echo "$build_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        if [ -n "$build_cmd" ] && [ "$build_cmd" != "echo 'No build command needed'" ]; then
            eval "$build_cmd"
        else
            echo "No build configuration found."
        fi
    fi
}

cmd_lint() {
    local subprojects_file=".agents/subprojects.sh"
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        local changed_files=""
        changed_files=$(git diff --cached --name-only 2>/dev/null || echo "")
        local failed=0
        local run_all=0
        if [ -z "$changed_files" ]; then
            run_all=1
            echo "No staged changes detected. Running linter on all monorepo modules..."
        else
            echo "Analyzing staged file boundaries for monorepo-aware linting..."
        fi
        
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local lint_cmd=$(echo "$sp" | cut -d'|' -f5)
            local should_run=$run_all
            if [ "$should_run" = "0" ]; then
                if echo "$changed_files" | grep -q "^$path/"; then
                    should_run=1
                fi
            fi
            if [ "$should_run" = "1" ]; then
                echo "  Linting $path ($lint_cmd)..."
                if ! (cd "$path" && eval "$lint_cmd"); then
                    echo "  [FAIL] Linter errors found in $path" >&2
                    failed=1
                fi
            else
                echo "  Skipping $path (no staged modifications)."
            fi
        done
        return $failed
    else
        # Fallback to project_rules linter
        local linter_line=$(grep "Linter command" .agents/project_rules.md || echo "")
        local linter_cmd=$(echo "$linter_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        if [ -n "$linter_cmd" ] && [ "$linter_cmd" != "echo 'No linter found'" ]; then
            eval "$linter_cmd"
        else
            echo "No linter configuration found."
        fi
    fi
}

cmd_test() {
    local subprojects_file=".agents/subprojects.sh"
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        local changed_files=""
        changed_files=$(git diff --cached --name-only 2>/dev/null || echo "")
        local failed=0
        local run_all=0
        if [ -z "$changed_files" ]; then
            run_all=1
            echo "No staged changes detected. Running tests on all monorepo modules..."
        else
            echo "Analyzing staged file boundaries for monorepo-aware testing..."
        fi
        
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local test_cmd=$(echo "$sp" | cut -d'|' -f4)
            local should_run=$run_all
            if [ "$should_run" = "0" ]; then
                if echo "$changed_files" | grep -q "^$path/"; then
                    should_run=1
                fi
            fi
            if [ "$should_run" = "1" ]; then
                echo "  Testing $path ($test_cmd)..."
                if ! (cd "$path" && eval "$test_cmd"); then
                    echo "  [FAIL] Testing suite failed in $path" >&2
                    failed=1
                fi
            else
                echo "  Skipping $path (no staged modifications)."
            fi
        done
        return $failed
    else
        # Fallback to project_rules test runner
        local test_line=$(grep "Test runner command" .agents/project_rules.md || echo "")
        local test_runner=$(echo "$test_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        if [ -n "$test_runner" ] && [ "$test_runner" != "echo 'No test suite found'" ]; then
            eval "$test_runner"
        else
            echo "No test runner configuration found."
        fi
    fi
}

cmd_archive() {
    if [ ! -f "$MEMORY_FILE" ]; then
        echo "Error: Memory file $MEMORY_FILE not found." >&2
        exit 1
    fi
    mkdir -p "$ARCHIVE_DIR"
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
    # replace slashes in branch name to avoid path issues
    branch_clean=${branch//\//_}
    local archive_file="$ARCHIVE_DIR/sprint_${branch_clean}.md"

    echo "Archiving tasks to $archive_file..."
    
    # Extract checklist from memory.md
    sed -n '/### Sprint Tasks Checklist/,/---/p' "$MEMORY_FILE" | grep -v -- '---' > "$archive_file"

    # Relocate workflow and PR review files to a branch-specific subdirectory
    local branch_archive_dir="$ARCHIVE_DIR/sprint_${branch_clean}"
    mkdir -p "$branch_archive_dir"
    echo "Archiving workflow and PR review files to $branch_archive_dir..."
    find .agents/workflows -maxdepth 1 -name "task_*.md" -exec mv {} "$branch_archive_dir/" \; 2>/dev/null || true
    find .agents/workflows -maxdepth 1 -name "pr_review_*.md" -exec mv {} "$branch_archive_dir/" \; 2>/dev/null || true


    # Reset checklist in memory.md
    local start_line
    start_line=$(grep -n "### Sprint Tasks Checklist" "$MEMORY_FILE" | cut -d: -f1)
    if [ -z "$start_line" ]; then
        echo "Error: Could not locate checklist section in $MEMORY_FILE" >&2
        exit 1
    fi

    local end_line
    end_line=$(tail -n +$start_line "$MEMORY_FILE" | grep -n "^---" | head -n 1 | cut -d: -f1)
    if [ -z "$end_line" ]; then
        end_line=$(wc -l < "$MEMORY_FILE")
    else
        end_line=$((start_line + end_line - 1))
    fi

    local temp_file
    temp_file=$(mktemp)
    head -n "$start_line" "$MEMORY_FILE" > "$temp_file"
    cat << 'INNER_EOF' >> "$temp_file"
- [ ] Implement core logic
- [ ] Write unit tests
- [ ] Verify build and tests pass
INNER_EOF
    tail -n +"$end_line" "$MEMORY_FILE" >> "$temp_file"
    mv "$temp_file" "$MEMORY_FILE"
    echo "Checklist reset successfully."
}

cmd_init() {
    echo "=========================================================="
    echo "  Antigravity Agent Core - Workspace Initialization"
    echo "=========================================================="
    
    local project_name="${2:-}"
    local tech_stack="${3:-}"
    local arch_pattern="${4:-}"
    local db_orm="${5:-}"
    local env_vars="${6:-}"
    local scaffold=""
    local be_choice="1"
    local be_arch_choice="2"
    local fe_choice="1"
    local fe_arch_choice="2"
    local gen_docker=""

    if [ -z "$project_name" ]; then
        read -p "Enter Project Name (default: My Project): " project_name
        if [ -z "$project_name" ]; then project_name="My Project"; fi
    fi
    
    if [ -z "$tech_stack" ]; then
        echo "Select Technology Stack:"
        echo "  [1] Next.js (TypeScript, Tailwind, App Router) [Recommended]"
        echo "  [2] Go Gin (Clean Architecture REST API)"
        echo "  [3] FastAPI (Python REST API with pytest)"
        echo "  [4] Node/TypeScript (Generic Node App)"
        echo "  [5] Go (Generic Main App)"
        echo "  [6] Python (Generic Script)"
        echo "  [7] Monorepo (Turborepo: Next.js Frontend + Go Gin Backend)"
        echo "  [8] Custom Multi-Project / Separate Apps (e.g. apps/backend + apps/frontend)"
        read -p "Select choice [1-8] (default: 1): " stack_choice
        case "$stack_choice" in
            2) tech_stack="Go Gin" ;;
            3) tech_stack="FastAPI" ;;
            4) tech_stack="Node/TypeScript" ;;
            5) tech_stack="Go" ;;
            6) tech_stack="Python" ;;
            7) tech_stack="Monorepo" ;;
            8) tech_stack="Multi-Project" ;;
            1|"") tech_stack="Next.js" ;;
            *) tech_stack="$stack_choice" ;;
        esac
    fi

    if [ "$tech_stack" = "Multi-Project" ]; then
        echo ""
        echo "--- Configure Backend Application ---"
        echo "  [1] NestJS (TypeScript)"
        echo "  [2] FastAPI (Python)"
        echo "  [3] Go Gin"
        echo "  [4] None"
        read -p "Select Backend Choice [1-4] (default: 1): " be_choice
        if [ -z "$be_choice" ]; then be_choice="1"; fi

        if [ "$be_choice" != "4" ]; then
            echo "Configure Backend Architecture:"
            echo "  [1] Hexagonal Architecture (Ports & Adapters)"
            echo "  [2] Clean Architecture"
            echo "  [3] Standard MVC / Modular"
            read -p "Select Architecture [1-3] (default: 2): " be_arch_choice
            if [ -z "$be_arch_choice" ]; then be_arch_choice="2"; fi
        fi

        echo ""
        echo "--- Configure Frontend Application ---"
        echo "  [1] Next.js (TypeScript)"
        echo "  [2] React SPA (Vite)"
        echo "  [3] Laravel Blade / PHP HTML"
        echo "  [4] None"
        read -p "Select Frontend Choice [1-4] (default: 1): " fe_choice
        if [ -z "$fe_choice" ]; then fe_choice="1"; fi

        if [ "$fe_choice" != "4" ]; then
            echo "Configure Frontend Architecture:"
            echo "  [1] Atomic Design"
            echo "  [2] Standard Components / App Router Layout"
            read -p "Select Architecture [1-2] (default: 2): " fe_arch_choice
            if [ -z "$fe_arch_choice" ]; then fe_arch_choice="2"; fi
        fi
        
        arch_pattern="Decoupled / Distributed Architecture"
        db_orm="None"
        env_vars="PORT"
    fi

    # Auto-suggest architecture based on stack
    local default_arch="MVC"
    if [ "$tech_stack" = "Next.js" ]; then
        default_arch="App Router"
    elif [ "$tech_stack" = "Go Gin" ]; then
        default_arch="Clean Architecture"
    elif [ "$tech_stack" = "FastAPI" ]; then
        default_arch="Modular REST"
    elif [ "$tech_stack" = "Monorepo" ]; then
        default_arch="Decoupled / Distributed"
    fi

    if [ -z "$arch_pattern" ]; then
        read -p "Enter Architectural Pattern (default: $default_arch): " arch_pattern
        if [ -z "$arch_pattern" ]; then arch_pattern="$default_arch"; fi
    fi

    # Auto-suggest env vars based on stack
    local default_env="PORT"
    if [ "$tech_stack" = "Go Gin" ] || [ "$tech_stack" = "FastAPI" ]; then
        default_env="PORT,ENV"
    elif [ "$tech_stack" = "Next.js" ]; then
        default_env="PORT"
    fi

    if [ -z "$db_orm" ]; then
        read -p "Enter Database/ORM (e.g. Prisma, PostgreSQL, None) (default: None): " db_orm
        if [ -z "$db_orm" ]; then db_orm="None"; fi
    fi

    if [ -z "$env_vars" ]; then
        read -p "Enter config variables (comma-separated) (default: $default_env): " env_vars
        if [ -z "$env_vars" ]; then env_vars="$default_env"; fi
    fi

    if [ -z "${7:-}" ]; then
        read -p "Scaffold initial project folders? (y/n) (default: y): " scaffold
        if [ -z "$scaffold" ]; then scaffold="y"; fi
    else
        scaffold="${7:-}"
    fi

    if [ -z "${8:-}" ]; then
        read -p "Generate Dockerfiles and docker-compose.yml? (y/n) (default: y): " gen_docker
        if [ -z "$gen_docker" ]; then gen_docker="y"; fi
    else
        gen_docker="${8:-}"
    fi

    # Initialize Git if not present
    if [ ! -d .git ]; then
        echo "Initializing Git repository..."
        git init
        git branch -m main
    fi

    # Install Git hooks (pre-commit & post-commit)
    mkdir -p .git/hooks
    if [ -f .agents/hooks/pre-commit ]; then
        cp .agents/hooks/pre-commit .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        echo "Git pre-commit hook installed."
    fi
    if [ -f .agents/hooks/post-commit ]; then
        cp .agents/hooks/post-commit .git/hooks/post-commit
        chmod +x .git/hooks/post-commit
        echo "Git post-commit hook installed."
    fi
    if [ -f .agents/hooks/commit-msg ]; then
        cp .agents/hooks/commit-msg .git/hooks/commit-msg
        chmod +x .git/hooks/commit-msg
        echo "Git commit-msg hook installed."
    fi

    # Scaffolding folders if requested
    if [ "$scaffold" = "y" ] || [ "$scaffold" = "yes" ]; then
        echo "Scaffolding directory structure..."
        
        if [ "$tech_stack" = "Next.js" ]; then
            if [[ "$arch_pattern" =~ "Atomic" || "$arch_pattern" =~ "atomic" ]]; then
                mkdir -p src/app src/components/atoms src/components/molecules src/components/organisms src/components/templates src/lib tests
            elif [[ "$arch_pattern" =~ "Clean" || "$arch_pattern" =~ "clean" ]]; then
                mkdir -p src/app src/core/entities src/core/usecases src/infrastructure/db src/infrastructure/api src/lib tests
            else
                mkdir -p src/app src/components src/lib tests
            fi
            # Write package.json
            cat << 'JSON_EOF' > package.json
{
  "name": "nextjs-boilerplate",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "dependencies": {
    "next": "^14.2.3",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/node": "^20.12.12",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "typescript": "^5.4.5",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.3",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.4"
  }
}
JSON_EOF
            # Write next.config.js
            cat << 'JS_EOF' > next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
JS_EOF
            # Write tailwind.config.js
            cat << 'JS_EOF' > tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
JS_EOF
            # Write postcss.config.js
            cat << 'JS_EOF' > postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
JS_EOF
            # Write tsconfig.json
            cat << 'JSON_EOF' > tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
JSON_EOF
            # Write jest.config.js
            cat << 'JS_EOF' > jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.ts'],
};
JS_EOF
            # Write src/app/globals.css
            cat << 'CSS_EOF' > src/app/globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  color-scheme: dark;
}

body {
  margin: 0;
  padding: 0;
  background-color: #020617;
  color: #f8fafc;
}
CSS_EOF
            # Write src/app/layout.tsx
            cat << 'TSX_EOF' > src/app/layout.tsx
import React from 'react';
import './globals.css';

export const metadata = {
  title: 'Antigravity Next.js Boilerplate',
  description: 'Scaffolded Next.js workspace for AI software agents',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
TSX_EOF
            # Write src/app/page.tsx
            cat << 'TSX_EOF' > src/app/page.tsx
import React from 'react';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans">
      <div className="max-w-4xl w-full text-center space-y-8">
        <header className="space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-semibold tracking-wide animate-pulse">
            🚀 Antigravity Workspace Active
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            Antigravity Next.js Boilerplate
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Your production-ready Next.js application, scaffolded and pre-configured for seamless development with AI coding agents.
          </p>
        </header>

        <main className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">⚡ App Router</h2>
            <p className="text-slate-400 text-sm">
              Scaffolded with React Server Components, layout sharing, and clean directory structure inside <code className="text-indigo-400">src/app</code>.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">🎨 Styling & UI</h2>
            <p className="text-slate-400 text-sm">
              Pre-integrated with Tailwind CSS, custom fonts, CSS variables, and modern dark-mode aesthetics ready for immediate extension.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-pink-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">🛡️ AI Agent Guard</h2>
            <p className="text-slate-400 text-sm">
              Wrapped inside Antigravity's cognitive alignment gates (automated pre-commit validators, secret scanning, and memory sync).
            </p>
          </div>
        </main>

        <footer className="text-slate-500 text-sm border-t border-slate-900 pt-8 mt-12 flex justify-between items-center">
          <div> Muhammad Rafael Ghifari &copy; 2026</div>
          <div className="flex gap-4">
            <a href="https://github.com/rafaelghif/antigravity-agents" target="_blank" rel="noopener noreferrer" className="hover:text-indigo-400 transition-colors">GitHub Repository</a>
            <a href="/api/health" className="hover:text-indigo-400 transition-colors">API Health Check</a>
          </div>
        </footer>
      </div>
    </div>
  );
}
TSX_EOF
            # Write src/app/api/health/route.ts
            mkdir -p src/app/api/health
            cat << 'TS_EOF' > src/app/api/health/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'HEALTHY',
    timestamp: new Date().toISOString(),
    system: 'Antigravity Workspace Core',
  });
}
TS_EOF
            # Write tests/health.test.ts
            cat << 'TS_EOF' > tests/health.test.ts
describe('Next.js Boilerplate Test Suite', () => {
  it('should pass initial unit test check', () => {
    expect(true).toBe(true);
  });
});
TS_EOF
            echo "Scaffolded Next.js application template successfully!"

        elif [ "$tech_stack" = "Go Gin" ]; then
            if [[ "$arch_pattern" =~ "Hexagonal" || "$arch_pattern" =~ "hexagonal" || "$arch_pattern" =~ "Ports" || "$arch_pattern" =~ "ports" ]]; then
                mkdir -p src/cmd/server src/internal/core/domain src/internal/core/ports src/internal/adapters/in/web src/internal/adapters/out/db src/internal/config tests
            elif [[ "$arch_pattern" =~ "Clean" || "$arch_pattern" =~ "clean" ]]; then
                mkdir -p src/cmd/server src/internal/domain/entity src/internal/domain/usecase src/internal/adapter/controller src/internal/adapter/repository src/internal/infrastructure/db src/internal/config tests
            else
                mkdir -p src/cmd/server src/internal/model src/internal/controller src/internal/view src/internal/config tests
            fi
            # Write go.mod
            cat << 'GO_EOF' > go.mod
module project

go 1.20

require (
	github.com/gin-gonic/gin v1.9.1
)
GO_EOF
            # Write src/cmd/server/main.go
            cat << 'GO_EOF' > src/cmd/server/main.go
package main

import (
	"fmt"
	"log"
	"net/http"
	"project/src/internal/config"
	"project/src/internal/controller"

	"github.com/gin-gonic/gin"
)

func main() {
	cfg := config.LoadConfig()

	if cfg.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()
	r.Use(gin.Recovery())

	healthCtrl := controller.NewHealthController()

	api := r.Group("/api")
	{
		api.GET("/health", healthCtrl.Check)
	}

	r.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Welcome to Antigravity Go Gin Boilerplate!",
			"status":  "Active",
		})
	})

	addr := fmt.Sprintf(":%s", cfg.Port)
	log.Printf("Server starting on port %s...", cfg.Port)
	if err := r.Run(addr); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}
GO_EOF
            # Write src/internal/config/config.go
            cat << 'GO_EOF' > src/internal/config/config.go
package config

import "os"

type Config struct {
	Port string
	Env  string
}

func LoadConfig() *Config {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	env := os.Getenv("ENV")
	if env == "" {
		env = "development"
	}
	return &Config{
		Port: port,
		Env:  env,
	}
}
GO_EOF
            # Write src/internal/controller/health_controller.go
            cat << 'GO_EOF' > src/internal/controller/health_controller.go
package controller

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
)

type HealthController struct{}

func NewHealthController() *HealthController {
	return &HealthController{}
}

func (h *HealthController) Check(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "HEALTHY",
		"timestamp": time.Now().Format(time.RFC3339),
		"system":    "Antigravity Go Gin Core",
	})
}
GO_EOF
            # Write tests/health_test.go
            cat << 'GO_EOF' > tests/health_test.go
package tests

import (
	"net/http"
	"net/http/httptest"
	"project/src/internal/controller"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestHealthCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.Default()
	healthCtrl := controller.NewHealthController()
	r.GET("/api/health", healthCtrl.Check)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/health", nil)
	r.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status code 200, got %d", w.Code)
	}
}
GO_EOF
            # Write Makefile
            cat << 'MAKE_EOF' > Makefile
.PHONY: run test build clean

run:
	go run src/cmd/server/main.go

test:
	go test -v ./tests/...

build:
	go build -o bin/server src/cmd/server/main.go

clean:
	rm -rf bin/
MAKE_EOF
            echo "Scaffolded Go Gin application template successfully!"

        elif [ "$tech_stack" = "FastAPI" ]; then
            if [[ "$arch_pattern" =~ "Hexagonal" || "$arch_pattern" =~ "hexagonal" || "$arch_pattern" =~ "Ports" || "$arch_pattern" =~ "ports" ]]; then
                mkdir -p src/app/domain src/app/ports src/app/adapters/in/api src/app/adapters/out/db src/app/core tests
            elif [[ "$arch_pattern" =~ "Clean" || "$arch_pattern" =~ "clean" ]]; then
                mkdir -p src/app/entities src/app/usecases src/app/controllers src/app/infrastructure/db src/app/core tests
            else
                mkdir -p src/app/core src/app/api/endpoints tests
            fi
            # Write requirements.txt
            cat << 'TXT_EOF' > requirements.txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.4
pytest>=8.1.1
httpx>=0.27.0
TXT_EOF
            # Write pyproject.toml
            cat << 'TOML_EOF' > pyproject.toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
TOML_EOF
            # Write src/app/main.py
            cat << 'PY_EOF' > src/app/main.py
import uvicorn
from fastapi import FastAPI
from src.app.core.config import settings
from src.app.api.endpoints import health

app = FastAPI(
    title="Antigravity FastAPI Boilerplate",
    description="Production-ready FastAPI setup for AI software agents",
    version="1.0.0",
)

app.include_router(health.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Antigravity FastAPI Boilerplate!",
        "status": "Active",
    }

if __name__ == "__main__":
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
PY_EOF
            # Write src/app/core/config.py
            cat << 'PY_EOF' > src/app/core/config.py
import os

class Settings:
    PORT: int = int(os.getenv("PORT", 8000))
    ENV: str = os.getenv("ENV", "development")

settings = Settings()
PY_EOF
            # Write src/app/api/endpoints/health.py
            cat << 'PY_EOF' > src/app/api/endpoints/health.py
from datetime import datetime
from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["system"])
def check_health():
    return {
        "status": "HEALTHY",
        "timestamp": datetime.utcnow().isoformat(),
        "system": "Antigravity FastAPI Core",
    }
PY_EOF
            # Write tests/test_health.py
            cat << 'PY_EOF' > tests/test_health.py
from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "timestamp" in data
    assert data["system"] == "Antigravity FastAPI Core"
PY_EOF
            echo "Scaffolded FastAPI application template successfully!"

        elif [ "$tech_stack" = "Monorepo" ]; then
            # Scaffold Turborepo monorepo structure
            mkdir -p apps/web apps/api packages/shared

            # Write root pnpm-workspace.yaml
            cat << 'YAML_EOF' > pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
YAML_EOF

            # Write root turbo.json
            cat << 'JSON_EOF' > turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**", "bin/**"]
    },
    "lint": {},
    "test": {},
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
JSON_EOF

            # Write root package.json
            cat << 'JSON_EOF' > package.json
{
  "name": "monorepo-root",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
JSON_EOF

            # ----------------------------------------------------
            # 1. Apps: apps/web (Next.js)
            # ----------------------------------------------------
            mkdir -p apps/web/src/app apps/web/src/components apps/web/src/lib apps/web/tests
            
            # package.json for web app
            cat << 'JSON_EOF' > apps/web/package.json
{
  "name": "web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "dependencies": {
    "next": "^14.2.3",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@monorepo/shared": "workspace:*"
  },
  "devDependencies": {
    "@types/node": "^20.12.12",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "typescript": "^5.4.5",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.3",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.4"
  }
}
JSON_EOF

            # next.config.js for web app
            cat << 'JS_EOF' > apps/web/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};
module.exports = nextConfig;
JS_EOF

            # tailwind.config.js for web app
            cat << 'JS_EOF' > apps/web/tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
JS_EOF

            # postcss.config.js for web app
            cat << 'JS_EOF' > apps/web/postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
JS_EOF

            # tsconfig.json for web app
            cat << 'JSON_EOF' > apps/web/tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
JSON_EOF

            # jest.config.js for web app
            cat << 'JS_EOF' > apps/web/jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.ts'],
};
JS_EOF

            # globals.css for web app
            cat << 'CSS_EOF' > apps/web/src/app/globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;
:root {
  color-scheme: dark;
}
body {
  margin: 0;
  padding: 0;
  background-color: #020617;
  color: #f8fafc;
}
CSS_EOF

            # layout.tsx for web app
            cat << 'TSX_EOF' > apps/web/src/app/layout.tsx
import React from 'react';
import './globals.css';
export const metadata = {
  title: 'Antigravity Monorepo Frontend',
  description: 'Scaffolded Turborepo Frontend Web Application',
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
TSX_EOF

            # page.tsx for web app
            cat << 'TSX_EOF' > apps/web/src/app/page.tsx
import React from 'react';
import { appName, version } from '@monorepo/shared';

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans">
      <div className="max-w-4xl w-full text-center space-y-8">
        <header className="space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-semibold tracking-wide animate-pulse">
            🚀 Antigravity Monorepo Active
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            {appName}
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Monorepo Web Client (v{version}) running alongside an isolated Go Gin backend service.
          </p>
        </header>
        <main className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">⚡ Next.js</h2>
            <p className="text-slate-400 text-sm">
              Frontend web client running Next.js App Router inside <code className="text-indigo-400">apps/web</code>.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">🐹 Go Gin API</h2>
            <p className="text-slate-400 text-sm">
              Isolated REST API backend service with Go Gin inside <code className="text-purple-400">apps/api</code>.
            </p>
          </div>
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-pink-500/30 transition-all duration-300">
            <h2 className="text-xl font-bold text-slate-100 mb-2">📦 Shared Workspace</h2>
            <p className="text-slate-400 text-sm">
              Shared package containing index exports, interfaces, and types inside <code className="text-pink-400">packages/shared</code>.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
TSX_EOF

            # health route for web app
            mkdir -p apps/web/src/app/api/health
            cat << 'TS_EOF' > apps/web/src/app/api/health/route.ts
import { NextResponse } from 'next/server';
export async function GET() {
  return NextResponse.json({
    status: 'HEALTHY',
    timestamp: new Date().toISOString(),
    system: 'Antigravity Monorepo Frontend',
  });
}
TS_EOF

            # tests for web app
            cat << 'TS_EOF' > apps/web/tests/health.test.ts
describe('Monorepo Web Client Test Suite', () => {
  it('should pass initial tests', () => {
    expect(true).toBe(true);
  });
});
TS_EOF

            # ----------------------------------------------------
            # 2. Apps: apps/api (Go Gin)
            # ----------------------------------------------------
            mkdir -p apps/api/src/cmd/server apps/api/src/internal/controller apps/api/src/internal/config apps/api/tests

            # go.mod for api app
            cat << 'GO_EOF' > apps/api/go.mod
module api

go 1.20

require (
	github.com/gin-gonic/gin v1.9.1
)
GO_EOF

            # main.go for api app
            cat << 'GO_EOF' > apps/api/src/cmd/server/main.go
package main
import (
	"fmt"
	"log"
	"net/http"
	"api/src/internal/config"
	"api/src/internal/controller"
	"github.com/gin-gonic/gin"
)
func main() {
	cfg := config.LoadConfig()
	if cfg.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}
	r := gin.Default()
	r.Use(gin.Recovery())
	healthCtrl := controller.NewHealthController()
	api := r.Group("/api")
	{
		api.GET("/health", healthCtrl.Check)
	}
	r.GET("/", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Welcome to Antigravity Go Gin Backend in Monorepo!",
			"status":  "Active",
		})
	})
	addr := fmt.Sprintf(":%s", cfg.Port)
	log.Printf("Backend starting on port %s...", cfg.Port)
	if err := r.Run(addr); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}
GO_EOF

            # config.go for api app
            cat << 'GO_EOF' > apps/api/src/internal/config/config.go
package config
import "os"
type Config struct {
	Port string
	Env  string
}
func LoadConfig() *Config {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	env := os.Getenv("ENV")
	if env == "" {
		env = "development"
	}
	return &Config{
		Port: port,
		Env:  env,
	}
}
GO_EOF

            # health_controller.go for api app
            cat << 'GO_EOF' > apps/api/src/internal/controller/health_controller.go
package controller
import (
	"net/http"
	"time"
	"github.com/gin-gonic/gin"
)
type HealthController struct{}
func NewHealthController() *HealthController {
	return &HealthController{}
}
func (h *HealthController) Check(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "HEALTHY",
		"timestamp": time.Now().Format(time.RFC3339),
		"system":    "Antigravity Monorepo Backend API",
	})
}
GO_EOF

            # test for api app
            cat << 'GO_EOF' > apps/api/tests/health_test.go
package tests
import (
	"net/http"
	"net/http/httptest"
	"api/src/internal/controller"
	"testing"
	"github.com/gin-gonic/gin"
)
func TestHealthCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.Default()
	healthCtrl := controller.NewHealthController()
	r.GET("/api/health", healthCtrl.Check)
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/health", nil)
	r.ServeHTTP(w, req)
	if w.Code != http.StatusOK {
		t.Errorf("Expected status code 200, got %d", w.Code)
	}
}
GO_EOF

            # Makefile for api app
            cat << 'MAKE_EOF' > apps/api/Makefile
.PHONY: run test build clean
run:
	go run src/cmd/server/main.go
test:
	go test -v ./tests/...
build:
	go build -o bin/server src/cmd/server/main.go
clean:
	rm -rf bin/
MAKE_EOF

            # ----------------------------------------------------
            # 3. Packages: packages/shared
            # ----------------------------------------------------
            cat << 'JSON_EOF' > packages/shared/package.json
{
  "name": "@monorepo/shared",
  "version": "1.0.0",
  "private": true,
  "main": "index.js",
  "types": "index.d.ts"
}
JSON_EOF

            cat << 'JS_EOF' > packages/shared/index.js
module.exports = {
  appName: "Antigravity Monorepo",
  version: "1.0.0"
};
JS_EOF

            cat << 'TS_EOF' > packages/shared/index.d.ts
export const appName: string;
export const version: string;
TS_EOF

            echo "Scaffolded Monorepo application template successfully!"

        elif [ "$tech_stack" = "Multi-Project" ]; then
            # Scaffold Custom Multi-Project / Separate Apps layout
            mkdir -p apps/backend apps/frontend
            
            echo "Scaffolding Custom Multi-Project layout..."

            # 1. Scaffold Backend App
            if [ "$be_choice" = "1" ]; then
                # NestJS Boilerplate
                echo "  Scaffolding NestJS backend..."
                mkdir -p apps/backend/src
                
                # Check Architecture
                if [ "$be_arch_choice" = "1" ]; then
                    # Hexagonal Architecture
                    mkdir -p apps/backend/src/core/domain apps/backend/src/core/ports apps/backend/src/adapters/in/web apps/backend/src/adapters/out/persistence
                elif [ "$be_arch_choice" = "2" ]; then
                    # Clean Architecture
                    mkdir -p apps/backend/src/entities apps/backend/src/usecases apps/backend/src/controllers apps/backend/src/infrastructure/db
                else
                    # Standard NestJS Modular
                    mkdir -p apps/backend/src/modules apps/backend/src/common
                fi
                
                cat << 'JSON_EOF' > apps/backend/package.json
{
  "name": "backend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "lint": "eslint 'src/**/*.ts'",
    "test": "jest"
  },
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "reflect-metadata": "^0.1.13",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.0.0",
    "@nestjs/testing": "^10.0.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
JSON_EOF

                cat << 'TS_EOF' > apps/backend/src/main.ts
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(process.env.PORT || 3000);
}
bootstrap();
TS_EOF

                cat << 'TS_EOF' > apps/backend/src/app.module.ts
import { Module } from '@nestjs/common';

@Module({
  imports: [],
  controllers: [],
  providers: [],
})
export class AppModule {}
TS_EOF

            elif [ "$be_choice" = "2" ]; then
                # FastAPI Boilerplate
                echo "  Scaffolding FastAPI backend..."
                mkdir -p apps/backend/src/app
                
                if [ "$be_arch_choice" = "1" ]; then
                    # Hexagonal Architecture
                    mkdir -p apps/backend/src/app/domain apps/backend/src/app/ports apps/backend/src/app/adapters/in/api apps/backend/src/app/adapters/out/db apps/backend/src/app/core
                elif [ "$be_arch_choice" = "2" ]; then
                    # Clean Architecture
                    mkdir -p apps/backend/src/app/entities apps/backend/src/app/usecases apps/backend/src/app/controllers apps/backend/src/app/infrastructure/db apps/backend/src/app/core
                else
                    # Standard Modular API
                    mkdir -p apps/backend/src/app/core apps/backend/src/app/api/endpoints
                fi
                
                cat << 'TXT_EOF' > apps/backend/requirements.txt
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.4
pytest>=8.1.1
httpx>=0.27.0
TXT_EOF

                cat << 'PY_EOF' > apps/backend/src/app/main.py
from fastapi import FastAPI

app = FastAPI(title="Antigravity Custom Backend")

@app.get("/")
def read_root():
    return {"message": "Hello from Custom FastAPI Backend!"}
PY_EOF

            elif [ "$be_choice" = "3" ]; then
                # Go Gin Boilerplate
                echo "  Scaffolding Go Gin backend..."
                mkdir -p apps/backend/src/cmd/server
                
                if [ "$be_arch_choice" = "1" ]; then
                    # Hexagonal Architecture
                    mkdir -p apps/backend/src/internal/core/domain apps/backend/src/internal/core/ports apps/backend/src/internal/adapters/in/web apps/backend/src/internal/adapters/out/db apps/backend/src/internal/config
                elif [ "$be_arch_choice" = "2" ]; then
                    # Clean Architecture
                    mkdir -p apps/backend/src/internal/domain/entity apps/backend/src/internal/domain/usecase apps/backend/src/internal/adapter/controller apps/backend/src/internal/adapter/repository apps/backend/src/internal/infrastructure/db apps/backend/src/internal/config
                else
                    # Standard Go Gin MVC
                    mkdir -p apps/backend/src/internal/model apps/backend/src/internal/controller apps/backend/src/internal/view apps/backend/src/internal/config
                fi
                
                cat << 'GO_EOF' > apps/backend/go.mod
module backend

go 1.20

require (
	github.com/gin-gonic/gin v1.9.1
)
GO_EOF

                cat << 'GO_EOF' > apps/backend/src/cmd/server/main.go
package main

import (
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "Hello from Custom Go Gin Backend!",
		})
	})
	r.Run()
}
GO_EOF
            fi

            # 2. Scaffold Frontend App
            if [ "$fe_choice" = "1" ]; then
                # Next.js Boilerplate
                echo "  Scaffolding Next.js frontend..."
                mkdir -p apps/frontend/src/app apps/frontend/src/lib
                
                if [ "$fe_arch_choice" = "1" ]; then
                    # Atomic Design
                    mkdir -p apps/frontend/src/components/atoms apps/frontend/src/components/molecules apps/frontend/src/components/organisms apps/frontend/src/components/templates
                else
                    # Standard Next.js App Router
                    mkdir -p apps/frontend/src/components
                fi
                
                cat << 'JSON_EOF' > apps/frontend/package.json
{
  "name": "frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "dependencies": {
    "next": "^14.2.3",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
JSON_EOF

                cat << 'TSX_EOF' > apps/frontend/src/app/layout.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Antigravity Custom Frontend',
  description: 'Flexible separate frontend application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
TSX_EOF

                cat << 'TSX_EOF' > apps/frontend/src/app/page.tsx
export default function Home() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🚀 Welcome to Antigravity Custom Frontend</h1>
      <p>Running alongside a decoupled backend service in a clean modular layout.</p>
    </main>
  );
}
TSX_EOF

            elif [ "$fe_choice" = "2" ]; then
                # React SPA (Vite) Boilerplate
                echo "  Scaffolding React SPA frontend..."
                mkdir -p apps/frontend/src apps/frontend/public
                
                if [ "$fe_arch_choice" = "1" ]; then
                    # Atomic Design
                    mkdir -p apps/frontend/src/components/atoms apps/frontend/src/components/molecules apps/frontend/src/components/organisms apps/frontend/src/components/templates
                else
                    # Standard React Components
                    mkdir -p apps/frontend/src/components
                fi
                
                cat << 'JSON_EOF' > apps/frontend/package.json
{
  "name": "frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint 'src/**/*.ts'",
    "test": "jest"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
JSON_EOF

                cat << 'HTML_EOF' > apps/frontend/index.html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Antigravity React SPA</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
HTML_EOF

                cat << 'TSX_EOF' > apps/frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
TSX_EOF

                cat << 'TSX_EOF' > apps/frontend/src/App.tsx
import React from 'react';

export default function App() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🚀 Welcome to Antigravity React SPA Frontend</h1>
      <p>Decoupled single-page frontend application.</p>
    </div>
  );
}
TSX_EOF

            elif [ "$fe_choice" = "3" ]; then
                # Laravel Blade / PHP HTML Boilerplate
                echo "  Scaffolding Laravel Blade/HTML frontend..."
                mkdir -p apps/frontend/resources/views apps/frontend/public/css apps/frontend/public/js
                
                cat << 'HTML_EOF' > apps/frontend/resources/views/welcome.blade.php
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity Blade Frontend</title>
    <style>
        body { font-family: sans-serif; padding: 2rem; background-color: #f8fafc; color: #1e293b; }
    </style>
</head>
<body>
    <h1>🚀 Welcome to Antigravity Blade/HTML Frontend</h1>
    <p>Flexible separate frontend application template.</p>
</body>
</html>
HTML_EOF
            fi

            echo "Scaffolded Custom Multi-Project application template successfully!"

        else
            # Generic/Basic Scaffolding Fallback
            mkdir -p src tests config
            if [[ "$tech_stack" =~ "Node" || "$tech_stack" =~ "TypeScript" || "$tech_stack" =~ "TS" ]]; then
                if [ ! -f package.json ]; then
                    cat << 'JSON_EOF' > package.json
{
  "name": "project",
  "version": "1.0.0",
  "description": "",
  "main": "src/index.js",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "lint": "eslint 'src/**/*.ts'"
  },
  "dependencies": {},
  "devDependencies": {}
}
JSON_EOF
                    echo "Created package.json scaffolding"
                fi
            fi
            
            if [[ "$tech_stack" =~ "Go" || "$tech_stack" =~ "Golang" ]]; then
                if [ ! -f go.mod ]; then
                    cat << 'GO_EOF' > go.mod
module project

go 1.20
GO_EOF
                    echo "Created go.mod scaffolding"
                fi
                if [ ! -f src/main.go ]; then
                    cat << 'GO_EOF' > src/main.go
package main

import "fmt"

func main() {
    fmt.Println("Hello, Antigravity!")
}
GO_EOF
                    echo "Created src/main.go template"
                fi
            fi

            if [[ "$tech_stack" =~ "Python" || "$tech_stack" =~ "Py" ]]; then
                if [ ! -f src/main.py ]; then
                    cat << 'PY_EOF' > src/main.py
def main():
    print("Hello, Antigravity!")

if __name__ == "__main__":
    main()
PY_EOF
                    echo "Created src/main.py template"
                fi
            fi
        fi

        if [ "$gen_docker" = "y" ] || [ "$gen_docker" = "yes" ]; then
            echo "Generating Dockerfiles and docker-compose.yml..."
            
            # Helper variables for database
            local db_service=""
            local db_envs=""
            local db_depends=""
            
            local db_lower
            db_lower=$(echo "$db_orm" | tr '[:upper:]' '[:lower:]')
            
            if [[ "$db_lower" =~ "postgres" ]]; then
                db_service=$(cat << 'DB_POSTGRES'
  postgres:
    image: postgres:15-alpine
    container_name: postgres_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_POSTGRES
)
                db_envs="      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres\n      - DB_HOST=postgres\n      - DB_PORT=5432"
                db_depends="    depends_on:\n      postgres:\n        condition: service_healthy"
            elif [[ "$db_lower" =~ "mysql" || "$db_lower" =~ "mariadb" ]]; then
                db_service=$(cat << 'DB_MYSQL'
  mysql:
    image: mysql:8.0
    container_name: mysql_db
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h localhost"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_MYSQL
)
                db_envs="      - DATABASE_URL=mysql://root:root@mysql:3306/db\n      - DB_HOST=mysql\n      - DB_PORT=3306"
                db_depends="    depends_on:\n      mysql:\n        condition: service_healthy"
            elif [[ "$db_lower" =~ "mongo" ]]; then
                db_service=$(cat << 'DB_MONGO'
  mongodb:
    image: mongo:6.0
    container_name: mongodb_db
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    healthcheck:
      test: ["CMD-SHELL", "echo 'db.runCommand(\"ping\")' | mongosh localhost:27017/test --quiet"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_MONGO
)
                db_envs="      - DATABASE_URL=mongodb://mongodb:27017/db\n      - DB_HOST=mongodb\n      - DB_PORT=27017"
                db_depends="    depends_on:\n      mongodb:\n        condition: service_healthy"
            elif [[ "$db_lower" =~ "redis" ]]; then
                db_service=$(cat << 'DB_REDIS'
  redis:
    image: redis:7-alpine
    container_name: redis_cache
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD-SHELL", "redis-cli ping | grep PONG"]
      interval: 5s
      timeout: 5s
      retries: 5
DB_REDIS
)
                db_envs="      - REDIS_URL=redis://redis:6379"
                db_depends="    depends_on:\n      redis:\n        condition: service_healthy"
            fi

            # 1. Monorepo / Multi-Project Scaffolding
            if [ "$tech_stack" = "Monorepo" ] || [ "$tech_stack" = "Multi-Project" ]; then
                local be_dir=""
                local fe_dir=""
                local be_port="3000"
                local fe_port="3000"
                local be_dockerfile=""
                local fe_dockerfile=""
                
                if [ "$tech_stack" = "Monorepo" ]; then
                    be_dir="apps/api"
                    fe_dir="apps/web"
                    be_port="8080" # Go Gin
                    fe_port="3000" # Next.js
                    
                    be_dockerfile=$(cat << 'MONO_BE'
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
MONO_BE
)
                    fe_dockerfile=$(cat << 'MONO_FE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN \
  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  else npm install; \
  fi
COPY . .
RUN \
  if [ -f pnpm-lock.yaml ]; then pnpm run build; \
  else npm run build; \
  fi

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
MONO_FE
)
                else
                    # Multi-Project
                    be_dir="apps/backend"
                    fe_dir="apps/frontend"
                    
                    # Backend Dockerfile selection
                    if [ "$be_choice" = "1" ]; then
                        be_port="3000"
                        be_dockerfile=$(cat << 'MULTI_NEST'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/main"]
MULTI_NEST
)
                    elif [ "$be_choice" = "2" ]; then
                        be_port="8000"
                        be_dockerfile=$(cat << 'MULTI_PY'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
MULTI_PY
)
                    elif [ "$be_choice" = "3" ]; then
                        be_port="8080"
                        be_dockerfile=$(cat << 'MULTI_GO'
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
MULTI_GO
)
                    fi

                    # Frontend Dockerfile selection
                    if [ "$fe_choice" = "1" ]; then
                        fe_port="3000"
                        fe_dockerfile=$(cat << 'MULTI_NEXT'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN \
  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  else npm install; \
  fi
COPY . .
RUN \
  if [ -f pnpm-lock.yaml ]; then pnpm run build; \
  else npm run build; \
  fi

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
MULTI_NEXT
)
                    elif [ "$fe_choice" = "2" ]; then
                        fe_port="80"
                        fe_dockerfile=$(cat << 'MULTI_VITE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
MULTI_VITE
)
                    elif [ "$fe_choice" = "3" ]; then
                        fe_port="80"
                        fe_dockerfile=$(cat << 'MULTI_PHP'
FROM php:8.2-apache
COPY . /var/www/html/
RUN chown -R www-data:www-data /var/www/html
EXPOSE 80
MULTI_PHP
)
                    fi
                fi
                
                # Write Dockerfiles
                if [ -n "$be_dockerfile" ] && [ -d "$be_dir" ]; then
                    echo "$be_dockerfile" > "$be_dir/Dockerfile"
                    echo "  Created $be_dir/Dockerfile"
                fi
                if [ -n "$fe_dockerfile" ] && [ -d "$fe_dir" ]; then
                    echo "$fe_dockerfile" > "$fe_dir/Dockerfile"
                    echo "  Created $fe_dir/Dockerfile"
                fi

                # Build docker-compose services
                local services=""
                if [ -d "$be_dir" ] && [ "$be_choice" != "4" ]; then
                    services="${services}\n  backend:\n    build:\n      context: ./${be_dir}\n    ports:\n      - \"${be_port}:${be_port}\"\n"
                    if [ -n "$db_depends" ]; then
                        services="${services}$(echo -e "$db_depends")\n"
                    fi
                    if [ -n "$db_envs" ]; then
                        services="${services}    environment:\n$(echo -e "$db_envs")\n"
                    fi
                fi
                
                if [ -d "$fe_dir" ] && [ "$fe_choice" != "4" ]; then
                    local host_fe_port="3000"
                    if [ "$be_choice" != "4" ] && [ "$be_port" = "3000" ]; then
                        host_fe_port="3001"
                    fi
                    services="${services}\n  frontend:\n    build:\n      context: ./${fe_dir}\n    ports:\n      - \"${host_fe_port}:${fe_port}\"\n"
                    if [ -d "$be_dir" ] && [ "$be_choice" != "4" ]; then
                        services="${services}    depends_on:\n      backend:\n        condition: service_started\n"
                        services="${services}    environment:\n      - BACKEND_URL=http://backend:${be_port}\n"
                    fi
                fi
                
                if [ -n "$db_service" ]; then
                    services="${services}\n$(echo -e "$db_service")"
                fi
                
                # Write docker-compose.yml
                cat << 'COMPOSE_MULTI' > docker-compose.yml
version: '3.8'

services:
COMPOSE_MULTI
                echo -e "$services" >> docker-compose.yml
                cat << 'COMPOSE_VOLUME' >> docker-compose.yml

volumes:
  pgdata:
  mysql_data:
  mongo_data:
  redis_data:
COMPOSE_VOLUME
                echo "  Created docker-compose.yml at root"

            else
                # 2. Single Project Scaffolding
                local port="3000"
                local dockerfile=""
                
                if [ "$tech_stack" = "Next.js" ]; then
                    port="3000"
                    dockerfile=$(cat << 'SINGLE_NEXT'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
SINGLE_NEXT
)
                elif [ "$tech_stack" = "Go Gin" ] || [ "$tech_stack" = "Go" ]; then
                    port="8080"
                    dockerfile=$(cat << 'SINGLE_GO'
FROM golang:1.20-alpine AS builder
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
SINGLE_GO
)
                elif [ "$tech_stack" = "FastAPI" ] || [ "$tech_stack" = "Python" ]; then
                    port="8000"
                    dockerfile=$(cat << 'SINGLE_PY'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
SINGLE_PY
)
                elif [ "$tech_stack" = "Node/TypeScript" ]; then
                    port="3000"
                    dockerfile=$(cat << 'SINGLE_NODE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
SINGLE_NODE
)
                fi
                
                if [ -n "$dockerfile" ]; then
                    echo "$dockerfile" > Dockerfile
                    echo "  Created Dockerfile"
                fi

                # Build services for docker-compose.yml
                local services="  app:\n    build:\n      context: .\n    ports:\n      - \"${port}:${port}\"\n"
                if [ -n "$db_depends" ]; then
                    services="${services}$(echo -e "$db_depends")\n"
                fi
                if [ -n "$db_envs" ]; then
                    services="${services}    environment:\n$(echo -e "$db_envs")\n"
                fi
                if [ -n "$db_service" ]; then
                    services="${services}\n$(echo -e "$db_service")"
                fi
                
                # Write docker-compose.yml
                cat << 'COMPOSE_SINGLE' > docker-compose.yml
version: '3.8'

services:
COMPOSE_SINGLE
                echo -e "$services" >> docker-compose.yml
                cat << 'COMPOSE_VOLUME' >> docker-compose.yml

volumes:
  pgdata:
  mysql_data:
  mongo_data:
  redis_data:
COMPOSE_VOLUME
                echo "  Created docker-compose.yml"
            fi
        fi
    fi


    # Create .env and .env.example if env_vars exist
    if [ -n "$env_vars" ]; then
        echo "Writing configuration environment variables..."
        IFS=',' read -ra ADDR <<< "$env_vars"
        # Reset files
        > .env.example
        > .env
        for i in "${ADDR[@]}"; do
            echo "$i=" >> .env.example
            echo "$i=" >> .env
        done
        echo "Created .env and .env.example templates"
    fi

    # Run auto-recon to generate the blueprints
    echo "Running autonomous reconnaissance to populate blueprint files..."
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh -f
    fi

    echo "=========================================================="
    echo "Workspace initialized successfully for '$project_name'!"
    echo "=========================================================="
}

cmd_recon() {
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh
    else
        echo "Error: recon.sh not found at .agents/scripts/recon.sh" >&2
        exit 1
    fi
}

cmd_validate() {
    if [ -f .agents/scripts/validate.sh ]; then
        .agents/scripts/validate.sh
    else
        echo "Error: validate.sh not found at .agents/scripts/validate.sh" >&2
        exit 1
    fi
}

cmd_doctor() {
    echo "=========================================================="
    echo "  Antigravity Workspace Doctor Diagnostics"
    echo "=========================================================="
    
    local errors=0
    
    # Check Git Repository
    if [ -d .git ]; then
        echo "  [PASS] Git repository initialized."
    else
        echo "  [FAIL] Git repository not initialized!"
        errors=$((errors + 1))
    fi
    
    # Check Git hooks
    if [ -f .git/hooks/pre-commit ] && [ -x .git/hooks/pre-commit ]; then
        echo "  [PASS] pre-commit Git hook is installed and executable."
    else
        echo "  [WARNING] Git pre-commit hook is missing or not executable."
        echo "            To install: cp .agents/hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit"
    fi
    if [ -f .git/hooks/post-commit ] && [ -x .git/hooks/post-commit ]; then
        echo "  [PASS] post-commit Git hook is installed and executable."
    else
        echo "  [WARNING] Git post-commit hook is missing or not executable."
        echo "            To install: cp .agents/hooks/post-commit .git/hooks/post-commit && chmod +x .git/hooks/post-commit"
    fi
    if [ -f .git/hooks/commit-msg ] && [ -x .git/hooks/commit-msg ]; then
        echo "  [PASS] commit-msg Git hook is installed and executable."
    else
        echo "  [WARNING] Git commit-msg hook is missing or not executable."
        echo "            To install: cp .agents/hooks/commit-msg .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg"
    fi
    
    # Check helper script executability
    if [ -x .agents/scripts/helper.sh ]; then
        echo "  [PASS] helper.sh is executable."
    else
        echo "  [WARNING] helper.sh is not executable."
        chmod +x .agents/scripts/helper.sh
    fi
    
    # Check recon script
    if [ -f .agents/scripts/recon.sh ]; then
        if [ -x .agents/scripts/recon.sh ]; then
            echo "  [PASS] recon.sh is executable."
        else
            echo "  [WARNING] recon.sh is not executable. Auto-correcting..."
            chmod +x .agents/scripts/recon.sh
        fi
    else
        echo "  [FAIL] recon.sh is missing!"
        errors=$((errors + 1))
    fi

    # Check validate script
    if [ -f .agents/scripts/validate.sh ]; then
        if [ -x .agents/scripts/validate.sh ]; then
            echo "  [PASS] validate.sh is executable."
        else
            echo "  [WARNING] validate.sh is not executable. Auto-correcting..."
            chmod +x .agents/scripts/validate.sh
        fi
    else
        echo "  [FAIL] validate.sh is missing!"
        errors=$((errors + 1))
    fi

    # Run validate.sh checks
    if [ -f .agents/scripts/validate.sh ]; then
        echo "----------------------------------------------------------"
        if ! .agents/scripts/validate.sh; then
            errors=$((errors + 1))
        fi
    fi
    
    echo "=========================================================="
    if [ $errors -eq 0 ]; then
        echo "Doctor diagnostics: ALL SYSTEMS HEALTHY"
        exit 0
    else
        echo "Doctor diagnostics: FOUND $errors ERROR(S) / WARNING(S)"
        exit 1
    fi
}

cmd_commit() {
    local no_test_flag="false"
    local stage_files=()
    local type=""
    local scope=""
    local desc=""

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --no-test|--no-verify)
                no_test_flag="true"
                shift
                ;;
            *)
                if [ "$1" = "commit" ]; then
                    shift
                elif [ -z "$type" ]; then
                    type="$1"
                    shift
                elif [ -z "$scope" ]; then
                    scope="$1"
                    shift
                elif [ -z "$desc" ]; then
                    desc="$1"
                    shift
                else
                    stage_files+=("$1")
                    shift
                fi
                ;;
        esac
    done

    # Interactive inputs if parameters are missing
    if [ -z "$type" ]; then
        echo "Choose commit type:"
        echo "  [1] feat:     A new feature"
        echo "  [2] fix:      A bug fix"
        echo "  [3] refactor: A code change that neither fixes a bug nor adds a feature"
        echo "  [4] chore:    Changes to the build process or auxiliary tools and libraries"
        echo "  [5] docs:     Documentation only changes"
        echo "  [6] test:     Adding missing tests or correcting existing tests"
        echo "  [7] perf:     A code change that improves performance"
        read -p "Select number or type string (default: feat): " type_choice
        case "$type_choice" in
            1) type="feat" ;;
            2) type="fix" ;;
            3) type="refactor" ;;
            4) type="chore" ;;
            5) type="docs" ;;
            6) type="test" ;;
            7) type="perf" ;;
            "") type="feat" ;;
            *) type="$type_choice" ;;
        esac
    fi

    if [ -z "$scope" ]; then
        read -p "Enter commit scope (e.g. core, auth, db, shared) (default: core): " scope
        if [ -z "$scope" ]; then scope="core"; fi
    fi

    if [ -z "$desc" ]; then
        read -p "Enter brief description of change: " desc
        if [ -z "$desc" ]; then
            echo "Error: Description cannot be empty." >&2
            exit 1
        fi
    fi

    # Workspace Validation
    echo "Running workspace validation checks..."
    if ! .agents/scripts/validate.sh; then
        echo "Error: Workspace validation failed. Aborting commit." >&2
        exit 1
    fi

    # Linter Execution
    if [ "$no_test_flag" = "false" ]; then
        local linter_cmd=""
        if [ -f .agents/project_rules.md ]; then
            local linter_line
            linter_line=$(grep "Linter command" .agents/project_rules.md || echo "")
            linter_cmd=$(echo "$linter_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        fi

        if [ -n "$linter_cmd" ] && [ "$linter_cmd" != "echo 'No linter found'" ]; then
            echo "Running linter command: $linter_cmd..."
            if ! eval "$linter_cmd"; then
                echo "Error: Linter check failed. Aborting commit." >&2
                exit 1
            fi
            echo "  [PASS] Linter check passed successfully."
        else
            echo "No linter configured in project_rules.md. Skipping linting."
        fi
    else
        echo "Linter check bypassed via --no-test / --no-verify."
    fi

    # Test Execution
    if [ "$no_test_flag" = "false" ]; then
        local test_runner=""
        if [ -f .agents/project_rules.md ]; then
            local test_line
            test_line=$(grep "Test runner command" .agents/project_rules.md || echo "")
            test_runner=$(echo "$test_line" | cut -d':' -f2- | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^`//' -e 's/`$//')
        fi

        if [ -n "$test_runner" ] && [ "$test_runner" != "echo 'No test suite found'" ]; then
            echo "Running test suite: $test_runner..."
            if ! eval "$test_runner"; then
                echo "Error: Test runner suite failed. Aborting commit." >&2
                exit 1
            fi
            echo "  [PASS] All tests passed successfully."
        else
            echo "No test runner configured in project_rules.md. Skipping tests."
        fi
    else
        echo "Test execution bypassed via --no-test / --no-verify."
    fi

    # File Staging
    if [ ${#stage_files[@]} -gt 0 ]; then
        echo "Staging specified files: ${stage_files[*]}..."
        git add "${stage_files[@]}"
    else
        echo "Staging all modified and untracked files..."
        # Check if there are changes to stage
        if [ -n "$(git status --porcelain | grep -v '^\?\? .agents/locks/')" ]; then
            git add -A -- ':!.agents/locks/*'
        fi
    fi

    # Conventional Commit Execution
    local commit_msg="$type($scope): $desc"
    echo "Executing conventional commit: '$commit_msg'..."
    if git commit -m "$commit_msg"; then
        echo "Commit successful."
    else
        echo "Error: Git commit failed." >&2
        exit 1
    fi
}

cmd_migrate() {
    echo "=========================================================="
    echo "  Antigravity Agent Core - Workspace Migration (V1.4.0)"
    echo "=========================================================="

    local backup_suffix=".backup"

    # 1. Back up user-controlled files if they exist
    if [ -f "$MEMORY_FILE" ]; then
        echo "Warning: Existing memory file found. Backing up to ${MEMORY_FILE}${backup_suffix}"
        cp "$MEMORY_FILE" "${MEMORY_FILE}${backup_suffix}"
    fi

    if [ -f ".agents/project_rules.md" ]; then
        echo "Warning: Existing project rules blueprint found. Backing up to .agents/project_rules.md${backup_suffix}"
        cp ".agents/project_rules.md" ".agents/project_rules.md${backup_suffix}"
    fi

    if [ -f ".agents/schema.md" ]; then
        echo "Warning: Existing schema index found. Backing up to .agents/schema.md${backup_suffix}"
        cp ".agents/schema.md" ".agents/schema.md${backup_suffix}"
    fi

    # 2. Ensure directories exist
    echo "Re-creating directory structure..."
    mkdir -p .agents/skills/codebase-recon
    mkdir -p .agents/skills/git-ops
    mkdir -p .agents/skills/test-driven-patch
    mkdir -p .agents/skills/infra-provisioner
    mkdir -p .agents/skills/security-ci-audit
    mkdir -p .agents/skills/code-review
    mkdir -p .agents/skills/impact-analysis
    mkdir -p .agents/workflows
    mkdir -p .agents/archive
    mkdir -p .agents/locks
    mkdir -p .agents/schemas
    mkdir -p .agents/scripts
    mkdir -p .agents/hooks

    # 3. Update Git Hooks
    echo "Updating local Git hooks..."
    if [ -f .agents/hooks/pre-commit ]; then
        cp .agents/hooks/pre-commit .git/hooks/pre-commit
        chmod +x .git/hooks/pre-commit
        echo "  - Installed pre-commit hook"
    fi
    if [ -f .agents/hooks/post-commit ]; then
        cp .agents/hooks/post-commit .git/hooks/post-commit
        chmod +x .git/hooks/post-commit
        echo "  - Installed post-commit hook"
    fi
    if [ -f .agents/hooks/commit-msg ]; then
        cp .agents/hooks/commit-msg .git/hooks/commit-msg
        chmod +x .git/hooks/commit-msg
        echo "  - Installed commit-msg hook"
    fi

    # 4. Update memory.md schema version
    if [ -f "$MEMORY_FILE" ]; then
        echo "Updating memory ledger schema version to 5.0.0..."
        if grep -Fq "Memory Schema Version" "$MEMORY_FILE"; then
            local temp_mem
            temp_mem=$(mktemp)
            sed -E "s|Memory Schema Version\*\*: [0-9]+\.[0-9]+\.[0-9]+|Memory Schema Version**: 5.0.0|" "$MEMORY_FILE" > "$temp_mem"
            mv "$temp_mem" "$MEMORY_FILE"
        else
            # Prepend schema version header if not found
            local temp_mem
            temp_mem=$(mktemp)
            echo -e "# Agent Core Memory\n\n> **Memory Schema Version**: 5.0.0  \n> **Target System**: Antigravity Agent Core\n> **Active Guidelines**: Read [AGENTS.md](file://../AGENTS.md) and [.agents/project_rules.md](file://./project_rules.md) for execution details. Keep this file under 100 lines at all times.\n" > "$temp_mem"
            tail -n +2 "$MEMORY_FILE" >> "$temp_mem"
            mv "$temp_mem" "$MEMORY_FILE"
        fi
    fi

    # 5. Fix .gitignore configuration
    if [ -f ".gitignore" ]; then
        echo "Validating .gitignore compliance..."
        local temp_git
        temp_git=$(mktemp)
        # remove any lines that ignore .agents or AGENTS.md globally
        grep -v -E "^\.agents/?$" .gitignore | grep -v "^AGENTS.md$" > "$temp_git" || true
        # ensure Locks directory is ignored
        if ! grep -E -q "^\.agents/locks/?" "$temp_git"; then
            echo -e "\n# Ignore agent transient locks\n.agents/locks/" >> "$temp_git"
        fi
        mv "$temp_git" ".gitignore"
        echo "  - .gitignore updated."
    else
        echo "Creating default compliant .gitignore..."
        cat << 'GIT_EOF' > .gitignore
# Ignore agent transient locks
.agents/locks/
GIT_EOF
    fi

    # 6. Re-run codebase stack reconstruction (forces regeneration of blueprints)
    echo "Running autonomous stack reconstruction..."
    if [ -f .agents/scripts/recon.sh ]; then
        .agents/scripts/recon.sh -f
    fi

    echo "=========================================================="
    echo "Migration Complete! Workspace successfully upgraded."
    echo "=========================================================="
}

cmd_sync_api() {
    echo "=========================================================="
    echo "Starting API Contract Synchronization..."
    echo "=========================================================="
    
    local subprojects_file=".agents/subprojects.sh"
    local be_path=""
    local fe_path=""
    local be_stack=""
    
    # 1. Detect backend and frontend directories
    if [ -f "$subprojects_file" ]; then
        source "$subprojects_file"
        for sp in "${SUBPROJECTS[@]}"; do
            local path=$(echo "$sp" | cut -d'|' -f1)
            local stack=$(echo "$sp" | cut -d'|' -f2)
            
            # Simple heuristics to identify backend vs frontend
            if [[ "$path" =~ "api" || "$path" =~ "backend" || "$stack" =~ "Go" || "$stack" =~ "Python" ]]; then
                be_path="$path"
                be_stack="$stack"
            elif [[ "$path" =~ "web" || "$path" =~ "frontend" || "$stack" =~ "Next.js" ]]; then
                fe_path="$path"
            fi
        done
    else
        # Fallback search if no subprojects config file
        if [ -d "apps/backend" ]; then be_path="apps/backend"; fi
        if [ -d "apps/frontend" ]; then fe_path="apps/frontend"; fi
        if [ -d "apps/api" ]; then be_path="apps/api"; fi
        if [ -d "apps/web" ]; then fe_path="apps/web"; fi
    fi
    
    # If still not found, search directories
    if [ -z "$be_path" ]; then
        if [ -f "go.mod" ] || [ -f "main.go" ]; then
            be_path="."
            be_stack="Go"
        elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
            be_path="."
            be_stack="Python"
        fi
    fi
    if [ -z "$fe_path" ]; then
        if [ -d "src/app" ] || [ -f "package.json" ]; then
            fe_path="."
        fi
    fi

    if [ -z "$be_path" ]; then
        echo "  [INFO] Backend application path could not be auto-detected. Operating in root fallback mode."
        be_path="."
        be_stack="Unknown"
    fi
    
    echo "  Detected Backend: $be_path ($be_stack)"
    if [ -n "$fe_path" ]; then
        echo "  Detected Frontend: $fe_path"
    fi

    local openapi_file="openapi.json"
    
    # 2. Extract OpenAPI schema from backend
    echo "  Extracting OpenAPI contract schema..."
    
    if [[ "$be_stack" =~ "Python" || -f "$be_path/requirements.txt" || -f "$be_path/pyproject.toml" ]]; then
        # Python / FastAPI extraction
        if [ "$be_path" = "." ]; then
            python3 -c "import json; from src.app.main import app; print(json.dumps(app.openapi()))" > "$openapi_file" 2>/dev/null || \
            python3 -c "import json; from app.main import app; print(json.dumps(app.openapi()))" > "$openapi_file" 2>/dev/null || \
            echo "Failed to extract FastAPI schema. Ensure FastAPI app is importable."
        else
            (cd "$be_path" && python3 -c "import json; from src.app.main import app; print(json.dumps(app.openapi()))" > "../../../$openapi_file" 2>/dev/null || \
            (cd "$be_path" && python3 -c "import json; from app.main import app; print(json.dumps(app.openapi()))" > "../../../$openapi_file" 2>/dev/null)) || \
            echo "Failed to extract FastAPI schema. Ensure FastAPI app is importable."
        fi
    elif [[ "$be_stack" =~ "Go" || -f "$be_path/go.mod" ]]; then
        # Go Swagger check
        if command -v swag &> /dev/null; then
            echo "  Running swag init in $be_path..."
            (cd "$be_path" && swag init -g src/cmd/server/main.go -o . --ot json && cp swagger.json ../../$openapi_file) 2>/dev/null || \
            (cd "$be_path" && swag init -g cmd/server/main.go -o . --ot json && cp swagger.json ../../$openapi_file) 2>/dev/null || \
            echo "Swag command failed. Creating mockup/fallback schema."
        fi
    fi

    # Fallback/Mockup schema if extraction failed or file is empty/missing
    if [ ! -f "$openapi_file" ] || [ ! -s "$openapi_file" ]; then
        echo "  Warning: Schema extraction returned empty. Writing a compliant mock/fallback openapi.json..."
        cat << 'MOCK_OPENAPI' > "$openapi_file"
{
  "openapi": "3.0.0",
  "info": {
    "title": "Antigravity Mock API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "http://localhost:3000"
    }
  ],
  "paths": {
    "/api/users": {
      "get": {
        "operationId": "get_users",
        "responses": {
          "200": {
            "description": "Success",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/User"
                  }
                }
              }
            }
          }
        }
      },
      "post": {
        "operationId": "create_user",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/User"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "Created",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/User"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "User": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
          "id": {
            "type": "integer"
          },
          "name": {
            "type": "string"
          },
          "email": {
            "type": "string"
          }
        }
      }
    }
  }
}
MOCK_OPENAPI
    fi

    # 3. Generate TypeScript API client
    if [ -n "$fe_path" ] && [ -d "$fe_path" ]; then
        local target_client="$fe_path/src/lib/api-client.ts"
        if [ "$fe_path" = "." ] && [ -d "src/app" ]; then
            target_client="src/lib/api-client.ts"
        fi
        
        echo "  Generating TypeScript client wrapper to $target_client..."
        node .agents/scripts/generate-client.js "$openapi_file" "$target_client"
    else
        echo "  Frontend directory not detected. Generated openapi.json is saved in root."
    fi

    echo "=========================================================="
    echo "API Sync Complete!"
    echo "=========================================================="
}

cmd_log_usage() {
    if [ $# -lt 2 ]; then
        echo "Usage: $0 log-usage <token_count>"
        exit 1
    fi
    local count="$2"
    local file=".agents/token_budget.json"
    if [ ! -f "$file" ]; then
        echo "{\"max_token_budget\": 500000, \"current_token_usage\": 0, \"alert_threshold_percent\": 90}" > "$file"
    fi
    if command -v jq >/dev/null 2>&1; then
        local current=$(jq -r '.current_token_usage' "$file")
        local new_usage=$((current + count))
        local temp=$(mktemp)
        jq --argjson usage "$new_usage" '.current_token_usage = $usage' "$file" > "$temp"
        mv "$temp" "$file"
        echo "Logged $count tokens. Total usage: $new_usage."
    else
        # fallback parsing using sed if jq not found
        local current=$(grep -o '"current_token_usage":\s*[0-9]*' "$file" | grep -o '[0-9]*' || echo "0")
        local new_usage=$((current + count))
        sed -i "s/\"current_token_usage\":\s*[0-9]*/\"current_token_usage\": $new_usage/" "$file"
        echo "Logged $count tokens (fallback). Total usage: $new_usage."
    fi
}

# Dispatch command
if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

case "$1" in
    init)
        cmd_init "$@"
        ;;
    recon)
        cmd_recon
        ;;
    validate)
        cmd_validate
        ;;
    doctor)
        cmd_doctor
        ;;
    commit)
        cmd_commit "$@"
        ;;
    sync-git)
        cmd_sync_git
        ;;
    lock)
        cmd_lock "${2:-}"
        ;;
    unlock)
        cmd_unlock "${2:-}"
        ;;
    archive)
        cmd_archive
        ;;
    migrate)
        cmd_migrate
        ;;
    build)
        cmd_build
        ;;
    lint)
        cmd_lint
        ;;
    test)
        cmd_test
        ;;
    sync-api)
        cmd_sync_api
        ;;
    log-usage)
        cmd_log_usage "$@"
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown command: $1" >&2
        show_help
        exit 1
        ;;
esac
