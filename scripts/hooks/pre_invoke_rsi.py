import sys, json
from pathlib import Path

def main():
    try:
        raw_input = sys.stdin.buffer.read().decode('utf-8', errors='replace').strip()
        payload = json.loads(raw_input) if raw_input else {}
    except Exception as e:
        sys.stderr.write(f"[hook] Error parsing stdin: {e}\n")
        print(json.dumps({}))
        return
        
    transcript_path = payload.get("transcriptPath", "")
    if transcript_path and Path(transcript_path).is_file():
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if lines:
                last_step = lines[-1]
                if "TOOL_RESPONSE" in last_step and ("failed with exit code" in last_step.lower() or "error:" in last_step.lower() or "exception:" in last_step.lower() or "exit status" in last_step.lower()):
                    print(json.dumps({
                        "injectSteps": [
                            {
                                "ephemeralMessage": "🚨 RSI PROTOCOL TRIGGERED 🚨: The previous terminal command failed! DO NOT guess the solution. You MUST immediately call `invoke_subagent` to spawn a `reviewer` subagent. Give the reviewer the error logs and ask it to analyze the root cause and provide a patch."
                            }
                        ]
                    }))
                    return
        except Exception as e:
            sys.stderr.write(f"[hook] Guard execution failed safely: {e}\n")
            
    print(json.dumps({}))

if __name__ == "__main__":
    main()
