# Обсудить GIL и потоки, отличие IO-bound и CPU-bound задач

import multiprocessing as mp
import os
import time

a = []

def worker(name: str, duration: float):
    """Функция, выполняемая в дочернем процессе"""
    pid = os.getpid()
    a.append(pid)
    print(f"Процесс '{name}' запущен (PID: {pid})")
    time.sleep(duration)
    print(f"Процесс '{name}' завершён")

    # обсудить, почему оба процесса выведут список из одного элемента
    print(a)


# обсудить зачем писать эту строчку и что будет если ее забыть написать
if __name__ == "__main__":
    print(f"Главный процесс (PID: {os.getpid()})")

    p1 = mp.Process(target=worker, args=("Alice", 2))
    p2 = mp.Process(target=worker, args=("Bob", 1))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Все процессы завершены")