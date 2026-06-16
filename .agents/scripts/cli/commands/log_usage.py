import sys
import utils

def run(args):
    if len(args) < 2:
        print("Usage: helper.py log-usage <token_count>", file=sys.stderr)
        sys.exit(1)
        
    try:
        tokens = int(args[1])
    except ValueError:
        print("Error: Token count must be an integer.", file=sys.stderr)
        sys.exit(1)
        
    utils.log_token_usage(tokens)
