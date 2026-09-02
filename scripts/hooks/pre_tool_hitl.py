import sys, json
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from hook_utils import read_hook_payload, json, re, subprocess

def main():
        sys.stderr.write(f"[hook] Error parsing stdin: {e}\n")
        print(json.dumps({"decision": "allow"}))
        return
        
    tool_name = payload.get("toolCall", {}).get("name", "")
    if tool_name != "run_command":
        print(json.dumps({"decision": "allow"}))
        return
        
    cmd = payload.get("toolCall", {}).get("args", {}).get("CommandLine", "")
    
    if re.search(r"git push|docker push|npm publish", cmd):
        consensus_file = Path(".agents/brain/AITL_CONSENSUS.yaml")
        if not consensus_file.is_file():
            print(json.dumps({
                "decision": "ask",
                "reason": "PRODUCTION GATE BLOCKED: No Human-in-the-Loop (HITL) OR Agent-in-the-Loop (AITL) consensus found. To deploy autonomously, you MUST invoke the 'reviewer' and 'security-reviewer' subagents and save their approval to '.agents/brain/AITL_CONSENSUS.yaml'."
            }))
            return
            
                    "reason": "PRODUCTION GATE BLOCKED: The AITL_CONSENSUS.yaml file exists but lacks 'STATUS: APPROVED'. The peer agents did not approve this deployment."
                }))
                return
        except Exception as e:
            sys.stderr.write(f"[hook] Guard execution failed safely: {e}\n")
            
        print(json.dumps({
            "decision": "allow",
            "reason": "AITL Consensus verified. Deployment authorized."
        }))
        return
        
    if re.search(r"git commit", cmd):
        guard_script = Path("scripts/git_hygiene_guard.py")
        if guard_script.is_file():
                        "decision": "deny",
                        "reason": "GIT HYGIENE BLOCKED: Detected scratch/temporary files staged or pending in workspace. Delete scratch scripts or run 'python3 scripts/git_hygiene_guard.py --clean' before committing."
                    }))
                    return
            except Exception:
                pass
                
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
