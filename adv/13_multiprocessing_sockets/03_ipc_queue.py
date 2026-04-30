# MPMC очереди сообщений

import multiprocessing as mp
import random
import time
from multiprocessing import Queue


def producer(q: Queue, producer_id: int, items: int):
    for i in range(items):
        item = f"P{producer_id}-{i}"
        q.put(item)
        print(f"Producer {producer_id}: {item}")
        time.sleep(random.uniform(0.01, 0.05))
    print(f"Producer {producer_id} finished")


def consumer(q: Queue, consumer_id: int):
    consumed = 0
    while True:
        item = q.get()
        if item is None:  # Сигнал завершения
            q.put(None)  # Возвращаем для других потребителей
            break
        consumed += 1
        print(f"Потребитель {consumer_id}: обработал {item}")
        time.sleep(random.uniform(0.02, 0.08))
    print(f"Consumer {consumer_id} precessed {consumed} elements")


if __name__ == "__main__":
    q = Queue()

    producers = []
    for i in range(3):
        p = mp.Process(target=producer, args=(q, i + 1, 5))
        producers.append(p)
        p.start()

    consumers = []
    for i in range(2):
        c = mp.Process(target=consumer, args=(q, i + 1))
        consumers.append(c)
        c.start()

    for p in producers:
        p.join()

    # finish message
    q.put(None)

    for c in consumers:
        c.join()
