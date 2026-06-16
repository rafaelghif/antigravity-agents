import os
import sys
import shutil
import subprocess
import utils

NEXT_TEMPLATES = {
  "package.json": "{\n  \"name\": \"nextjs-boilerplate\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"dev\": \"next dev\",\n    \"build\": \"next build\",\n    \"start\": \"next start\",\n    \"lint\": \"next lint\",\n    \"test\": \"jest\"\n  },\n  \"dependencies\": {\n    \"next\": \"^14.2.3\",\n    \"react\": \"^18.3.1\",\n    \"react-dom\": \"^18.3.1\"\n  },\n  \"devDependencies\": {\n    \"@types/node\": \"^20.12.12\",\n    \"@types/react\": \"^18.3.3\",\n    \"@types/react-dom\": \"^18.3.0\",\n    \"autoprefixer\": \"^10.4.19\",\n    \"postcss\": \"^8.4.38\",\n    \"tailwindcss\": \"^3.4.3\",\n    \"typescript\": \"^5.4.5\",\n    \"eslint\": \"^8.57.0\",\n    \"eslint-config-next\": \"^14.2.3\",\n    \"jest\": \"^29.7.0\",\n    \"ts-jest\": \"^29.1.4\"\n  }\n}\n",
  "next.config.js": "/** @type {import('next').NextConfig} */\nconst nextConfig = {\n  reactStrictMode: true,\n};\n\nmodule.exports = nextConfig;\n",
  "tailwind.config.js": "/** @type {import('tailwindcss').Config} */\nmodule.exports = {\n  content: [\n    \"./src/app/**/*.{js,ts,jsx,tsx,mdx}\",\n    \"./src/components/**/*.{js,ts,jsx,tsx,mdx}\",\n  ],\n  theme: {\n    extend: {},\n  },\n  plugins: [],\n}\n",
  "postcss.config.js": "module.exports = {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n}\n",
  "tsconfig.json": "{\n  \"compilerOptions\": {\n    \"target\": \"es5\",\n    \"lib\": [\"dom\", \"dom.iterable\", \"esnext\"],\n    \"allowJs\": true,\n    \"skipLibCheck\": true,\n    \"strict\": true,\n    \"noEmit\": true,\n    \"esModuleInterop\": true,\n    \"module\": \"esnext\",\n    \"moduleResolution\": \"bundler\",\n    \"resolveJsonModule\": true,\n    \"isolatedModules\": true,\n    \"jsx\": \"preserve\",\n    \"incremental\": true,\n    \"plugins\": [\n      {\n        \"name\": \"next\"\n      }\n    ],\n    \"paths\": {\n      \"@/*\": [\"./src/*\"]\n    }\n  },\n  \"include\": [\"next-env.d.ts\", \"**/*.ts\", \"**/*.tsx\", \".next/types/**/*.ts\"],\n  \"exclude\": [\"node_modules\"]\n}\n",
  "jest.config.js": "module.exports = {\n  preset: 'ts-jest',\n  testEnvironment: 'node',\n  testMatch: ['**/tests/**/*.test.ts'],\n};\n",
  "src/app/globals.css": "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n:root {\n  color-scheme: dark;\n}\n\nbody {\n  margin: 0;\n  padding: 0;\n  background-color: #020617;\n  color: #f8fafc;\n}\n",
  "src/app/layout.tsx": "import React from 'react';\nimport './globals.css';\n\nexport const metadata = {\n  title: 'Antigravity Next.js Boilerplate',\n  description: 'Scaffolded Next.js workspace for AI software agents',\n};\n\nexport default function RootLayout({\n  children,\n}: {\n  children: React.ReactNode;\n}) {\n  return (\n    <html lang=\"en\">\n      <body>{children}</body>\n    </html>\n  );\n}\n",
  "src/app/page.tsx": "import React from 'react';\n\nexport default function Home() {\n  return (\n    <div className=\"min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans\">\n      <div className=\"max-w-4xl w-full text-center space-y-8\">\n        <header className=\"space-y-4\">\n          <div className=\"inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-semibold tracking-wide animate-pulse\">\n            \ud83d\ude80 Antigravity Workspace Active\n          </div>\n          <h1 className=\"text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent\">\n            Antigravity Next.js Boilerplate\n          </h1>\n          <p className=\"text-slate-400 text-lg max-w-2xl mx-auto\">\n            Your production-ready Next.js application, scaffolded and pre-configured for seamless development with AI coding agents.\n          </p>\n        </header>\n\n        <main className=\"grid grid-cols-1 md:grid-cols-3 gap-6 text-left\">\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\u26a1 App Router</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Scaffolded with React Server Components, layout sharing, and clean directory structure inside <code className=\"text-indigo-400\">src/app</code>.\n            </p>\n          </div>\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\ud83c\udfa8 Styling & UI</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Pre-integrated with Tailwind CSS, custom fonts, CSS variables, and modern dark-mode aesthetics ready for immediate extension.\n            </p>\n          </div>\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-pink-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\ud83d\udee1\ufe0f AI Agent Guard</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Wrapped inside Antigravity's cognitive alignment gates (automated pre-commit validators, secret scanning, and memory sync).\n            </p>\n          </div>\n        </main>\n\n        <footer className=\"text-slate-500 text-sm border-t border-slate-900 pt-8 mt-12 flex justify-between items-center\">\n          <div> Muhammad Rafael Ghifari &copy; 2026</div>\n          <div className=\"flex gap-4\">\n            <a href=\"https://github.com/rafaelghif/antigravity-agents\" target=\"_blank\" rel=\"noopener noreferrer\" className=\"hover:text-indigo-400 transition-colors\">GitHub Repository</a>\n            <a href=\"/api/health\" className=\"hover:text-indigo-400 transition-colors\">API Health Check</a>\n          </div>\n        </footer>\n      </div>\n    </div>\n  );\n}\n",
  "src/app/api/health/route.ts": "import { NextResponse } from 'next/server';\n\nexport async function GET() {\n  return NextResponse.json({\n    status: 'HEALTHY',\n    timestamp: new Date().toISOString(),\n    system: 'Antigravity Workspace Core',\n  });\n}\n",
  "tests/health.test.ts": "describe('Next.js Boilerplate Test Suite', () => {\n  it('should pass initial unit test check', () => {\n    expect(true).toBe(true);\n  });\n});\n"
}
GOGIN_TEMPLATES = {
  "go.mod": "module project\n\ngo 1.20\n\nrequire (\n\tgithub.com/gin-gonic/gin v1.9.1\n)\n",
  "src/cmd/server/main.go": "package main\n\nimport (\n\t\"fmt\"\n\t\"log\"\n\t\"net/http\"\n\t\"project/src/internal/config\"\n\t\"project/src/internal/controller\"\n\n\t\"github.com/gin-gonic/gin\"\n)\n\nfunc main() {\n\tcfg := config.LoadConfig()\n\n\tif cfg.Env == \"production\" {\n\t\tgin.SetMode(gin.ReleaseMode)\n\t}\n\n\tr := gin.Default()\n\tr.Use(gin.Recovery())\n\n\thealthCtrl := controller.NewHealthController()\n\n\tapi := r.Group(\"/api\")\n\t{\n\t\tapi.GET(\"/health\", healthCtrl.Check)\n\t}\n\n\tr.GET(\"/\", func(c *gin.Context) {\n\t\tc.JSON(http.StatusOK, gin.H{\n\t\t\t\"message\": \"Welcome to Antigravity Go Gin Boilerplate!\",\n\t\t\t\"status\":  \"Active\",\n\t\t})\n\t})\n\n\taddr := fmt.Sprintf(\":%s\", cfg.Port)\n\tlog.Printf(\"Server starting on port %s...\", cfg.Port)\n\tif err := r.Run(addr); err != nil {\n\t\tlog.Fatalf(\"Failed to run server: %v\", err)\n\t}\n}\n",
  "src/internal/config/config.go": "package config\n\nimport \"os\"\n\ntype Config struct {\n\tPort string\n\tEnv  string\n}\n\nfunc LoadConfig() *Config {\n\tport := os.Getenv(\"PORT\")\n\tif port == \"\" {\n\t\tport = \"8080\"\n\t}\n\tenv := os.Getenv(\"ENV\")\n\tif env == \"\" {\n\t\tenv = \"development\"\n\t}\n\treturn &Config{\n\t\tPort: port,\n\t\tEnv:  env,\n\t}\n}\n",
  "src/internal/controller/health_controller.go": "package controller\n\nimport (\n\t\"net/http\"\n\t\"time\"\n\n\t\"github.com/gin-gonic/gin\"\n)\n\ntype HealthController struct{}\n\nfunc NewHealthController() *HealthController {\n\treturn &HealthController{}\n}\n\nfunc (h *HealthController) Check(c *gin.Context) {\n\tc.JSON(http.StatusOK, gin.H{\n\t\t\"status\":    \"HEALTHY\",\n\t\t\"timestamp\": time.Now().Format(time.RFC3339),\n\t\t\"system\":    \"Antigravity Go Gin Core\",\n\t})\n}\n",
  "tests/health_test.go": "package tests\n\nimport (\n\t\"net/http\"\n\t\"net/http/httptest\"\n\t\"project/src/internal/controller\"\n\t\"testing\"\n\n\t\"github.com/gin-gonic/gin\"\n)\n\nfunc TestHealthCheck(t *testing.T) {\n\tgin.SetMode(gin.TestMode)\n\tr := gin.Default()\n\thealthCtrl := controller.NewHealthController()\n\tr.GET(\"/api/health\", healthCtrl.Check)\n\n\tw := httptest.NewRecorder()\n\treq, _ := http.NewRequest(\"GET\", \"/api/health\", nil)\n\tr.ServeHTTP(w, req)\n\n\tif w.Code != http.StatusOK {\n\t\tt.Errorf(\"Expected status code 200, got %d\", w.Code)\n\t}\n}\n",
  "Makefile": ".PHONY: run test build clean\n\nrun:\n\tgo run src/cmd/server/main.go\n\ntest:\n\tgo test -v ./tests/...\n\nbuild:\n\tgo build -o bin/server src/cmd/server/main.go\n\nclean:\n\trm -rf bin/\n"
}
FASTAPI_TEMPLATES = {
  "requirements.txt": "fastapi>=0.110.0\nuvicorn[standard]>=0.28.0\npydantic>=2.6.4\npytest>=8.1.1\nhttpx>=0.27.0\n",
  "pyproject.toml": "[tool.pytest.ini_options]\npythonpath = [\".\"]\ntestpaths = [\"tests\"]\n",
  "src/app/main.py": "import uvicorn\nfrom fastapi import FastAPI\nfrom src.app.core.config import settings\nfrom src.app.api.endpoints import health\n\napp = FastAPI(\n    title=\"Antigravity FastAPI Boilerplate\",\n    description=\"Production-ready FastAPI setup for AI software agents\",\n    version=\"1.0.0\",\n)\n\napp.include_router(health.router, prefix=\"/api\")\n\n@app.get(\"/\")\ndef read_root():\n    return {\n        \"message\": \"Welcome to Antigravity FastAPI Boilerplate!\",\n        \"status\": \"Active\",\n    }\n\nif __name__ == \"__main__\":\n    uvicorn.run(\"src.app.main:app\", host=\"0.0.0.0\", port=settings.PORT, reload=True)\n",
  "src/app/core/config.py": "import os\n\nclass Settings:\n    PORT: int = int(os.getenv(\"PORT\", 8000))\n    ENV: str = os.getenv(\"ENV\", \"development\")\n\nsettings = Settings()\n",
  "src/app/api/endpoints/health.py": "from datetime import datetime\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n\n@router.get(\"/health\", tags=[\"system\"])\ndef check_health():\n    return {\n        \"status\": \"HEALTHY\",\n        \"timestamp\": datetime.utcnow().isoformat(),\n        \"system\": \"Antigravity FastAPI Core\",\n    }\n",
  "tests/test_health.py": "from fastapi.testclient import TestClient\nfrom src.app.main import app\n\nclient = TestClient(app)\n\ndef test_health_check():\n    response = client.get(\"/api/health\")\n    assert response.status_code == 200\n    data = response.json()\n    assert data[\"status\"] == \"HEALTHY\"\n    assert \"timestamp\" in data\n    assert data[\"system\"] == \"Antigravity FastAPI Core\"\n"
}
MONOREPO_TEMPLATES = {
  "pnpm-workspace.yaml": "packages:\n  - 'apps/*'\n  - 'packages/*'\n",
  "turbo.json": "{\n  \"$schema\": \"https://turbo.build/schema.json\",\n  \"tasks\": {\n    \"build\": {\n      \"dependsOn\": [\"^build\"],\n      \"outputs\": [\".next/**\", \"dist/**\", \"bin/**\"]\n    },\n    \"lint\": {},\n    \"test\": {},\n    \"dev\": {\n      \"cache\": false,\n      \"persistent\": true\n    }\n  }\n}\n",
  "package.json": "{\n  \"name\": \"monorepo-root\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"build\": \"turbo run build\",\n    \"dev\": \"turbo run dev\",\n    \"lint\": \"turbo run lint\",\n    \"test\": \"turbo run test\"\n  },\n  \"devDependencies\": {\n    \"turbo\": \"^2.0.0\"\n  }\n}\n",
  "apps/web/package.json": "{\n  \"name\": \"web\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"dev\": \"next dev\",\n    \"build\": \"next build\",\n    \"start\": \"next start\",\n    \"lint\": \"next lint\",\n    \"test\": \"jest\"\n  },\n  \"dependencies\": {\n    \"next\": \"^14.2.3\",\n    \"react\": \"^18.3.1\",\n    \"react-dom\": \"^18.3.1\",\n    \"@monorepo/shared\": \"workspace:*\"\n  },\n  \"devDependencies\": {\n    \"@types/node\": \"^20.12.12\",\n    \"@types/react\": \"^18.3.3\",\n    \"@types/react-dom\": \"^18.3.0\",\n    \"autoprefixer\": \"^10.4.19\",\n    \"postcss\": \"^8.4.38\",\n    \"tailwindcss\": \"^3.4.3\",\n    \"typescript\": \"^5.4.5\",\n    \"eslint\": \"^8.57.0\",\n    \"eslint-config-next\": \"^14.2.3\",\n    \"jest\": \"^29.7.0\",\n    \"ts-jest\": \"^29.1.4\"\n  }\n}\n",
  "apps/web/next.config.js": "/** @type {import('next').NextConfig} */\nconst nextConfig = {\n  reactStrictMode: true,\n};\nmodule.exports = nextConfig;\n",
  "apps/web/tailwind.config.js": "/** @type {import('tailwindcss').Config} */\nmodule.exports = {\n  content: [\n    \"./src/app/**/*.{js,ts,jsx,tsx,mdx}\",\n    \"./src/components/**/*.{js,ts,jsx,tsx,mdx}\",\n  ],\n  theme: {\n    extend: {},\n  },\n  plugins: [],\n}\n",
  "apps/web/postcss.config.js": "module.exports = {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n}\n",
  "apps/web/tsconfig.json": "{\n  \"compilerOptions\": {\n    \"target\": \"es5\",\n    \"lib\": [\"dom\", \"dom.iterable\", \"esnext\"],\n    \"allowJs\": true,\n    \"skipLibCheck\": true,\n    \"strict\": true,\n    \"noEmit\": true,\n    \"esModuleInterop\": true,\n    \"module\": \"esnext\",\n    \"moduleResolution\": \"bundler\",\n    \"resolveJsonModule\": true,\n    \"isolatedModules\": true,\n    \"jsx\": \"preserve\",\n    \"incremental\": true,\n    \"plugins\": [\n      {\n        \"name\": \"next\"\n      }\n    ],\n    \"paths\": {\n      \"@/*\": [\"./src/*\"]\n    }\n  },\n  \"include\": [\"next-env.d.ts\", \"**/*.ts\", \"**/*.tsx\", \".next/types/**/*.ts\"],\n  \"exclude\": [\"node_modules\"]\n}\n",
  "apps/web/jest.config.js": "module.exports = {\n  preset: 'ts-jest',\n  testEnvironment: 'node',\n  testMatch: ['**/tests/**/*.test.ts'],\n};\n",
  "apps/web/src/app/globals.css": "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n:root {\n  color-scheme: dark;\n}\nbody {\n  margin: 0;\n  padding: 0;\n  background-color: #020617;\n  color: #f8fafc;\n}\n",
  "apps/web/src/app/layout.tsx": "import React from 'react';\nimport './globals.css';\nexport const metadata = {\n  title: 'Antigravity Monorepo Frontend',\n  description: 'Scaffolded Turborepo Frontend Web Application',\n};\nexport default function RootLayout({\n  children,\n}: {\n  children: React.ReactNode;\n}) {\n  return (\n    <html lang=\"en\">\n      <body>{children}</body>\n    </html>\n  );\n}\n",
  "apps/web/src/app/page.tsx": "import React from 'react';\nimport { appName, version } from '@monorepo/shared';\n\nexport default function Home() {\n  return (\n    <div className=\"min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 font-sans\">\n      <div className=\"max-w-4xl w-full text-center space-y-8\">\n        <header className=\"space-y-4\">\n          <div className=\"inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-sm font-semibold tracking-wide animate-pulse\">\n            \ud83d\ude80 Antigravity Monorepo Active\n          </div>\n          <h1 className=\"text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent\">\n            {appName}\n          </h1>\n          <p className=\"text-slate-400 text-lg max-w-2xl mx-auto\">\n            Monorepo Web Client (v{version}) running alongside an isolated Go Gin backend service.\n          </p>\n        </header>\n        <main className=\"grid grid-cols-1 md:grid-cols-3 gap-6 text-left\">\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-indigo-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\u26a1 Next.js</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Frontend web client running Next.js App Router inside <code className=\"text-indigo-400\">apps/web</code>.\n            </p>\n          </div>\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-purple-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\ud83d\udc39 Go Gin API</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Isolated REST API backend service with Go Gin inside <code className=\"text-purple-400\">apps/api</code>.\n            </p>\n          </div>\n          <div className=\"bg-slate-900/50 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm hover:border-pink-500/30 transition-all duration-300\">\n            <h2 className=\"text-xl font-bold text-slate-100 mb-2\">\ud83d\udce6 Shared Workspace</h2>\n            <p className=\"text-slate-400 text-sm\">\n              Shared package containing index exports, interfaces, and types inside <code className=\"text-pink-400\">packages/shared</code>.\n            </p>\n          </div>\n        </main>\n      </div>\n    </div>\n  );\n}\n",
  "apps/web/src/app/api/health/route.ts": "import { NextResponse } from 'next/server';\nexport async function GET() {\n  return NextResponse.json({\n    status: 'HEALTHY',\n    timestamp: new Date().toISOString(),\n    system: 'Antigravity Monorepo Frontend',\n  });\n}\n",
  "apps/web/tests/health.test.ts": "describe('Monorepo Web Client Test Suite', () => {\n  it('should pass initial tests', () => {\n    expect(true).toBe(true);\n  });\n});\n",
  "apps/api/go.mod": "module api\n\ngo 1.20\n\nrequire (\n\tgithub.com/gin-gonic/gin v1.9.1\n)\n",
  "apps/api/src/cmd/server/main.go": "package main\nimport (\n\t\"fmt\"\n\t\"log\"\n\t\"net/http\"\n\t\"api/src/internal/config\"\n\t\"api/src/internal/controller\"\n\t\"github.com/gin-gonic/gin\"\n)\nfunc main() {\n\tcfg := config.LoadConfig()\n\tif cfg.Env == \"production\" {\n\t\tgin.SetMode(gin.ReleaseMode)\n\t}\n\tr := gin.Default()\n\tr.Use(gin.Recovery())\n\thealthCtrl := controller.NewHealthController()\n\tapi := r.Group(\"/api\")\n\t{\n\t\tapi.GET(\"/health\", healthCtrl.Check)\n\t}\n\tr.GET(\"/\", func(c *gin.Context) {\n\t\tc.JSON(http.StatusOK, gin.H{\n\t\t\t\"message\": \"Welcome to Antigravity Go Gin Backend in Monorepo!\",\n\t\t\t\"status\":  \"Active\",\n\t\t})\n\t})\n\taddr := fmt.Sprintf(\":%s\", cfg.Port)\n\tlog.Printf(\"Backend starting on port %s...\", cfg.Port)\n\tif err := r.Run(addr); err != nil {\n\t\tlog.Fatalf(\"Failed to run server: %v\", err)\n\t}\n}\n",
  "apps/api/src/internal/config/config.go": "package config\nimport \"os\"\ntype Config struct {\n\tPort string\n\tEnv  string\n}\nfunc LoadConfig() *Config {\n\tport := os.Getenv(\"PORT\")\n\tif port == \"\" {\n\t\tport = \"8080\"\n\t}\n\tenv := os.Getenv(\"ENV\")\n\tif env == \"\" {\n\t\tenv = \"development\"\n\t}\n\treturn &Config{\n\t\tPort: port,\n\t\tEnv:  env,\n\t}\n}\n",
  "apps/api/src/internal/controller/health_controller.go": "package controller\nimport (\n\t\"net/http\"\n\t\"time\"\n\t\"github.com/gin-gonic/gin\"\n)\ntype HealthController struct{}\nfunc NewHealthController() *HealthController {\n\treturn &HealthController{}\n}\nfunc (h *HealthController) Check(c *gin.Context) {\n\tc.JSON(http.StatusOK, gin.H{\n\t\t\"status\":    \"HEALTHY\",\n\t\t\"timestamp\": time.Now().Format(time.RFC3339),\n\t\t\"system\":    \"Antigravity Monorepo Backend API\",\n\t})\n}\n",
  "apps/api/tests/health_test.go": "package tests\nimport (\n\t\"net/http\"\n\t\"net/http/httptest\"\n\t\"api/src/internal/controller\"\n\t\"testing\"\n\t\"github.com/gin-gonic/gin\"\n)\nfunc TestHealthCheck(t *testing.T) {\n\tgin.SetMode(gin.TestMode)\n\tr := gin.Default()\n\thealthCtrl := controller.NewHealthController()\n\tr.GET(\"/api/health\", healthCtrl.Check)\n\tw := httptest.NewRecorder()\n\treq, _ := http.NewRequest(\"GET\", \"/api/health\", nil)\n\tr.ServeHTTP(w, req)\n\tif w.Code != http.StatusOK {\n\t\tt.Errorf(\"Expected status code 200, got %d\", w.Code)\n\t}\n}\n",
  "apps/api/Makefile": ".PHONY: run test build clean\nrun:\n\tgo run src/cmd/server/main.go\ntest:\n\tgo test -v ./tests/...\nbuild:\n\tgo build -o bin/server src/cmd/server/main.go\nclean:\n\trm -rf bin/\n",
  "packages/shared/package.json": "{\n  \"name\": \"@monorepo/shared\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"main\": \"index.js\",\n  \"types\": \"index.d.ts\"\n}\n",
  "packages/shared/index.js": "module.exports = {\n  appName: \"Antigravity Monorepo\",\n  version: \"1.0.0\"\n};\n",
  "packages/shared/index.d.ts": "export const appName: string;\nexport const version: string;\n"
}
LARAVEL_TEMPLATES = {
  "app/Http/Controllers/Controller.php": "<?php\n\nnamespace App\\Http\\Controllers;\n\nuse Illuminate\\Foundation\\Auth\\Access\\AuthorizesRequests;\nuse Illuminate\\Foundation\\Validation\\ValidatesRequests;\nuse Illuminate\\Routing\\Controller as BaseController;\n\nclass Controller extends BaseController\n{\n    use AuthorizesRequests, ValidatesRequests;\n}\n",
  "app/Models/User.php": "<?php\n\nnamespace App\\Models;\n\nuse Illuminate\\Database\\Eloquent\\Factories\\HasFactory;\nuse Illuminate\\Foundation\\Auth\\User as Authenticatable;\nuse Illuminate\\Notifications\\Notifiable;\nuse Laravel\\Sanctum\\HasApiTokens;\n\nclass User extends Authenticatable\n{\n    use HasApiTokens, HasFactory, Notifiable;\n\n    protected $fillable = [\n        'name',\n        'email',\n        'password',\n    ];\n\n    protected $hidden = [\n        'password',\n        'remember_token',\n    ];\n\n    protected $casts = [\n        'email_verified_at' => 'datetime',\n        'password' => 'hashed',\n    ];\n}\n",
  "composer.json": "{\n    \"name\": \"laravel/laravel\",\n    \"type\": \"project\",\n    \"description\": \"The Laravel Framework.\",\n    \"keywords\": [\"framework\", \"laravel\"],\n    \"license\": \"MIT\",\n    \"require\": {\n        \"php\": \"^8.1\",\n        \"guzzlehttp/guzzle\": \"^7.2\",\n        \"laravel/framework\": \"^10.0\",\n        \"laravel/sanctum\": \"^3.2\",\n        \"laravel/tinker\": \"^2.8\"\n    },\n    \"require-dev\": {\n        \"fakerphp/faker\": \"^1.9.1\",\n        \"laravel/pint\": \"^1.0\",\n        \"laravel/sail\": \"^1.18\",\n        \"mockery/mockery\": \"^1.4.4\",\n        \"nunomaduro/collision\": \"^7.0\",\n        \"phpunit/phpunit\": \"^10.0\",\n        \"spatie/laravel-ignition\": \"^2.0\"\n    },\n    \"autoload\": {\n        \"psr-4\": {\n            \"App\\\\\": \"app/\",\n            \"Database\\\\Factories\\\\\": \"database/factories/\",\n            \"Database\\\\Seeders\\\\\": \"database/seeders/\"\n        }\n    },\n    \"autoload-dev\": {\n        \"psr-4\": {\n            \"Tests\\\\\": \"tests/\"\n        }\n    },\n    \"scripts\": {\n        \"post-autoload-dump\": [\n            \"Illuminate\\\\Foundation\\\\ComposerScripts::postAutoloadDump\",\n            \"@php artisan package:discover --ansi\"\n        ],\n        \"post-update-cmd\": [\n            \"@php artisan vendor:publish --tag=laravel-assets --ansi --force\"\n        ],\n        \"post-root-package-install\": [\n            \"@php -r \\\"file_exists('.env') || copy('.env.example', '.env');\\\"\"\n        ],\n        \"post-create-project-cmd\": [\n            \"@php artisan key:generate --ansi\"\n        ]\n    },\n    \"extra\": {\n        \"laravel\": {\n            \"dont-discover\": []\n        }\n    },\n    \"config\": {\n        \"optimize-autoloader\": true,\n        \"preferred-install\": \"dist\",\n        \"sort-packages\": true,\n        \"allow-plugins\": {\n            \"pestphp/pest-plugin\": true,\n            \"php-http/discovery\": true\n        }\n    },\n    \"minimum-stability\": \"stable\",\n    \"prefer-stable\": true\n}\n",
  "package.json": "{\n    \"private\": true,\n    \"type\": \"module\",\n    \"scripts\": {\n        \"dev\": \"vite\",\n        \"build\": \"vite build\"\n    },\n    \"devDependencies\": {\n        \"axios\": \"^1.1.2\",\n        \"laravel-vite-plugin\": \"^0.7.5\",\n        \"vite\": \"^4.0.0\"\n    }\n}\n",
  ".env.example": "APP_NAME=Laravel\nAPP_ENV=local\nAPP_KEY=\nAPP_DEBUG=true\nAPP_URL=http://localhost\n\nLOG_CHANNEL=stack\nLOG_DEPRECATIONS_CHANNEL=null\nLOG_LEVEL=debug\n\nDB_CONNECTION=mysql\nDB_HOST=127.0.0.1\nDB_PORT=3306\nDB_DATABASE=laravel\nDB_USERNAME=root\nDB_PASSWORD=\n\nBROADCAST_DRIVER=log\nCACHE_DRIVER=file\nFILESYSTEM_DISK=local\nQUEUE_CONNECTION=sync\nSESSION_DRIVER=file\nSESSION_LIFETIME=120\n",
  "artisan": "#!/usr/bin/env php\n<?php\n\ndefine('LARAVEL_START', microtime(true));\n\nif (file_exists($maintenance = __DIR__.'/storage/framework/maintenance.php')) {\n    require $maintenance;\n}\n\nrequire __DIR__.'/vendor/autoload.php';\n\n$app = require_once __DIR__.'/bootstrap/app.php';\n\n$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);\n\n$status = $kernel->handle(\n    $input = new Symfony\\Component\\Console\\Input\\ArgvInput,\n    new Symfony\\Component\\Console\\Output\\ConsoleOutput\n);\n\n$kernel->terminate($input, $status);\n\nexit($status);\n",
  "bootstrap/app.php": "<?php\n\n$app = new Illuminate\\Foundation\\Application(\n    $_ENV['APP_BASE_PATH'] ?? dirname(__DIR__)\n);\n\n$app->singleton(\n    Illuminate\\Contracts\\Http\\Kernel::class,\n    App\\Http\\Kernel::class\n);\n\n$app->singleton(\n    Illuminate\\Contracts\\Console\\Kernel::class,\n    App\\Http\\Console\\Kernel::class\n);\n\n$app->singleton(\n    Illuminate\\Contracts\\Debug\\ExceptionHandler::class,\n    App\\Exceptions\\Handler::class\n);\n\nreturn $app;\n",
  "app/Http/Kernel.php": "<?php\n\nnamespace App\\Http;\n\nuse Illuminate\\Foundation\\Http\\Kernel as HttpKernel;\n\nclass Kernel extends HttpKernel\n{\n    protected $middleware = [\n        \\Illuminate\\Http\\Middleware\\TrustProxies::class,\n        \\Illuminate\\Http\\Middleware\\HandleCors::class,\n        \\Illuminate\\Foundation\\Http\\Middleware\\PreventRequestsDuringMaintenance::class,\n        \\Illuminate\\Foundation\\Http\\Middleware\\ValidatePostSize::class,\n        \\App\\Http\\Middleware\\TrimStrings::class,\n        \\Illuminate\\Foundation\\Http\\Middleware\\ConvertEmptyStringsToNull::class,\n    ];\n\n    protected $middlewareGroups = [\n        'web' => [\n            \\App\\Http\\Middleware\\EncryptCookies::class,\n            \\Illuminate\\Cookie\\Middleware\\AddQueuedCookiesToResponse::class,\n            \\Illuminate\\Session\\Middleware\\StartSession::class,\n            \\Illuminate\\View\\Middleware\\ShareErrorsFromSession::class,\n            \\App\\Http\\Middleware\\VerifyCsrfToken::class,\n            \\Illuminate\\Routing\\Middleware\\SubstituteBindings::class,\n        ],\n        'api' => [\n            \\Laravel\\Sanctum\\Http\\Middleware\\EnsureFrontendRequestsAreStateful::class,\n            \\Illuminate\\Routing\\Middleware\\ThrottleRequests::class.':api',\n            \\Illuminate\\Routing\\Middleware\\SubstituteBindings::class,\n        ],\n    ];\n\n    protected $middlewareAliases = [\n        'auth' => \\App\\Http\\Middleware\\Authenticate::class,\n        'guest' => \\App\\Http\\Middleware\\RedirectIfAuthenticated::class,\n        'verified' => \\Illuminate\\Auth\\Middleware\\EnsureEmailIsVerified::class,\n    ];\n}\n",
  "app/Console/Kernel.php": "<?php\n\nnamespace App\\Console;\n\nuse Illuminate\\Foundation\\Console\\Kernel as ConsoleKernel;\n\nclass Kernel extends ConsoleKernel\n{\n    protected function commands(): void\n    {\n        $this->load(__DIR__.'/Commands');\n        require base_path('routes/console.php');\n    }\n}\n",
  "app/Exceptions/Handler.php": "<?php\n\nnamespace App\\Exceptions;\n\nuse Illuminate\\Foundation\\Exceptions\\Handler as ExceptionHandler;\nuse Throwable;\n\nclass Handler extends ExceptionHandler\n{\n    protected $dontFlash = [\n        'current_password',\n        'password',\n        'password_confirmation',\n    ];\n\n    public function register(): void\n    {\n        $this->reportable(function (Throwable $e) {\n            //\n        });\n    }\n}\n",
  "app/Http/Middleware/TrimStrings.php": "<?php\nnamespace App\\Http\\Middleware;\nuse Illuminate\\Foundation\\Http\\Middleware\\TrimStrings as Middleware;\nclass TrimStrings extends Middleware {}\n",
  "app/Http/Middleware/EncryptCookies.php": "<?php\nnamespace App\\Http\\Middleware;\nuse Illuminate\\Cookie\\Middleware\\EncryptCookies as Middleware;\nclass EncryptCookies extends Middleware {}\n",
  "app/Http/Middleware/VerifyCsrfToken.php": "<?php\nnamespace App\\Http\\Middleware;\nuse Illuminate\\Foundation\\Http\\Middleware\\VerifyCsrfToken as Middleware;\nclass VerifyCsrfToken extends Middleware {}\n",
  "app/Http/Middleware/Authenticate.php": "<?php\nnamespace App\\Http\\Middleware;\nuse Illuminate\\Auth\\Middleware\\Authenticate as Middleware;\nuse Illuminate\\Http\\Request;\nclass Authenticate extends Middleware {\n    protected function redirectTo(Request $request): ?string {\n        return $request->expectsJson() ? null : route('login');\n    }\n}\n",
  "app/Http/Middleware/RedirectIfAuthenticated.php": "<?php\nnamespace App\\Http\\Middleware;\nuse App\\Providers\\RouteServiceProvider;\nuse Closure;\nuse Illuminate\\Http\\Request;\nuse Illuminate\\Support\\Facades\\Auth;\nuse Symfony\\Component\\HttpFoundation\\Response;\nclass RedirectIfAuthenticated {\n    public function handle(Request $request, Closure $next, string ...$guards): Response {\n        $guards = empty($guards) ? [null] : $guards;\n        foreach ($guards as $guard) {\n            if (Auth::guard($guard)->check()) {\n                return redirect(RouteServiceProvider::HOME);\n            }\n        }\n        return $next($request);\n    }\n}\n",
  "app/Providers/RouteServiceProvider.php": "<?php\n\nnamespace App\\Providers;\n\nuse Illuminate\\Cache\\RateLimiting\\Limit;\nuse Illuminate\\Foundation\\Support\\Providers\\RouteServiceProvider as ServiceProvider;\nuse Illuminate\\Http\\Request;\nuse Illuminate\\Support\\Facades\\RateLimiter;\nuse Illuminate\\Support\\Facades\\Route;\n\nclass RouteServiceProvider extends ServiceProvider\n{\n    public const HOME = '/home';\n\n    public function boot(): void\n    {\n        RateLimiter::for('api', function (Request $request) {\n            return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());\n        });\n\n        $this->routes(function () {\n            Route::middleware('api')\n                ->prefix('api')\n                ->group(base_path('routes/api.php'));\n\n            Route::middleware('web')\n                ->group(base_path('routes/web.php'));\n        });\n    }\n}\n",
  "routes/web.php": "<?php\n\nuse Illuminate\\Support\\Facades\\Route;\n\nRoute::get('/', function () {\n    return view('welcome');\n});\n",
  "routes/api.php": "<?php\n\nuse Illuminate\\Support\\Facades\\Route;\nuse Illuminate\\Http\\Request;\n\nRoute::middleware('auth:sanctum')->get('/user', function (Request $request) {\n    return $request->user();\n});\n",
  "routes/console.php": "<?php\n\nuse Illuminate\\Support\\Facades\\Artisan;\n\nArtisan::command('inspire', function () {\n    $this->comment(Illuminate\\Foundation\\Inspiring::quote());\n})->purpose('Display an inspiring quote');\n",
  "resources/views/welcome.blade.php": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Antigravity Laravel Application</title>\n    <style>\n        body {\n            font-family: 'Outfit', 'Inter', sans-serif;\n            background: radial-gradient(circle at top right, #1e1b4b, #0f172a);\n            color: #f8fafc;\n            min-height: 100vh;\n            display: flex;\n            align-items: center;\n            justify-content: center;\n            margin: 0;\n        }\n        .container {\n            text-align: center;\n            padding: 3rem;\n            background: rgba(255, 255, 255, 0.03);\n            backdrop-filter: blur(16px);\n            border: 1px solid rgba(255, 255, 255, 0.08);\n            border-radius: 24px;\n            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);\n            max-width: 500px;\n        }\n        h1 {\n            font-size: 2.5rem;\n            margin-bottom: 1rem;\n            background: linear-gradient(to right, #f43f5e, #fb7185);\n            -webkit-background-clip: text;\n            -webkit-text-fill-color: transparent;\n        }\n        p {\n            color: #94a3b8;\n            line-height: 1.6;\n        }\n        .badge {\n            display: inline-block;\n            padding: 0.5rem 1rem;\n            background: rgba(244, 63, 94, 0.1);\n            color: #f43f5e;\n            border-radius: 9999px;\n            font-size: 0.875rem;\n            font-weight: 600;\n            margin-bottom: 1.5rem;\n        }\n    </style>\n</head>\n<body>\n    <div class=\"container\">\n        <div class=\"badge\">Laravel 10.x + PHP</div>\n        <h1>\ud83d\ude80 Welcome to Antigravity Laravel</h1>\n        <p>Your production-ready Laravel full-stack MVC application, scaffolded and pre-configured for seamless development with AI coding agents.</p>\n    </div>\n</body>\n</html>\n",
  "phpunit.xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<phpunit xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n         xsi:noNamespaceSchemaLocation=\"./vendor/phpunit/phpunit/phpunit.xsd\"\n         bootstrap=\"vendor/autoload.php\"\n         colors=\"true\">\n    <testsuites>\n        <testsuite name=\"Unit\">\n            <directory suffix=\"Test.php\">./tests/Unit</directory>\n        </testsuite>\n        <testsuite name=\"Feature\">\n            <directory suffix=\"Test.php\">./tests/Feature</directory>\n        </testsuite>\n    </testsuites>\n</phpunit>\n"
}
FALLBACK_TEMPLATES = {
  "package.json": "{\n  \"name\": \"project\",\n  \"version\": \"1.0.0\",\n  \"description\": \"\",\n  \"main\": \"src/index.js\",\n  \"scripts\": {\n    \"build\": \"tsc\",\n    \"start\": \"node dist/index.js\",\n    \"test\": \"jest\",\n    \"lint\": \"eslint 'src/**/*.ts'\"\n  },\n  \"dependencies\": {},\n  \"devDependencies\": {}\n}\n",
  "go.mod": "module project\n\ngo 1.20\n",
  "src/main.go": "package main\n\nimport \"fmt\"\n\nfunc main() {\n    fmt.Println(\"Hello, Antigravity!\")\n}\n",
  "src/main.py": "def main():\n    print(\"Hello, Antigravity!\")\n\nif __name__ == \"__main__\":\n    main()\n"
}
DOCKER_TEMPLATES = {
  "db_postgres": "  postgres:\n    image: postgres:15-alpine\n    container_name: postgres_db\n    environment:\n      POSTGRES_USER: postgres\n      POSTGRES_PASSWORD: postgres\n      POSTGRES_DB: postgres\n    ports:\n      - \"5432:5432\"\n    volumes:\n      - pgdata:/var/lib/postgresql/data\n    healthcheck:\n      test: [\"CMD-SHELL\", \"pg_isready -U postgres\"]\n      interval: 5s\n      timeout: 5s\n      retries: 5\n",
  "db_mysql": "  mysql:\n    image: mysql:8.0\n    container_name: mysql_db\n    environment:\n      MYSQL_ROOT_PASSWORD: root\n      MYSQL_DATABASE: db\n    ports:\n      - \"3306:3306\"\n    volumes:\n      - mysql_data:/var/lib/mysql\n    healthcheck:\n      test: [\"CMD-SHELL\", \"mysqladmin ping -h localhost\"]\n      interval: 5s\n      timeout: 5s\n      retries: 5\n",
  "db_mongodb": "  mongodb:\n    image: mongo:6.0\n    container_name: mongodb_db\n    ports:\n      - \"27017:27017\"\n    volumes:\n      - mongo_data:/data/db\n    healthcheck:\n      test: [\"CMD-SHELL\", \"echo 'db.runCommand(\\\"ping\\\")' | mongosh localhost:27017/test --quiet\"]\n      interval: 5s\n      timeout: 5s\n      retries: 5\n",
  "db_redis": "  redis:\n    image: redis:7-alpine\n    container_name: redis_cache\n    ports:\n      - \"6379:6379\"\n    volumes:\n      - redis_data:/data\n    healthcheck:\n      test: [\"CMD-SHELL\", \"redis-cli ping | grep PONG\"]\n      interval: 5s\n      timeout: 5s\n      retries: 5\n",
  "nextjs_dockerfile": "FROM golang:1.20-alpine AS builder\nWORKDIR /app\nCOPY go.mod go.sum* ./\nRUN go mod download\nCOPY . .\nRUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go\n\nFROM alpine:latest\nWORKDIR /root/\nCOPY --from=builder /app/main .\nEXPOSE 8080\nCMD [\"./main\"]\n",
  "gogin_dockerfile": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* ./\nRUN npm ci\nCOPY . .\nRUN npm run build\n\nFROM node:20-alpine AS runner\nWORKDIR /app\nENV NODE_ENV=production\nCOPY --from=builder /app/package.json ./\nCOPY --from=builder /app/dist ./dist\nCOPY --from=builder /app/node_modules ./node_modules\nEXPOSE 3000\nCMD [\"node\", \"dist/main\"]\n",
  "fastapi_dockerfile": "FROM golang:1.20-alpine AS builder\nWORKDIR /app\nCOPY go.mod go.sum* ./\nRUN go mod download\nCOPY . .\nRUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go\n\nFROM alpine:latest\nWORKDIR /root/\nCOPY --from=builder /app/main .\nEXPOSE 8080\nCMD [\"./main\"]\n",
  "laravel_dockerfile": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* ./\nRUN npm ci\nCOPY . .\nRUN npm run build\n\nFROM nginx:alpine\nCOPY --from=builder /app/dist /usr/share/nginx/html\nEXPOSE 80\nCMD [\"nginx\", \"-g\", \"daemon off;\"]\n",
  "nextjs_dockerignore": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./\nRUN \\\n  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \\\n  elif [ -f package-lock.json ]; then npm ci; \\\n  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \\\n  else npm install; \\\n  fi\nCOPY . .\nRUN \\\n  if [ -f pnpm-lock.yaml ]; then pnpm run build; \\\n  else npm run build; \\\n  fi\n\nFROM node:20-alpine AS runner\nWORKDIR /app\nENV NODE_ENV=production\nCOPY --from=builder /app/package.json ./\nCOPY --from=builder /app/.next ./.next\nCOPY --from=builder /app/public ./public\nCOPY --from=builder /app/node_modules ./node_modules\nEXPOSE 3000\nCMD [\"npm\", \"start\"]\n",
  "gogin_dockerignore": "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nEXPOSE 8000\nCMD [\"uvicorn\", \"src.app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n",
  "fastapi_dockerignore": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./\nRUN \\\n  if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile; \\\n  elif [ -f package-lock.json ]; then npm ci; \\\n  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \\\n  else npm install; \\\n  fi\nCOPY . .\nRUN \\\n  if [ -f pnpm-lock.yaml ]; then pnpm run build; \\\n  else npm run build; \\\n  fi\n\nFROM node:20-alpine AS runner\nWORKDIR /app\nENV NODE_ENV=production\nCOPY --from=builder /app/package.json ./\nCOPY --from=builder /app/.next ./.next\nCOPY --from=builder /app/public ./public\nCOPY --from=builder /app/node_modules ./node_modules\nEXPOSE 3000\nCMD [\"npm\", \"start\"]\n",
  "fallback_node_dockerfile": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* ./\nRUN npm ci\nCOPY . .\nRUN npm run build\n\nFROM node:20-alpine AS runner\nWORKDIR /app\nENV NODE_ENV=production\nCOPY --from=builder /app/package.json ./\nCOPY --from=builder /app/.next ./.next\nCOPY --from=builder /app/public ./public\nCOPY --from=builder /app/node_modules ./node_modules\nEXPOSE 3000\nCMD [\"npm\", \"start\"]\n",
  "fallback_go_dockerfile": "FROM golang:1.20-alpine AS builder\nWORKDIR /app\nCOPY go.mod go.sum* ./\nRUN go mod download\nCOPY . .\nRUN CGO_ENABLED=0 GOOS=linux go build -o main ./src/cmd/server/main.go\n\nFROM alpine:latest\nWORKDIR /root/\nCOPY --from=builder /app/main .\nEXPOSE 8080\nCMD [\"./main\"]\n",
  "fallback_py_dockerfile": "FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nEXPOSE 8000\nCMD [\"uvicorn\", \"src.app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n",
  "fallback_laravel_dockerfile": "FROM node:20-alpine AS builder\nWORKDIR /app\nCOPY package.json package-lock.json* ./\nRUN npm ci\nCOPY . .\nRUN npm run build\n\nFROM node:20-alpine AS runner\nWORKDIR /app\nENV NODE_ENV=production\nCOPY --from=builder /app/package.json ./\nCOPY --from=builder /app/dist ./dist\nCOPY --from=builder /app/node_modules ./node_modules\nEXPOSE 3000\nCMD [\"node\", \"dist/index.js\"]\n",
  "compose_multi": "version: '3.8'\n\nservices:\n",
  "compose_volume": "\nvolumes:\n  pgdata:\n  mysql_data:\n  mongo_data:\n  redis_data:\n",
  "compose_single": "version: '3.8'\n\nservices:\n"
}
MULTIPROJECT_FILES = {
  "apps/backend/package.json": "{\n  \"name\": \"backend\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"build\": \"nest build\",\n    \"start\": \"nest start\",\n    \"lint\": \"eslint 'src/**/*.ts'\",\n    \"test\": \"jest\"\n  },\n  \"dependencies\": {\n    \"@nestjs/common\": \"^10.0.0\",\n    \"@nestjs/core\": \"^10.0.0\",\n    \"reflect-metadata\": \"^0.1.13\",\n    \"rxjs\": \"^7.8.1\"\n  },\n  \"devDependencies\": {\n    \"@nestjs/cli\": \"^10.0.0\",\n    \"@nestjs/testing\": \"^10.0.0\",\n    \"@types/node\": \"^20.0.0\",\n    \"typescript\": \"^5.0.0\",\n    \"eslint\": \"^8.0.0\",\n    \"jest\": \"^29.0.0\"\n  }\n}\n",
  "apps/backend/src/main.ts": "import { NestFactory } from '@nestjs/core';\nimport { AppModule } from './app.module';\n\nasync function bootstrap() {\n  const app = await NestFactory.create(AppModule);\n  await app.listen(process.env.PORT || 3000);\n}\nbootstrap();\n",
  "apps/backend/src/app.module.ts": "import { Module } from '@nestjs/common';\n\n@Module({\n  imports: [],\n  controllers: [],\n  providers: [],\n})\nexport class AppModule {}\n",
  "apps/backend/requirements.txt": "fastapi>=0.110.0\nuvicorn[standard]>=0.28.0\npydantic>=2.6.4\npytest>=8.1.1\nhttpx>=0.27.0\n",
  "apps/backend/src/app/main.py": "from fastapi import FastAPI\n\napp = FastAPI(title=\"Antigravity Custom Backend\")\n\n@app.get(\"/\")\ndef read_root():\n    return {\"message\": \"Hello from Custom FastAPI Backend!\"}\n",
  "apps/backend/go.mod": "module backend\n\ngo 1.20\n\nrequire (\n\tgithub.com/gin-gonic/gin v1.9.1\n)\n",
  "apps/backend/src/cmd/server/main.go": "package main\n\nimport (\n\t\"github.com/gin-gonic/gin\"\n)\n\nfunc main() {\n\tr := gin.Default()\n\tr.GET(\"/\", func(c *gin.Context) {\n\t\tc.JSON(200, gin.H{\n\t\t\t\"message\": \"Hello from Custom Go Gin Backend!\",\n\t\t})\n\t})\n\tr.Run()\n}\n",
  "apps/frontend/package.json": "{\n  \"name\": \"frontend\",\n  \"version\": \"1.0.0\",\n  \"private\": true,\n  \"scripts\": {\n    \"dev\": \"vite\",\n    \"build\": \"tsc && vite build\",\n    \"lint\": \"eslint 'src/**/*.ts'\",\n    \"test\": \"jest\"\n  },\n  \"dependencies\": {\n    \"react\": \"^18.3.1\",\n    \"react-dom\": \"^18.3.1\"\n  },\n  \"devDependencies\": {\n    \"vite\": \"^5.0.0\",\n    \"@types/react\": \"^18.0.0\",\n    \"typescript\": \"^5.0.0\",\n    \"eslint\": \"^8.0.0\",\n    \"jest\": \"^29.0.0\"\n  }\n}\n",
  "apps/frontend/src/app/layout.tsx": "import type { Metadata } from 'next';\n\nexport const metadata: Metadata = {\n  title: 'Antigravity Custom Frontend',\n  description: 'Flexible separate frontend application',\n};\n\nexport default function RootLayout({\n  children,\n}: {\n  children: React.ReactNode;\n}) {\n  return (\n    <html lang=\"en\">\n      <body>{children}</body>\n    </html>\n  );\n}\n",
  "apps/frontend/src/app/page.tsx": "export default function Home() {\n  return (\n    <main style={{ padding: '2rem', fontFamily: 'sans-serif' }}>\n      <h1>\ud83d\ude80 Welcome to Antigravity Custom Frontend</h1>\n      <p>Running alongside a decoupled backend service in a clean modular layout.</p>\n    </main>\n  );\n}\n",
  "apps/frontend/index.html": "<!DOCTYPE html>\n<html lang=\"en\">\n  <head>\n    <meta charset=\"UTF-8\" />\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n    <title>Antigravity React SPA</title>\n  </head>\n  <body>\n    <div id=\"root\"></div>\n    <script type=\"module\" src=\"/src/main.tsx\"></script>\n  </body>\n</html>\n",
  "apps/frontend/src/main.tsx": "import React from 'react';\nimport ReactDOM from 'react-dom/client';\nimport App from './App';\n\nReactDOM.createRoot(document.getElementById('root')!).render(\n  <React.StrictMode>\n    <App />\n  </React.StrictMode>\n);\n",
  "apps/frontend/src/App.tsx": "import React from 'react';\n\nexport default function App() {\n  return (\n    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>\n      <h1>\ud83d\ude80 Welcome to Antigravity React SPA Frontend</h1>\n      <p>Decoupled single-page frontend application.</p>\n    </div>\n  );\n}\n",
  "apps/frontend/resources/views/welcome.blade.php": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Antigravity Blade Frontend</title>\n    <style>\n        body { font-family: sans-serif; padding: 2rem; background-color: #f8fafc; color: #1e293b; }\n    </style>\n</head>\n<body>\n    <h1>\ud83d\ude80 Welcome to Antigravity Blade/HTML Frontend</h1>\n    <p>Flexible separate frontend application template.</p>\n</body>\n</html>\n"
}

def get_input(prompt, default):
    try:
        val = input(f"{prompt} (default: {default}): ").strip()
        return val if val else default
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)

def select_choice(prompt, options, default_choice="1"):
    print(prompt)
    for opt in options:
        print(f"  {opt}")
    try:
        val = input(f"Select choice (default: {default_choice}): ").strip()
        return val if val else default_choice
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Created {path}")

def run(args):
    print("==========================================================")
    print("  Antigravity Agent Core - Workspace Initialization")
    print("==========================================================")
    
    project_name = args[1] if len(args) > 1 else None
    tech_stack = args[2] if len(args) > 2 else None
    arch_pattern = args[3] if len(args) > 3 else None
    db_orm = args[4] if len(args) > 4 else None
    env_vars = args[5] if len(args) > 5 else None
    scaffold = args[6] if len(args) > 6 else None
    gen_docker = args[7] if len(args) > 7 else None
    
    be_choice = "1"
    be_arch_choice = "2"
    fe_choice = "1"
    fe_arch_choice = "2"
    
    if not project_name:
        project_name = get_input("Enter Project Name", "My Project")
        
    if not tech_stack:
        stack_opts = [
            "[1] Next.js (TypeScript, Tailwind, App Router) [Recommended]",
            "[2] Go Gin (Clean Architecture REST API)",
            "[3] FastAPI (Python REST API with pytest)",
            "[4] Node/TypeScript (Generic Node App)",
            "[5] Go (Generic Main App)",
            "[6] Python (Generic Script)",
            "[7] Monorepo (Turborepo: Next.js Frontend + Go Gin Backend)",
            "[8] Custom Multi-Project / Separate Apps (e.g. apps/backend + apps/frontend)",
            "[9] Laravel (PHP MVC Framework)"
        ]
        choice = select_choice("Select Technology Stack:", stack_opts, "1")
        mapping = {
            "1": "Next.js", "2": "Go Gin", "3": "FastAPI", "4": "Node/TypeScript",
            "5": "Go", "6": "Python", "7": "Monorepo", "8": "Multi-Project", "9": "Laravel"
        }
        tech_stack = mapping.get(choice, choice)
        
    if tech_stack == "Multi-Project":
        be_opts = ["[1] NestJS (TypeScript)", "[2] FastAPI (Python)", "[3] Go Gin", "[4] None"]
        be_choice = select_choice("--- Configure Backend Application ---", be_opts, "1")
        
        if be_choice != "4":
            arch_opts = ["[1] Hexagonal Architecture (Ports & Adapters)", "[2] Clean Architecture", "[3] Standard MVC / Modular"]
            be_arch_choice = select_choice("Configure Backend Architecture:", arch_opts, "2")
            
        fe_opts = ["[1] Next.js (TypeScript)", "[2] React SPA (Vite)", "[3] Laravel Blade / PHP HTML", "[4] None"]
        fe_choice = select_choice("--- Configure Frontend Application ---", fe_opts, "1")
        
        if fe_choice != "4":
            arch_opts = ["[1] Atomic Design", "[2] Standard Components / App Router Layout"]
            fe_arch_choice = select_choice("Configure Frontend Architecture:", arch_opts, "2")
            
        arch_pattern = "Decoupled / Distributed Architecture"
        db_orm = "None"
        env_vars = "PORT"
        
    default_arch = "MVC"
    if tech_stack == "Next.js":
        default_arch = "App Router"
    elif tech_stack == "Go Gin":
        default_arch = "Clean Architecture"
    elif tech_stack == "FastAPI":
        default_arch = "Modular REST"
    elif tech_stack == "Monorepo":
        default_arch = "Decoupled / Distributed"
    elif tech_stack == "Laravel":
        default_arch = "MVC"
        
    if not arch_pattern:
        arch_pattern = get_input("Enter Architectural Pattern", default_arch)
        
    default_env = "PORT"
    if tech_stack in ("Go Gin", "FastAPI"):
        default_env = "PORT,ENV"
    elif tech_stack == "Next.js":
        default_env = "PORT"
    elif tech_stack == "Laravel":
        default_env = "APP_KEY,DB_CONNECTION,DB_DATABASE"
        
    if not db_orm:
        db_orm = get_input("Enter Database/ORM (e.g. Prisma, PostgreSQL, None)", "None")
        
    if not env_vars:
        env_vars = get_input("Enter config variables (comma-separated)", default_env)
        
    if not scaffold:
        scaffold = get_input("Scaffold initial project folders? (y/n)", "y").lower()
        
    if not gen_docker:
        gen_docker = get_input("Generate Dockerfiles and docker-compose.yml? (y/n)", "y").lower()

    # 1. Initialize Git if not present
    if not os.path.exists(".git"):
        print("Initializing Git repository...")
        subprocess.run(["git", "init"])
        subprocess.run(["git", "branch", "-m", "main"])
        
    # 2. Install Git hooks
    agents_dir = utils.get_agents_dir()
    os.makedirs(".git/hooks", exist_ok=True)
    for h in ('pre-commit', 'post-commit', 'commit-msg'):
        src = os.path.join(agents_dir, 'hooks', h)
        dest = os.path.join('.git', 'hooks', h)
        if os.path.exists(src):
            shutil.copy(src, dest)
            os.chmod(dest, 0o755)
            print(f"Git {h} hook installed.")

    # 3. Scaffold folders if requested
    if scaffold in ("y", "yes"):
        print("Scaffolding directory structure...")
        
        if tech_stack == "Next.js":
            if "Atomic" in arch_pattern or "atomic" in arch_pattern:
                dirs = ['src/app', 'src/components/atoms', 'src/components/molecules', 'src/components/organisms', 'src/components/templates', 'src/lib', 'tests']
            elif "Clean" in arch_pattern or "clean" in arch_pattern:
                dirs = ['src/app', 'src/core/entities', 'src/core/usecases', 'src/infrastructure/db', 'src/infrastructure/api', 'src/lib', 'tests']
            else:
                dirs = ['src/app', 'src/components', 'src/lib', 'tests']
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                
            for path, content in NEXT_TEMPLATES.items():
                write_file(path, content)
                
        elif tech_stack == "Go Gin":
            if any(x in arch_pattern for x in ("Hexagonal", "Ports", "Adapters")):
                dirs = ['src/cmd/server', 'src/internal/core/domain', 'src/internal/core/ports', 'src/internal/adapters/in/web', 'src/internal/adapters/out/db', 'src/internal/config', 'tests']
            elif "Clean" in arch_pattern:
                dirs = ['src/cmd/server', 'src/internal/domain/entity', 'src/internal/domain/usecase', 'src/internal/adapter/controller', 'src/internal/adapter/repository', 'src/internal/infrastructure/db', 'src/internal/config', 'tests']
            else:
                dirs = ['src/cmd/server', 'src/internal/model', 'src/internal/controller', 'src/internal/view', 'src/internal/config', 'tests']
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                
            for path, content in GOGIN_TEMPLATES.items():
                write_file(path, content)
                
        elif tech_stack == "FastAPI":
            if any(x in arch_pattern for x in ("Hexagonal", "Ports", "Adapters")):
                dirs = ['src/app/domain', 'src/app/ports', 'src/app/adapters/in/api', 'src/app/adapters/out/db', 'src/app/core', 'tests']
            elif "Clean" in arch_pattern:
                dirs = ['src/app/entities', 'src/app/usecases', 'src/app/controllers', 'src/app/infrastructure/db', 'src/app/core', 'tests']
            else:
                dirs = ['src/app/core', 'src/app/api/endpoints', 'tests']
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                
            for path, content in FASTAPI_TEMPLATES.items():
                write_file(path, content)
                
        elif tech_stack == "Monorepo":
            dirs = ['apps/web/src/app/api/health', 'apps/web/src/components', 'apps/web/src/lib', 'apps/web/tests',
                    'apps/api/src/cmd/server', 'apps/api/src/internal/controller', 'apps/api/src/internal/config', 'apps/api/tests',
                    'packages/shared']
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                
            for path, content in MONOREPO_TEMPLATES.items():
                write_file(path, content)
                
        elif tech_stack == "Laravel":
            dirs = ['app/Http/Controllers', 'app/Models', 'app/Providers', 'bootstrap', 'config', 'database/migrations',
                    'database/seeders', 'database/factories', 'public', 'resources/views', 'resources/css', 'resources/js',
                    'routes', 'tests/Feature', 'tests/Unit', 'app/Http/Middleware', 'app/Exceptions', 'app/Console']
            for d in dirs:
                os.makedirs(d, exist_ok=True)
                
            for path, content in LARAVEL_TEMPLATES.items():
                write_file(path, content)
                
        elif tech_stack == "Multi-Project":
            os.makedirs("apps/backend", exist_ok=True)
            os.makedirs("apps/frontend", exist_ok=True)
            
            # 1. Backend
            if be_choice == "1":
                # NestJS
                if be_arch_choice == "1":
                    dirs = ['apps/backend/src/core/domain', 'apps/backend/src/core/ports', 'apps/backend/src/adapters/in/web', 'apps/backend/src/adapters/out/persistence']
                elif be_arch_choice == "2":
                    dirs = ['apps/backend/src/entities', 'apps/backend/src/usecases', 'apps/backend/src/controllers', 'apps/backend/src/infrastructure/db']
                else:
                    dirs = ['apps/backend/src/modules', 'apps/backend/src/common']
                for d in dirs: os.makedirs(d, exist_ok=True)
                write_file("apps/backend/package.json", MULTIPROJECT_FILES["apps/backend/package.json"])
                write_file("apps/backend/src/main.ts", MULTIPROJECT_FILES["apps/backend/src/main.ts"])
                write_file("apps/backend/src/app.module.ts", MULTIPROJECT_FILES["apps/backend/src/app.module.ts"])
            elif be_choice == "2":
                # FastAPI
                if be_arch_choice == "1":
                    dirs = ['apps/backend/src/domain', 'apps/backend/src/ports', 'apps/backend/src/adapters/in/api', 'apps/backend/src/adapters/out/db', 'apps/backend/src/core']
                elif be_arch_choice == "2":
                    dirs = ['apps/backend/src/entities', 'apps/backend/src/usecases', 'apps/backend/src/controllers', 'apps/backend/src/infrastructure/db', 'apps/backend/src/core']
                else:
                    dirs = ['apps/backend/src/core', 'apps/backend/src/api/endpoints']
                for d in dirs: os.makedirs(d, exist_ok=True)
                write_file("apps/backend/requirements.txt", MULTIPROJECT_FILES["apps/backend/requirements.txt"])
                write_file("apps/backend/src/app/main.py", MULTIPROJECT_FILES["apps/backend/src/app/main.py"])
            elif be_choice == "3":
                # Go Gin
                if be_arch_choice == "1":
                    dirs = ['apps/backend/src/cmd/server', 'apps/backend/src/internal/core/domain', 'apps/backend/src/internal/core/ports', 'apps/backend/src/internal/adapters/in/web', 'apps/backend/src/internal/adapters/out/db', 'apps/backend/src/internal/config']
                elif be_arch_choice == "2":
                    dirs = ['apps/backend/src/cmd/server', 'apps/backend/src/internal/domain/entity', 'apps/backend/src/internal/domain/usecase', 'apps/backend/src/internal/adapter/controller', 'apps/backend/src/internal/adapter/repository', 'apps/backend/src/internal/infrastructure/db', 'apps/backend/src/internal/config']
                else:
                    dirs = ['apps/backend/src/cmd/server', 'apps/backend/src/internal/model', 'apps/backend/src/internal/controller', 'apps/backend/src/internal/view', 'apps/backend/src/internal/config']
                for d in dirs: os.makedirs(d, exist_ok=True)
                write_file("apps/backend/go.mod", MULTIPROJECT_FILES["apps/backend/go.mod"])
                write_file("apps/backend/src/cmd/server/main.go", MULTIPROJECT_FILES["apps/backend/src/cmd/server/main.go"])
                
            # 2. Frontend
            if fe_choice == "1":
                # Next.js
                if fe_arch_choice == "1":
                    dirs = ['apps/frontend/src/app', 'apps/frontend/src/lib', 'apps/frontend/src/components/atoms', 'apps/frontend/src/components/molecules', 'apps/frontend/src/components/organisms', 'apps/frontend/src/components/templates']
                else:
                    dirs = ['apps/frontend/src/app', 'apps/frontend/src/lib', 'apps/frontend/src/components']
                for d in dirs: os.makedirs(d, exist_ok=True)
                write_file("apps/frontend/package.json", MULTIPROJECT_FILES["apps/frontend/package.json"])
                write_file("apps/frontend/src/app/layout.tsx", MULTIPROJECT_FILES["apps/frontend/src/app/layout.tsx"])
                write_file("apps/frontend/src/app/page.tsx", MULTIPROJECT_FILES["apps/frontend/src/app/page.tsx"])
            elif fe_choice == "2":
                # React SPA
                if fe_arch_choice == "1":
                    dirs = ['apps/frontend/src', 'apps/frontend/public', 'apps/frontend/src/components/atoms', 'apps/frontend/src/components/molecules', 'apps/frontend/src/components/organisms', 'apps/frontend/src/components/templates']
                else:
                    dirs = ['apps/frontend/src', 'apps/frontend/public', 'apps/frontend/src/components']
                for d in dirs: os.makedirs(d, exist_ok=True)
                write_file("apps/frontend/package.json", MULTIPROJECT_FILES["apps/frontend/package.json"])
                write_file("apps/frontend/index.html", MULTIPROJECT_FILES["apps/frontend/index.html"])
                write_file("apps/frontend/src/main.tsx", MULTIPROJECT_FILES["apps/frontend/src/main.tsx"])
                write_file("apps/frontend/src/App.tsx", MULTIPROJECT_FILES["apps/frontend/src/App.tsx"])
            elif fe_choice == "3":
                # Laravel Blade
                os.makedirs("apps/frontend/resources/views", exist_ok=True)
                write_file("apps/frontend/resources/views/welcome.blade.php", MULTIPROJECT_FILES["apps/frontend/resources/views/welcome.blade.php"])
                
        else:
            # Fallback (Generic/Basic)
            dirs = ['src', 'tests', 'config']
            for d in dirs: os.makedirs(d, exist_ok=True)
            
            stack_lower = tech_stack.lower()
            if any(x in stack_lower for x in ("node", "typescript", "ts")):
                write_file("package.json", FALLBACK_TEMPLATES["package.json"])
            if any(x in stack_lower for x in ("go", "golang")):
                write_file("go.mod", FALLBACK_TEMPLATES["go.mod"])
                write_file("src/main.go", FALLBACK_TEMPLATES["src/main.go"])
            if any(x in stack_lower for x in ("python", "py")):
                write_file("src/main.py", FALLBACK_TEMPLATES["src/main.py"])

    # 4. Generate Dockerfiles
    if gen_docker in ("y", "yes"):
        print("Generating Dockerfiles and docker-compose.yml...")
        
        db_service = ""
        db_envs = ""
        db_depends = ""
        db_lower = db_orm.lower()
        
        if "postgres" in db_lower:
            db_service = DOCKER_TEMPLATES["db_postgres"]
            db_envs = "      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres\n      - DB_HOST=postgres\n      - DB_PORT=5432"
            db_depends = "    depends_on:\n      postgres:\n        condition: service_healthy"
        elif "mysql" in db_lower or "mariadb" in db_lower:
            db_service = DOCKER_TEMPLATES["db_mysql"]
            db_envs = "      - DATABASE_URL=mysql://root:root@mysql:3306/db\n      - DB_HOST=mysql\n      - DB_PORT=3306"
            db_depends = "    depends_on:\n      mysql:\n        condition: service_healthy"
        elif "mongo" in db_lower:
            db_service = DOCKER_TEMPLATES["db_mongodb"]
            db_envs = "      - DATABASE_URL=mongodb://mongodb:27017/db\n      - DB_HOST=mongodb\n      - DB_PORT=27017"
            db_depends = "    depends_on:\n      mongodb:\n        condition: service_healthy"
        elif "redis" in db_lower:
            db_service = DOCKER_TEMPLATES["db_redis"]
            db_envs = "      - REDIS_URL=redis://redis:6379/0\n      - REDIS_HOST=redis\n      - REDIS_PORT=6379"
            db_depends = "    depends_on:\n      redis:\n        condition: service_healthy"

        # Multi/Monorepos
        if tech_stack in ("Monorepo", "Multi-Project"):
            be_dir = "apps/api" if tech_stack == "Monorepo" else "apps/backend"
            fe_dir = "apps/web" if tech_stack == "Monorepo" else "apps/frontend"
            
            # Backend Dockerfile selection
            be_docker = ""
            if tech_stack == "Monorepo" or be_choice == "3":
                be_docker = DOCKER_TEMPLATES["gogin_dockerfile"]
            elif be_choice == "2":
                be_docker = DOCKER_TEMPLATES["fastapi_dockerfile"]
            elif be_choice == "1":
                # NestJS
                be_docker = "FROM node:18-alpine\nWORKDIR /app\nCOPY package*.json ./\nRUN npm install\nCOPY . .\nRUN npm run build\nCMD [\"npm\", \"run\", \"start:prod\"]"
                
            # Frontend Dockerfile selection
            fe_docker = ""
            if tech_stack == "Monorepo" or fe_choice == "1":
                fe_docker = DOCKER_TEMPLATES["nextjs_dockerfile"]
            elif fe_choice == "2":
                fe_docker = "FROM node:18-alpine\nWORKDIR /app\nCOPY package*.json ./\nRUN npm install\nCOPY . .\nRUN npm run build\nRUN npm install -g serve\nCMD [\"serve\", \"-s\", \"dist\"]"
            elif fe_choice == "3":
                fe_docker = DOCKER_TEMPLATES["laravel_dockerfile"]
                
            # Write Dockerfiles
            if be_choice != "4":
                write_file(f"{be_dir}/Dockerfile", be_docker.replace('\\n', '\n').replace('\"', '"'))
            if fe_choice != "4":
                write_file(f"{fe_dir}/Dockerfile", fe_docker.replace('\\n', '\n').replace('\"', '"'))
                
            # Compose
            services = ""
            if fe_choice != "4":
                services += f"  frontend:\n    build:\n      context: ./{fe_dir}\n      dockerfile: Dockerfile\n    ports:\n      - \"3000:3000\"\n"
            if be_choice != "4":
                services += f"  backend:\n    build:\n      context: ./{be_dir}\n      dockerfile: Dockerfile\n    ports:\n      - \"8080:8080\"\n"
                if db_depends:
                    services += f"{db_depends}\n"
                if db_envs:
                    services += f"    environment:\n{db_envs}\n"
                    
            if db_service:
                services += f"\n{db_service}\n"
                
            compose_content = f"version: '3.8'\n\nservices:\n{services}"
            if "postgres" in db_lower or "mysql" in db_lower or "mariadb" in db_lower or "mongo" in db_lower:
                vol_name = "pgdata" if "postgres" in db_lower else ("mysql_data" if "mysql" in db_lower or "mariadb" in db_lower else "mongo_data")
                compose_content += f"\nvolumes:\n  {vol_name}:\n"
                
            write_file("docker-compose.yml", compose_content.replace('\\n', '\n').replace('\"', '"'))
            
        else:
            # Single Project dockerfiles
            dockerfile_content = ""
            dockerignore_content = ""
            
            if tech_stack == "Next.js":
                dockerfile_content = DOCKER_TEMPLATES.get("nextjs_dockerfile", "")
                dockerignore_content = DOCKER_TEMPLATES.get("nextjs_dockerignore", "")
            elif tech_stack in ("Go Gin", "Go"):
                dockerfile_content = DOCKER_TEMPLATES.get("gogin_dockerfile", "")
                dockerignore_content = DOCKER_TEMPLATES.get("gogin_dockerignore", "")
            elif tech_stack in ("FastAPI", "Python"):
                dockerfile_content = DOCKER_TEMPLATES.get("fastapi_dockerfile", "")
                dockerignore_content = DOCKER_TEMPLATES.get("fastapi_dockerignore", "")
            elif tech_stack == "Laravel":
                dockerfile_content = DOCKER_TEMPLATES.get("laravel_dockerfile", "")
            elif any(x in tech_stack.lower() for x in ("node", "typescript", "ts")):
                dockerfile_content = DOCKER_TEMPLATES.get("fallback_node_dockerfile", "")
                
            if dockerfile_content:
                write_file("Dockerfile", dockerfile_content.replace('\\n', '\n').replace('\"', '"'))
            if dockerignore_content:
                write_file(".dockerignore", dockerignore_content.replace('\\n', '\n').replace('\"', '"'))
                
            # Compose
            port = "3000" if tech_stack == "Next.js" else ("8080" if tech_stack in ("Go Gin", "Go") else "8000")
            services = f"  app:\n    build:\n      context: .\n      dockerfile: Dockerfile\n    ports:\n      - \"{port}:{port}\"\n"
            if db_depends:
                services += f"{db_depends}\n"
            if db_envs:
                services += f"    environment:\n{db_envs}\n"
                
            if db_service:
                services += f"\n{db_service}\n"
                
            compose_content = f"version: '3.8'\n\nservices:\n{services}"
            if "postgres" in db_lower or "mysql" in db_lower or "mariadb" in db_lower or "mongo" in db_lower:
                vol_name = "pgdata" if "postgres" in db_lower else ("mysql_data" if "mysql" in db_lower or "mariadb" in db_lower else "mongo_data")
                compose_content += f"\nvolumes:\n  {vol_name}:\n"
                
            write_file("docker-compose.yml", compose_content.replace('\\n', '\n').replace('\"', '"'))

    # 5. Create .env and .env.example
    if env_vars:
        print("Writing configuration environment variables...")
        vars_list = [v.strip() for v in env_vars.split(',') if v.strip()]
        env_content = "\n".join([f"{v}=" for v in vars_list]) + "\n"
        with open(".env.example", 'w') as f:
            f.write(env_content)
        with open(".env", 'w') as f:
            f.write(env_content)
        print("Created .env and .env.example templates")

    # 6. Run auto-recon to generate the blueprints
    print("Running autonomous reconnaissance to populate blueprint files...")
    recon_sh = os.path.join(agents_dir, 'scripts', 'recon.sh')
    if os.path.exists(recon_sh):
        utils.run_shell_script(recon_sh, ["-f"])
        
    print("==========================================================")
    print(f"Workspace initialized successfully for '{project_name}'!")
    print("==========================================================")
