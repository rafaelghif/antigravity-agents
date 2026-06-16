#!/usr/bin/env python3
import argparse
import sys
import json
import logging
import os
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_active_api_keys():
    """
    Parses .agents/active_api_keys to load active API keys into the environment.
    """
    path = ".agents/active_api_keys"
    if os.path.exists(path):
        logging.info(f"Loading active API keys from {path}...")
        with open(path, "r") as f:
            for line in f:
                if line.startswith("export "):
                    # strip 'export ' and split on first '='
                    parts = line[7:].strip().split("=")
                    if len(parts) >= 2:
                        var_name = parts[0]
                        # join remaining parts in case value contains '='
                        var_val = "=".join(parts[1:]).strip('"\'')
                        os.environ[var_name] = var_val
                        logging.debug(f"Loaded env var: {var_name}")
    else:
        logging.warning("No active API keys file found at .agents/active_api_keys.")

def check_and_rotate_budget():
    """
    Proactively checks the current active profile's token budget.
    Rotates to the next profile if the limit is exceeded.
    """
    budget_file = ".agents/token_budget.json"
    profile_file = ".agents/active_api_profile_name"
    if not os.path.exists(budget_file) or not os.path.exists(profile_file):
        return
        
    with open(profile_file, "r") as f:
        profile = f.read().strip()
        
    with open(budget_file, "r") as f:
        try:
            budget = json.load(f)
        except Exception:
            return
        
    profiles = budget.get("profiles", {})
    if profile in profiles:
        prof_data = profiles[profile]
        usage = prof_data.get("current_token_usage", 0)
        limit = prof_data.get("max_token_budget", 500000)
        if usage >= limit:
            logging.info(f"Quota limit reached for profile '{profile}' ({usage}/{limit}). Proactively rotating...")
            # Rotate using helper.sh
            subprocess.run(["./.agents/scripts/helper.sh", "api-profile", "rotate"], check=True)
            load_active_api_keys()

def run_skill(args):
    """
    Main logic of the skill script.
    """
    # 1. Proactive Budget Check & Initial Key Load
    check_and_rotate_budget()
    load_active_api_keys()

    prompt = args.prompt
    provider = args.provider
    model = args.model
    simulate_limit = args.simulate_limit
    
    max_retries = 3
    # Try parsing number of API profiles configured to set max_retries dynamically
    api_keys_file = ".agents/api_keys"
    if os.path.exists(api_keys_file):
        try:
            with open(api_keys_file, "r") as f:
                prefixes = set()
                for line in f:
                    if line.strip() and not line.strip().startswith("#") and "=" in line:
                        prefix = line.split(".")[0].strip()
                        prefixes.add(prefix)
                if prefixes:
                    max_retries = len(prefixes)
        except Exception:
            pass

    for attempt in range(max_retries):
        # Read the current profile name for log visibility
        profile_file = ".agents/active_api_profile_name"
        profile_name = "default"
        if os.path.exists(profile_file):
            with open(profile_file, "r") as f:
                profile_name = f.read().strip()
                
        logging.info(f"Attempt {attempt + 1}/{max_retries} using profile: '{profile_name}'")
        
        # 2. Simulate or execute API request
        try:
            # Check if simulation is requested
            if simulate_limit is not None and attempt < simulate_limit:
                logging.warning(f"Simulating API rate-limit error (HTTP 429) for attempt {attempt + 1}...")
                # Raise custom exception that mimics a rate limit/quota limit
                raise Exception("API rate limit exceeded. Status code: 429")
                
            # Try real imports/execution if packages are available
            if provider == "gemini":
                api_key = os.environ.get("GEMINI_API_KEY")
                if not api_key or api_key.endswith("_key_here") or "personal_key" in api_key:
                    # Treat mock keys as simulated success
                    logging.info("GEMINI_API_KEY is a placeholder/simulation key. Simulating successful call...")
                    response_text = f"[Simulated Response for prompt: '{prompt}']"
                else:
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=api_key)
                        gemini_model = genai.GenerativeModel(model)
                        response = gemini_model.generate_content(prompt)
                        response_text = response.text
                    except ImportError:
                        logging.warning("google-generativeai library is not installed. Falling back to simulation.")
                        response_text = f"[Simulated Response for prompt: '{prompt}']"
            elif provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key or api_key.endswith("_key_here") or "personal_key" in api_key:
                    logging.info("OPENAI_API_KEY is a placeholder/simulation key. Simulating successful call...")
                    response_text = f"[Simulated Response for prompt: '{prompt}']"
                else:
                    try:
                        import openai
                        client = openai.OpenAI(api_key=api_key)
                        response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        response_text = response.choices[0].message.content
                    except ImportError:
                        logging.warning("openai library is not installed. Falling back to simulation.")
                        response_text = f"[Simulated Response for prompt: '{prompt}']"
            else:
                response_text = f"[Simulated Response for prompt: '{prompt}' on unsupported provider {provider}]"

            # 3. Successful execution: Log Token Usage
            tokens_used = args.tokens
            logging.info(f"API call successful! Logging {tokens_used} tokens for profile '{profile_name}'...")
            subprocess.run(["./.agents/scripts/helper.sh", "log-usage", str(tokens_used)], check=True)
            
            return {
                "status": "success",
                "profile": profile_name,
                "provider": provider,
                "model": model,
                "response": response_text,
                "tokens_logged": tokens_used
            }
            
        except Exception as e:
            # 4. Reactive Rotation: Check if it's a rate-limit / resource exhaustion error
            error_msg = str(e)
            is_rate_limit = False
            
            # Check for typical rate limit indicators in error message
            rate_limit_keywords = ["429", "rate limit", "resource_exhausted", "quota exceeded", "limit exceeded"]
            if any(kw in error_msg.lower() for kw in rate_limit_keywords):
                is_rate_limit = True
                
            if is_rate_limit and attempt < max_retries - 1:
                logging.warning(f"Rate limit hit: {error_msg}. Rotating API profile and retrying...")
                # Rotate profile
                subprocess.run(["./.agents/scripts/helper.sh", "api-profile", "rotate"], check=True)
                # Reload updated environment keys
                load_active_api_keys()
            else:
                # Re-raise the exception if not rate limited or if we ran out of profiles
                raise e

def main():
    parser = argparse.ArgumentParser(description="Python wrapper for api-rotator skill execution with hybrid rotation.")
    parser.add_argument('--prompt', '-p', type=str, default="Hello, World!", help="Prompt text to send to LLM")
    parser.add_argument('--provider', type=str, default="gemini", choices=["gemini", "openai"], help="LLM Provider")
    parser.add_argument('--model', type=str, default="gemini-1.5-flash", help="Model name")
    parser.add_argument('--tokens', type=int, default=150, help="Simulated token usage count")
    parser.add_argument('--simulate-limit', type=int, default=None, help="Number of attempts to simulate rate limits (e.g. 1)")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    try:
        output = run_skill(args)
        print(json.dumps(output, indent=2))
        sys.exit(0)
    except Exception as e:
        logging.error(f"Execution failed: {str(e)}")
        error_output = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main()
