# 02_process_pool.py
# Решаем cpu-bound задачу
import multiprocessing as mp
import time
from math import sqrt


def is_prime(n: int) -> bool:
    """Вычислительно сложная задача)"""
    if n < 2:
        return False
    for i in range(2, int(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


if __name__ == "__main__":
    test_numbers = [
        100000000003,
        100000000019,
        1000000000000037,
        1000000000000091,
    ]


    start = time.time()
    prime_results = [is_prime(x) for x in test_numbers]
    elapsed = time.time() - start

    for num, is_prime_result in zip(test_numbers, prime_results):
        print(f"{num} - {'простое' if is_prime_result else 'составное'}")
    print(f"Время выполнения в одном процессе: {elapsed:.2f} сек")

    with mp.Pool(processes=mp.cpu_count()) as pool:
        start = time.time()
        prime_results = pool.map(is_prime, test_numbers)
        elapsed = time.time() - start

        for num, is_prime_result in zip(test_numbers, prime_results):
            print(f"{num} - {'простое' if is_prime_result else 'составное'}")
        print(f"Время выполнения в пуле процессов: {elapsed:.2f} сек")