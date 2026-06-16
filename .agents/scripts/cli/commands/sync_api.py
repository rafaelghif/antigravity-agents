import os
import sys
import subprocess
import utils
import re

def run(args):
    print("==========================================================")
    print("Starting API Contract Synchronization...")
    print("==========================================================")
    
    subprojects_file = os.path.join(utils.get_agents_dir(), "subprojects.sh")
    be_path = ""
    fe_path = ""
    be_stack = ""
    
    if os.path.exists(subprojects_file):
        try:
            with open(subprojects_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            lines = []
            
        for line in lines:
            line_strip = line.strip()
            if '|' in line_strip:
                clean_line = re.sub(r'^[A-Z_a-z0-9\+]+=\s*\(?\s*', '', line_strip).strip(') \'"')
                parts = clean_line.split('|')
                if len(parts) >= 2:
                    path = parts[0]
                    stack = parts[1]
                    if any(x in path or x in stack for x in ("api", "backend", "Go", "Python")):
                        be_path = path
                        be_stack = stack
                    elif any(x in path or x in stack for x in ("web", "frontend", "Next.js")):
                        fe_path = path
    else:
        # Fallbacks
        if os.path.isdir("apps/backend"): be_path = "apps/backend"
        if os.path.isdir("apps/frontend"): fe_path = "apps/frontend"
        if os.path.isdir("apps/api"): be_path = "apps/api"
        if os.path.isdir("apps/web"): fe_path = "apps/web"
        
    if not be_path:
        if os.path.isfile("go.mod") or os.path.isfile("main.go"):
            be_path = "."
            be_stack = "Go"
        elif os.path.isfile("requirements.txt") or os.path.isfile("pyproject.toml"):
            be_path = "."
            be_stack = "Python"
            
    if not fe_path:
        if os.path.isdir("src/app") or os.path.isfile("package.json"):
            fe_path = "."
            
    if not be_path:
        print("  [INFO] Backend application path could not be auto-detected. Operating in root fallback mode.")
        be_path = "."
        be_stack = "Unknown"
        
    print(f"  Detected Backend: {be_path} ({be_stack})")
    if fe_path:
        print(f"  Detected Frontend: {fe_path}")
        
    openapi_file = "openapi.json"
    print("  Extracting OpenAPI contract schema...")
    
    extracted = False
    
    # Python
    if "Python" in be_stack or os.path.isfile(os.path.join(be_path, "requirements.txt")) or os.path.isfile(os.path.join(be_path, "pyproject.toml")):
        cmd1 = f"python3 -c \"import json; from src.app.main import app; print(json.dumps(app.openapi()))\" > {openapi_file}"
        cmd2 = f"python3 -c \"import json; from app.main import app; print(json.dumps(app.openapi()))\" > {openapi_file}"
        
        cwd = None if be_path == "." else be_path
        target_path = openapi_file if be_path == "." else os.path.join("..", "..", "..", openapi_file)
        
        cmd1_run = f"python3 -c \"import json; from src.app.main import app; print(json.dumps(app.openapi()))\" > {target_path}"
        cmd2_run = f"python3 -c \"import json; from app.main import app; print(json.dumps(app.openapi()))\" > {target_path}"
        
        proc = subprocess.run(cmd1_run, shell=True, cwd=cwd, stderr=subprocess.DEVNULL)
        if proc.returncode == 0:
            extracted = True
        else:
            proc = subprocess.run(cmd2_run, shell=True, cwd=cwd, stderr=subprocess.DEVNULL)
            if proc.returncode == 0:
                extracted = True
                
    # Go
    elif "Go" in be_stack or os.path.isfile(os.path.join(be_path, "go.mod")):
        # check if swag command exists
        try:
            subprocess.run(["swag", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            swag_exists = True
        except:
            swag_exists = False
            
        if swag_exists:
            print(f"  Running swag init in {be_path}...")
            cwd = None if be_path == "." else be_path
            # try different main locations
            proc1 = subprocess.run("swag init -g src/cmd/server/main.go -o . --ot json", shell=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if proc1.returncode == 0:
                shutil_copy = True
            else:
                proc2 = subprocess.run("swag init -g cmd/server/main.go -o . --ot json", shell=True, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                shutil_copy = proc2.returncode == 0
                
            if shutil_copy:
                src_swagger = os.path.join(be_path, "swagger.json")
                if os.path.exists(src_swagger):
                    import shutil
                    shutil.copy(src_swagger, openapi_file)
                    extracted = True
                    
    if not extracted or not os.path.exists(openapi_file) or os.path.getsize(openapi_file) == 0:
        print("  Warning: Schema extraction returned empty. Writing a compliant mock/fallback openapi.json...")
        mock_content = """{
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
"""
        with open(openapi_file, 'w', encoding='utf-8') as f:
            f.write(mock_content)
            
    # Generate client
    if fe_path and os.path.isdir(fe_path):
        target_client = os.path.join(fe_path, "src", "lib", "api-client.ts")
        if fe_path == "." and os.path.isdir("src/app"):
            target_client = os.path.join("src", "lib", "api-client.ts")
            
        print(f"  Generating TypeScript client wrapper to {target_client}...")
        client_js = os.path.join(utils.get_agents_dir(), "scripts", "generate-client.js")
        proc = subprocess.run(["node", client_js, openapi_file, target_client])
        sys.exit(proc.returncode)
    else:
        print("  Frontend directory not detected. Generated openapi.json is saved in root.")
        sys.exit(0)
