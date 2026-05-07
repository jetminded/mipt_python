# 20_shared_memory_basic_stdlib.py
"""Basic shared memory example with standard library only"""

import multiprocessing
from multiprocessing import shared_memory
import time


def worker(shm_name, worker_id):
    """Worker process reads and modifies shared memory"""
    # Attach to existing shared memory block
    existing_shm = shared_memory.SharedMemory(name=shm_name)

    for i in range(3):
        # Read first 8 bytes as integer
        current = int.from_bytes(existing_shm.buf[0:8], 'little')
        print(f"[Worker {worker_id}] Read: {current}")

        # Modify value
        new_value = current + 1
        existing_shm.buf[0:8] = new_value.to_bytes(8, 'little')
        print(f"[Worker {worker_id}] Wrote: {new_value}")

        time.sleep(0.5)

    existing_shm.close()


if __name__ == "__main__":
    shm = shared_memory.SharedMemory(create=True, size=8)

    shm.buf[0:8] = (100).to_bytes(8, 'little')

    print(f"[Main] Initial value: {int.from_bytes(shm.buf[0:8], 'little')}")

    processes = []
    for i in range(2):
        p = multiprocessing.Process(target=worker, args=(shm.name, i))
        processes.append(p)
        p.start()

    # Wait for workers
    for p in processes:
        p.join()

    final_value = int.from_bytes(shm.buf[0:8], 'little')
    print(f"[Main] Final value: {final_value}")

    # Cleanup
    shm.close()
    shm.unlink()  # Destroy shared memory block