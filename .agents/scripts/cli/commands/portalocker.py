import os
import sys
import time

LOCK_EX = 1
LOCK_SH = 2
LOCK_NB = 4
LOCK_UN = 8

class LockException(Exception):
    pass

class AlreadyLocked(LockException):
    pass

if os.name == 'nt':
    import msvcrt
    def lock(file, flags):
        try:
            mode = msvcrt.LK_NBLCK if (flags & LOCK_NB) else msvcrt.LK_LOCK
            file.seek(0)
            msvcrt.locking(file.fileno(), mode, 1)
        except IOError as e:
            raise AlreadyLocked(str(e))

    def unlock(file):
        try:
            file.seek(0)
            msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
        except IOError as e:
            raise LockException(str(e))
else:
    import fcntl
    def lock(file, flags):
        # Translate portalocker constants to fcntl ones
        fn_flags = 0
        if flags & LOCK_EX:
            fn_flags |= fcntl.LOCK_EX
        elif flags & LOCK_SH:
            fn_flags |= fcntl.LOCK_SH
        if flags & LOCK_NB:
            fn_flags |= fcntl.LOCK_NB
            
        try:
            fcntl.flock(file.fileno(), fn_flags)
        except IOError as e:
            raise AlreadyLocked(str(e))

    def unlock(file):
        try:
            fcntl.flock(file.fileno(), fcntl.LOCK_UN)
        except IOError as e:
            raise LockException(str(e))

class Lock:
    def __init__(self, filename, mode='r', flags=LOCK_EX, timeout=None, check_interval=0.25, fail_when_locked=False, **kwargs):
        self.filename = filename
        self.mode = mode
        self.flags = flags
        self.timeout = timeout
        self.check_interval = check_interval
        self.fail_when_locked = fail_when_locked
        self.file = None

    def __enter__(self):
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.filename)), exist_ok=True)
        # Open file
        # If writing, we should check if file exists or create it, but avoid truncating on open before locking
        # Wait, if we use mode='w' on open, Python truncates the file immediately BEFORE we acquire the lock.
        # This is a classic race condition in file locking!
        # To avoid this, we should open with 'a+' or open and truncate after locking.
        # But for 'r', 'r+' it is fine.
        # If mode starts with 'w', we can open with 'a' or 'r+' (if exists) or create it first, then lock, then truncate.
        # Let's handle 'w' modes safely:
        open_mode = self.mode
        if 'w' in self.mode:
            # Open in append mode so we don't truncate before locking
            open_mode = self.mode.replace('w', 'a')
            
        self.file = open(self.filename, open_mode)
        
        start_time = time.time()
        while True:
            try:
                lock(self.file, self.flags)
                # If we successfully locked, and the original mode was 'w', we truncate it now!
                if 'w' in self.mode:
                    self.file.seek(0)
                    self.file.truncate()
                return self.file
            except AlreadyLocked:
                if self.fail_when_locked:
                    self.file.close()
                    raise
                if self.timeout is not None and (time.time() - start_time) > self.timeout:
                    self.file.close()
                    raise LockException("Lock acquisition timed out")
                time.sleep(self.check_interval)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            unlock(self.file)
        finally:
            self.file.close()
