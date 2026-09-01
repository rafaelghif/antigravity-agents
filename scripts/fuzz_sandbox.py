import argparse
import sys
import random
import string
import subprocess
import json

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))

def generate_random_int():
    return random.randint(-10000, 10000)

def generate_random_dict():
    return {
        generate_random_string(5): generate_random_string(10),
        generate_random_string(5): generate_random_int()
    }

def fuzz_loop(target_script, iterations=10):
    print(f"Starting fuzzing sandbox for {target_script} with {iterations} iterations...")
    
    success_count = 0
    failure_count = 0

    for i in range(iterations):
        # Generate some random inputs
        input_data = {
            "test_string": generate_random_string(20),
            "test_int": generate_random_int(),
            "test_dict": generate_random_dict()
        }
        input_json = json.dumps(input_data)
        
        print(f"Iteration {i+1}/{iterations}: Fuzzing with input {input_json[:50]}...")
        
        if target_script:
            try:
                process = subprocess.Popen(
                    ["python3", target_script],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(input=input_json, timeout=5)
                
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, target_script, output=stdout, stderr=stderr)
                    
                success_count += 1
            except subprocess.TimeoutExpired:
                print(f"Iteration {i+1} FAILED: Timeout")
                process.kill()
                failure_count += 1
            except subprocess.CalledProcessError as e:
                print(f"Iteration {i+1} FAILED: Process crashed with code {e.returncode}")
                if hasattr(e, 'stderr') and e.stderr:
                    print(f"STDERR: {e.stderr.strip()}")
                failure_count += 1
            except Exception as e:
                print(f"Iteration {i+1} FAILED: {str(e)}")
                failure_count += 1
        else:
            success_count += 1
            
    print(f"\nFuzzing Complete: {success_count} passed, {failure_count} failed.")
    if failure_count > 0:
        return 1
    return 0

def main():
    parser = argparse.ArgumentParser(description="Fuzzing Sandbox Wrapper")
    parser.add_argument("role", nargs="?", default="qa-engineer", help="Role (usually qa-engineer)")
    parser.add_argument("--target", type=str, default="", help="Target python script to fuzz")
    parser.add_argument("--iterations", type=int, default=5, help="Number of fuzzing iterations")
    args = parser.parse_args()

    sys.exit(fuzz_loop(args.target, args.iterations))

if __name__ == "__main__":
    main()
