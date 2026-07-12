import unittest
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cli/commands')))
import portalocker

class TestLockConcurrency(unittest.TestCase):
    
    def setUp(self):
        self.temp_file = tempfile.mktemp(suffix=".json")
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def tearDown(self):
        if os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except Exception:
                pass

    def test_portalocker_mutual_exclusion(self):
        # We will run multiple threads trying to write to the same file.
        # Each thread will read the current integer from the file, increment it, and write it back.
        # If there is no concurrency control, the final value will be less than the number of threads (race condition).
        # With portalocker, the final value must be exactly the number of threads.
        
        # Write initial value 0
        with open(self.temp_file, "w") as f:
            f.write("0")
            
        num_threads = 10
        
        def worker(thread_idx):
            # Attempt to acquire exclusive lock, read, increment, sleep, and write
            # We use timeout=10.0 to ensure threads wait for their turn
            with portalocker.Lock(self.temp_file, 'r+', flags=portalocker.LOCK_EX, timeout=10.0) as f:
                content = f.read().strip()
                val = int(content) if content else 0
                time.sleep(0.01) # Simulate some work under lock
                f.seek(0)
                f.write(str(val + 1))
                f.truncate()
                
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Launch all workers simultaneously
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            for fut in futures:
                fut.result() # Wait and raise exceptions if any
                
        # Read final value
        with open(self.temp_file, "r") as f:
            final_val = int(f.read().strip())
            
        self.assertEqual(final_val, num_threads)

if __name__ == '__main__':
    unittest.main()
