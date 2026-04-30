# signals_demo.py
"""Complete signals demo: parent controls child processes with signals"""

import multiprocessing
import signal
import time
import os
import sys


class WorkerProcess:
    """Worker that responds to signals from parent"""

    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.process = None
        self.running = False

    def _run(self):
        """Main worker loop"""
        pid = os.getpid()
        print(f"[Worker {self.worker_id}] Started with PID {pid}")

        # Setup signal handlers
        def handle_sigusr1(signum, frame):
            print(f"[Worker {self.worker_id}] Paused (SIGUSR1)")
            self.running = False

        def handle_sigusr2(signum, frame):
            print(f"[Worker {self.worker_id}] Resumed (SIGUSR2)")
            self.running = True

        def handle_sigterm(signum, frame):
            print(f"[Worker {self.worker_id}] Terminating (SIGTERM)")
            sys.exit(0)

        signal.signal(signal.SIGUSR1, handle_sigusr1)
        signal.signal(signal.SIGUSR2, handle_sigusr2)
        signal.signal(signal.SIGTERM, handle_sigterm)

        self.running = True
        counter = 0

        while True:
            if self.running:
                counter += 1
                print(f"[Worker {self.worker_id}] Working... count={counter}")
            else:
                print(f"[Worker {self.worker_id}] Paused, waiting...")

            time.sleep(1)

    def start(self):
        """Start the worker process"""
        self.process = multiprocessing.Process(target=self._run)
        self.process.start()
        return self.process.pid

    def pause(self):
        """Pause the worker (SIGUSR1)"""
        if self.process and self.process.is_alive():
            os.kill(self.process.pid, signal.SIGUSR1)
            print(f"[Controller] Paused worker {self.worker_id}")

    def resume(self):
        """Resume the worker (SIGUSR2)"""
        if self.process and self.process.is_alive():
            os.kill(self.process.pid, signal.SIGUSR2)
            print(f"[Controller] Resumed worker {self.worker_id}")

    def stop(self):
        """Stop the worker (SIGTERM)"""
        if self.process and self.process.is_alive():
            os.kill(self.process.pid, signal.SIGTERM)
            print(f"[Controller] Stopping worker {self.worker_id}")
            self.process.join(timeout=2)

            if self.process.is_alive():
                self.process.terminate()  # Force kill if needed
                self.process.join()

    def is_alive(self):
        return self.process and self.process.is_alive()


def main():
    """Main controller"""
    print("=" * 60)
    print("SIGNALS DEMO - Parent controlling child processes")
    print("=" * 60)
    print(f"Parent PID: {os.getpid()}")
    print()

    # Create two workers
    workers = [WorkerProcess(1), WorkerProcess(2)]

    # Start workers
    for w in workers:
        w.start()

    time.sleep(2)

    # Demo: pause worker 1
    print("\n--- Pausing worker 1 ---")
    workers[0].pause()
    time.sleep(3)

    # Demo: resume worker 1
    print("\n--- Resuming worker 1 ---")
    workers[0].resume()
    time.sleep(3)

    # Demo: pause worker 2
    print("\n--- Pausing worker 2 ---")
    workers[1].pause()
    time.sleep(3)

    # Demo: stop worker 1
    print("\n--- Stopping worker 1 ---")
    workers[0].stop()
    time.sleep(2)

    # Demo: resume worker 2
    print("\n--- Resuming worker 2 ---")
    workers[1].resume()
    time.sleep(3)

    # Cleanup: stop all remaining workers
    print("\n--- Cleaning up ---")
    for w in workers:
        if w.is_alive():
            w.stop()

    print("\n[Controller] All workers terminated")


if __name__ == "__main__":
    main()