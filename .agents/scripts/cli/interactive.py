"""
Antigravity Agent Core (AAC) CLI Interactive UI Helpers.
Provides cross-platform arrow-key menus and interactive prompt inputs using Python's standard library.
"""
import sys
import os

def get_key_posix():
    """Reads a single keypress from standard input on POSIX systems."""
    import tty
    import termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == '\x1b':
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                if ch3 == 'A':
                    return 'up'
                elif ch3 == 'B':
                    return 'down'
                elif ch3 == 'C':
                    return 'right'
                elif ch3 == 'D':
                    return 'left'
            return 'esc'
        elif ch1 == '\r' or ch1 == '\n':
            return 'enter'
        elif ch1 == '\x03':  # Ctrl+C
            return 'ctrl+c'
        elif ch1 in ('\x7f', '\x08'):  # Backspace
            return 'backspace'
        return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def get_key_windows():
    """Reads a single keypress from standard input on Windows systems."""
    import msvcrt
    ch = msvcrt.getch()
    if ch in (b'\x00', b'\xe0'):
        ch2 = msvcrt.getch()
        if ch2 == b'H':
            return 'up'
        elif ch2 == b'P':
            return 'down'
        elif ch2 == b'K':
            return 'left'
        elif ch2 == b'M':
            return 'right'
    elif ch in (b'\r', b'\n'):
        return 'enter'
    elif ch == b'\x1b':
        return 'esc'
    elif ch == b'\x03':
        return 'ctrl+c'
    elif ch == b'\x08':
        return 'backspace'
    try:
        return ch.decode('utf-8', errors='ignore')
    except Exception:
        return ""

def interactive_select(options, title="Select an option:", default_idx=0):
    """
    Renders an interactive selection menu in the terminal.
    
    Args:
        options (list): A list of strings or list of dicts with {"name": ..., "desc": ...}.
        title (str): The menu header/title.
        default_idx (int): Initially highlighted index.
        
    Returns:
        The selected option from the input list, or None if cancelled.
    """
    if not options:
        return None

    is_testing = "unittest" in sys.modules or "pytest" in sys.modules or os.environ.get("AAC_TEST_MODE") == "1"
    if not sys.stdin.isatty() or is_testing:
        # Fallback to standard numbered input
        print(f"\n{title}")
        for idx, opt in enumerate(options):
            label = opt if isinstance(opt, str) else opt.get("name", "")
            desc = f" - {opt.get('desc')}" if isinstance(opt, dict) and opt.get("desc") else ""
            print(f"  {idx + 1}) {label}{desc}")
        try:
            choice = input(f"Select option (1-{len(options)}): ").strip()
            val = int(choice) - 1
            if 0 <= val < len(options):
                return options[val]
        except Exception:
            pass
        return None

    # TTY Arrow selection
    idx = default_idx
    n_options = len(options)
    
    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    
    try:
        while True:
            # Print title
            sys.stdout.write(f"\033[1;36m{title}\033[0m\n")
            for i, opt in enumerate(options):
                label = opt if isinstance(opt, str) else opt.get("name", "")
                desc = f" \033[90m({opt.get('desc')})\033[0m" if isinstance(opt, dict) and opt.get("desc") else ""
                if i == idx:
                    # Highlighted
                    sys.stdout.write(f"  \033[1;92m➔  {label}\033[0m{desc}\n")
                else:
                    sys.stdout.write(f"     {label}{desc}\n")
            sys.stdout.flush()
            
            # Wait for keypress
            try:
                if sys.platform == 'win32':
                    key = get_key_windows()
                else:
                    key = get_key_posix()
            except KeyboardInterrupt:
                key = 'ctrl+c'
            
            # Clear printed lines
            sys.stdout.write(f"\033[{n_options + 1}A\033[J")
            sys.stdout.flush()
            
            if key == 'up':
                idx = (idx - 1) % n_options
            elif key == 'down':
                idx = (idx + 1) % n_options
            elif key == 'enter':
                chosen = options[idx]
                label = chosen if isinstance(chosen, str) else chosen.get("name", "")
                sys.stdout.write(f"\033[1;36m{title}\033[0m \033[1;92m{label}\033[0m\n")
                sys.stdout.flush()
                return chosen
            elif key in ('esc', 'ctrl+c'):
                sys.stdout.write(f"\033[1;36m{title}\033[0m \033[1;91m(cancelled)\033[0m\n")
                sys.stdout.flush()
                return None
    finally:
        # Show cursor
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def prompt_input(prompt_text, default=""):
    """
    Prompts user for text input, supporting default values.
    
    Args:
        prompt_text (str): The prompt label.
        default (str): The default value returned if input is empty.
        
    Returns:
        str: The user input, or the default value.
    """
    default_suffix = f" [{default}]" if default else ""
    try:
        val = input(f"\033[1;33m{prompt_text}{default_suffix}:\033[0m ").strip()
        if not val:
            return default
        return val
    except (KeyboardInterrupt, EOFError):
        print()
        return default
