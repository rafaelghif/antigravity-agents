import os
import sys
import json
import time
import utils

def run(args):
    # args[0] is 'api-profile'
    target_profile = ""
    if len(args) > 1:
        target_profile = args[1]
        
    api_keys_file = ""
    agents_keys = os.path.join(utils.get_agents_dir(), 'api_keys')
    home_keys = os.path.expanduser('~/.antigravity_api_keys')
    if os.path.exists(agents_keys):
        api_keys_file = agents_keys
    elif os.path.exists(home_keys):
        api_keys_file = home_keys
        
    rate_limited = "--rate-limited" in args
    
    # Parse available profiles prefix (e.g. name.GEMINI_API_KEY=val)
    config = {}
    if os.path.exists(api_keys_file):
        with open(api_keys_file, 'r') as f:
            for line in f:
                if line.strip() and not line.strip().startswith('#') and '=' in line:
                    parts = line.strip().split('=', 1)
                    config[parts[0].strip()] = parts[1].strip()
                    
    profiles_list = sorted(list(set(k.split('.')[0] for k in config.keys() if '.' in k)))
    num_profiles = len(profiles_list)
    
    if target_profile in ("rotate", "--rotate"):
        if not api_keys_file or not os.path.exists(api_keys_file):
            print("Error: No API keys configuration found (.agents/api_keys or ~/.antigravity_api_keys) to rotate.", file=sys.stderr)
            sys.exit(1)
            
        if num_profiles == 0:
            print(f"Error: No API profiles found in {api_keys_file}.", file=sys.stderr)
            sys.exit(1)
            
        current_profile = "none"
        profile_name_file = os.path.join(utils.get_agents_dir(), 'active_api_profile_name')
        if os.path.exists(profile_name_file):
            with open(profile_name_file, 'r') as f:
                current_profile = f.read().strip()
                
        if rate_limited:
            current_time = int(time.time())
            cooldown_sec = int(os.environ.get("API_ROTATION_COOLDOWN_SEC", 60))
            expiry_time = current_time + cooldown_sec
            
            cooldowns_file = os.path.join(utils.get_agents_dir(), 'cooldowns.json')
            
            if current_profile != "none":
                print(f"Putting profile '{current_profile}' on cooldown for {cooldown_sec} seconds...")
                cooldowns = {}
                if os.path.exists(cooldowns_file):
                    try:
                        with open(cooldowns_file, 'r') as f:
                            cooldowns = json.load(f)
                    except: pass
                cooldowns[current_profile] = expiry_time
                with open(cooldowns_file, 'w') as f:
                    json.dump(cooldowns, f, indent=2)
                    
            # Choose next profile that is NOT on cooldown
            cooldowns = {}
            if os.path.exists(cooldowns_file):
                try:
                    with open(cooldowns_file, 'r') as f:
                        cooldowns = json.load(f)
                except: pass
            # Clean expired cooldowns
            cooldowns = {p: exp for p, exp in cooldowns.items() if exp > current_time}
            with open(cooldowns_file, 'w') as f:
                json.dump(cooldowns, f, indent=2)
                
            if current_profile in profiles_list:
                start_idx = profiles_list.index(current_profile)
                ordered_candidates = profiles_list[start_idx+1:] + profiles_list[:start_idx]
            else:
                ordered_candidates = profiles_list
                
            selected = None
            for p in ordered_candidates:
                if p not in cooldowns:
                    selected = p
                    break
                    
            if selected:
                target_profile = selected
                print(f"Rotating active API profile to: '{target_profile}'...")
            else:
                # All profiles in cooldown
                if cooldowns:
                    earliest_profile = min(cooldowns, key=cooldowns.get)
                    earliest_expiry = cooldowns[earliest_profile]
                    
                    now_time = int(time.time())
                    sleep_sec = earliest_expiry - now_time
                    if sleep_sec > 0:
                        print(f"All API profiles are in cooldown! Earliest available is '{earliest_profile}' in {sleep_sec}s.")
                        print(f"Waiting/sleeping for {sleep_sec} seconds before retrying...")
                        for i in range(sleep_sec, 0, -1):
                            sys.stdout.write(f"  Retrying in {i} seconds...\r")
                            sys.stdout.flush()
                            time.sleep(1)
                        print(f"\n  Cooldown finished. Selecting profile '{earliest_profile}'...")
                        
                    # Clear cooldown entry
                    if earliest_profile in cooldowns:
                        del cooldowns[earliest_profile]
                    with open(cooldowns_file, 'w') as f:
                        json.dump(cooldowns, f, indent=2)
                    target_profile = earliest_profile
                else:
                    target_profile = profiles_list[0]
                    print(f"Rotating active API profile to: '{target_profile}'...")
        else:
            # Standard round robin
            selected_idx = 0
            if current_profile in profiles_list:
                selected_idx = (profiles_list.index(current_profile) + 1) % num_profiles
            target_profile = profiles_list[selected_idx]
            print(f"Rotating active API profile to: '{target_profile}'...")
            
    if target_profile and target_profile != "--rate-limited":
        if os.path.exists(api_keys_file):
            # Check if profile exists
            profile_keys = [k for k in config.keys() if k.startswith(f"{target_profile}.")]
            if profile_keys:
                print(f"Setting active API profile to '{target_profile}'...")
                
                active_keys_sh = os.path.join(utils.get_agents_dir(), 'active_api_keys')
                active_keys_ps1 = os.path.join(utils.get_agents_dir(), 'active_api_keys.ps1')
                profile_name_file = os.path.join(utils.get_agents_dir(), 'active_api_profile_name')
                
                # Write bash file
                with open(active_keys_sh, 'w') as f_sh, open(active_keys_ps1, 'w') as f_ps:
                    f_sh.write(f"# Active API keys for profile: {target_profile}\n")
                    f_ps.write(f"# Active API keys for profile: {target_profile}\n")
                    
                    for k in profile_keys:
                        var_name = k.split('.', 1)[1]
                        var_val = config[k]
                        f_sh.write(f"export {var_name}=\"{var_val}\"\n")
                        f_ps.write(f"$env:{var_name} = \"{var_val}\"\n")
                        
                with open(profile_name_file, 'w') as f:
                    f.write(target_profile)
                    
                print("  [SUCCESS] Active API keys updated in .agents/active_api_keys and .agents/active_api_keys.ps1")
            else:
                print(f"Error: Profile '{target_profile}' not found in {api_keys_file}.", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: API keys file not found.", file=sys.stderr)
            sys.exit(1)
            
    # Display configuration
    utils.print_title("Current API Profile Configuration")
    
    current_profile = "none"
    profile_name_file = os.path.join(utils.get_agents_dir(), 'active_api_profile_name')
    if os.path.exists(profile_name_file):
        with open(profile_name_file, 'r') as f:
            current_profile = f.read().strip()
            
    print(f"Active Profile: {current_profile}")
    print("")
    
    # Mask key values for display
    print("Active Keys (masked for security):")
    for k, v in config.items():
        if k.startswith(f"{current_profile}."):
            var_name = k.split('.', 1)[1]
            masked = v
            if len(v) > 8:
                masked = v[:4] + "****" + v[-4:]
            print(f"  {var_name}: {masked}")
    print("")
    
    if os.path.exists(api_keys_file):
        print(f"Available API Profiles (from {api_keys_file}):")
        for p in profiles_list:
            keys = [k.split('.', 1)[1] for k in config.keys() if k.startswith(f"{p}.")]
            print(f"  - {p} ({' '.join(keys)} )")
