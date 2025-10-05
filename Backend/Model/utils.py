import sys
import time
import threading
from typing import Callable

def spinner_with_timer(msg: str = "Processing...") -> Callable[[], None]:
    """Displays a spinner with a timer in the console."""
    done = False
    start_time = time.time()
    def spin():
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        i = 0
        while not done:
            elapsed = int(time.time() - start_time)
            # ANSI escape code for green color
            green_color = "\033[92m"
            # ANSI escape code to reset color
            reset_color = "\033[0m"
            spinner = spinner_chars[i % len(spinner_chars)]
            i += 1
            sys.stdout.write(f"\r{msg} {spinner} ({green_color}{elapsed}s{reset_color})")
            sys.stdout.flush()
            time.sleep(0.1)
    t = threading.Thread(target=spin)
    t.start()
    def stop():
        nonlocal done
        done = True
        t.join()
        # ANSI escape code for green color
        green_color = "\033[92m"
        # ANSI escape code to reset color
        reset_color = "\033[0m"
        elapsed_time = int(time.time() - start_time)
        sys.stdout.write(f"\r{msg} Done! ({green_color}{elapsed_time}s{reset_color})\n")
        sys.stdout.flush()
    return stop
