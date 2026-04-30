import multiprocessing
import time
import random
from multiprocessing import Lock, RLock, Semaphore, Event, Barrier, Value, Array, Manager


# ============================================================================
# Проблема без синхронизации
# ============================================================================

class UnsafeCounter:
    """НЕБЕЗОПАСНЫЙ счетчик - демонстрация проблемы"""

    def __init__(self):
        self.value = multiprocessing.Value('i', 0)

    def increment(self):
        # Эта операция НЕ атомарна!
        # Процессор делает: read -> add -> write
        # Между read и write другой процесс может изменить значение!
        current = self.value.value
        time.sleep(0.000001)  # Имитация задержки (увеличивает шанс race condition)
        self.value.value = current + 1

    def get(self):
        return self.value.value


def unsafe_worker(counter, worker_id, increments):
    for _ in range(increments):
        counter.increment()
    print(f"Worker {worker_id}: закончил (думает что сделал {increments})")


def demo_unsafe():
    """Демонстрация проблемы гонки данных"""
    print("НЕБЕЗОПАСНЫЙ СЧЕТЧИК (БЕЗ синхронизации)")
    print("=" * 60)

    counter = UnsafeCounter()
    num_workers = 5
    increments_per_worker = 1000
    expected = num_workers * increments_per_worker

    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(target=unsafe_worker, args=(counter, i, increments_per_worker))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    actual = counter.get()
    print(f"\nОжидаемое значение: {expected}")
    print(f"Фактическое значение: {actual}")


# ============================================================================
# МЕТОД 1: Lock (Блокировка) - самый простой и распространенный
# ============================================================================

class LockCounter:
    """Счетчик с использованием Lock"""

    def __init__(self):
        self.value = multiprocessing.Value('i', 0)
        self.lock = Lock()  # Блокировка

    def increment(self):
        with self.lock:  # Захватываем блокировку
            current = self.value.value
            time.sleep(0.000001)  # типа работаем
            self.value.value = current + 1
        # Блокировка автоматически освобождается благодаря with

    def get(self):
        with self.lock:
            return self.value.value


def lock_worker(counter, worker_id, increments):
    """Worker с Lock счетчиком"""
    for _ in range(increments):
        counter.increment()
    print(f"Worker {worker_id}: закончил, счетчик = {counter.get()}")


def demo_lock():
    """Демонстрация Lock"""
    print("LOCK - Взаимное исключение")
    counter = LockCounter()
    num_workers = 5
    increments_per_worker = 1000
    expected = num_workers * increments_per_worker

    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(target=lock_worker, args=(counter, i, increments_per_worker))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    actual = counter.get()
    print(f"\nОжидаемое значение: {expected}")
    print(f"Фактическое значение: {actual}")

    print("Lock не позволяет вложенные вызовы (сделать ctrl + C)")
    try:
        with counter.lock:
            with counter.lock:  # deadlock! тк мьютекс уже залочен
                print("  Это сообщение не будет напечатано")
    except:
        print("Lock завис бы навсегда!")


# ============================================================================
# МЕТОД 2: RLock (Reentrant Lock) - рекурсивная блокировка
# ============================================================================

class RLockCounter:
    """Счетчик с использованием RLock (рекурсивная блокировка)"""

    def __init__(self):
        self.value = multiprocessing.Value('i', 0)
        self.lock = RLock()  # Рекурсивная блокировка

    def increment(self):
        with self.lock:
            current = self.value.value
            time.sleep(0.000001)
            self.value.value = current + 1

    def increment_multiple(self, times):
        with self.lock:
            for _ in range(times):  # Вложенные вызовы работают!
                self.increment()

    def get(self):
        with self.lock:
            return self.value.value


def rlock_worker(counter, worker_id, increments):
    """Worker с RLock счетчиком"""
    # Используем метод с вложенными вызовами
    counter.increment_multiple(increments)
    print(f"Worker {worker_id}: закончил, счетчик = {counter.get()}")


def demo_rlock():
    """Демонстрация RLock"""
    print("RLOCK (Рекурсивная блокировка)")

    counter = RLockCounter()
    num_workers = 3
    increments_per_worker = 1000

    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(target=rlock_worker, args=(counter, i, increments_per_worker))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"\nФинальное значение: {counter.get()}")


# ============================================================================
# Semaphore (Семафор) - ограничение количества доступов
# ============================================================================

class SemaphoreCounter:
    """Счетчик с использованием Semaphore (ограничение параллелизма)"""

    def __init__(self, max_concurrent=2):
        self.value = multiprocessing.Value('i', 0)
        self.semaphore = Semaphore(max_concurrent)  # Только 2 процесса одновременно
        self.max_concurrent = max_concurrent
        self.current_workers = Value('i', 0)

    def increment(self, worker_id):
        # Пытаемся войти в критическую секцию (ждем, если занято)
        acquired = self.semaphore.acquire(timeout=1)
        if not acquired:
            print(f"  Worker {worker_id}: не удалось получить доступ (таймаут)")
            return False

        try:
            # Считаем активные процессы
            with self.current_workers.get_lock():
                self.current_workers.value += 1
                active = self.current_workers.value

            print(f"  Worker {worker_id}: вошел (активно: {active}/{self.max_concurrent})")

            # Критическая секция
            current = self.value.value
            time.sleep(0.05)
            self.value.value = current + 1

            with self.current_workers.get_lock():
                self.current_workers.value -= 1
                active = self.current_workers.value

            print(f"  Worker {worker_id}: вышел (активно: {active}/{self.max_concurrent})")
            return True
        finally:
            self.semaphore.release()

    def get(self):
        return self.value.value


def semaphore_worker(counter, worker_id, increments):
    """Worker с Semaphore счетчиком"""
    successful = 0
    for _ in range(increments):
        if counter.increment(worker_id):
            successful += 1
        time.sleep(0.01)
    print(f"Worker {worker_id}: выполнено {successful}/{increments} операций")


def demo_semaphore():
    """Демонстрация Semaphore"""
    print("SEMAPHORE - Ограничение параллельного доступа")

    counter = SemaphoreCounter(max_concurrent=2)
    num_workers = 5
    increments_per_worker = 3

    print(f"Одновременно могут работать только 2 процесса\n")

    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(target=semaphore_worker, args=(counter, i, increments_per_worker))
        processes.append(p)
        p.start()
        time.sleep(0.1)  # Небольшая задержка между запусками

    for p in processes:
        p.join()

    print(f"\nФинальное значение: {counter.get()}")


# ============================================================================
# Event (Событие) - для сигнализации и паузы
# ============================================================================

class EventCounter:
    """Счетчик с использованием Event (управление паузой)"""

    def __init__(self):
        self.value = multiprocessing.Value('i', 0)
        self.lock = Lock()
        self.pause_event = Event()  # Событие для паузы
        self.stop_event = Event()  # Событие для остановки
        self.pause_event.set()  # Изначально не на паузе

    def increment(self):
        with self.lock:
            current = self.value.value
            time.sleep(0.001)
            self.value.value = current + 1

    def pause(self):
        """Поставить счетчик на паузу"""
        self.pause_event.clear()
        print("СЧЕТЧИК НА ПАУЗЕ")

    def resume(self):
        """Возобновить работу"""
        self.pause_event.set()
        print("СЧЕТЧИК ВОЗОБНОВЛЕН")

    def stop(self):
        """Остановить"""
        self.stop_event.set()

    def should_continue(self):
        """Проверить, можно ли продолжать"""
        return not self.stop_event.is_set()

    def should_pause(self):
        """Ждать, если на паузе"""
        self.pause_event.wait()  # Блокируется, если на паузе

    def get(self):
        with self.lock:
            return self.value.value


def event_worker(counter, worker_id, increments):
    """Worker с Event счетчиком (может быть приостановлен)"""
    for i in range(increments):
        # Проверяем, не остановили ли нас
        if not counter.should_continue():
            print(f"Worker {worker_id}: получил сигнал остановки")
            break

        # Ждем, если на паузе
        counter.should_pause()

        # Инкрементируем
        counter.increment()

        if (i + 1) % 50 == 0:
            print(f"Worker {worker_id}: сделано {i + 1} инкрементов")

        time.sleep(0.01)

    print(f"Worker {worker_id}: закончил, всего сделано до остановки")


def demo_event():
    """Демонстрация Event"""
    print("EVENT - Управление паузой и остановкой")
    counter = EventCounter()

    # Запускаем 2 рабочих процесса
    processes = []
    for i in range(2):
        p = multiprocessing.Process(target=event_worker, args=(counter, i, 200))
        processes.append(p)
        p.start()

    time.sleep(1)
    print("Ставим счетчик на паузу...")
    counter.pause()
    time.sleep(2)

    print("Возобновляем работу...")
    counter.resume()
    time.sleep(2)

    print("Останавливаем счетчик...")
    counter.stop()

    for p in processes:
        p.join()

    print(f"\nФинальное значение: {counter.get()}")


# ============================================================================
# Barrier (Барьер) - синхронизация фаз
# ============================================================================

class BarrierCounter:
    """Счетчик с Barrier (все процессы синхронизируются)"""

    def __init__(self):
        self.value = multiprocessing.Value('i', 0)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            current = self.value.value
            time.sleep(0.001)
            self.value.value = current + 1
            return self.value.value

    def get(self):
        with self.lock:
            return self.value.value


def barrier_worker(counter, barrier, worker_id, increments_per_phase):
    """Worker, который синхронизируется через Barrier после каждой фазы"""

    for phase in range(3):
        # Фаза: каждый worker делает инкременты
        print(f"Worker {worker_id}: фаза {phase} - начинаю")

        for _ in range(increments_per_phase):
            current = counter.increment()

        print(f"Worker {worker_id}: фаза {phase} - закончил (счетчик={counter.get()})")

        # Ждем всех остальных
        print(f"Worker {worker_id}: жду у барьера...")
        barrier.wait()
        print(f"Worker {worker_id}: прошел барьер, продолжаю")

        time.sleep(0.1)

    print(f"Worker {worker_id}: все фазы завершены")


def demo_barrier():
    """Демонстрация Barrier"""
    print("BARRIER - Синхронизация фаз выполнения")

    num_workers = 3
    barrier = Barrier(num_workers)
    counter = BarrierCounter()

    print(f"{num_workers} worker'а синхронизируются после каждой фазы\n")

    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(target=barrier_worker, args=(counter, barrier, i, 5))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"\nФинальное значение: {counter.get()}")
    print(f"Всего инкрементов: 3 фазы × 3 worker'а × 5 инкрементов = 45")


# ============================================================================
# Manager - высокоуровневая синхронизация
# ============================================================================
def worker(worker_id, increments, counter, lock, results_queue):
    """Worker с Manager счетчиком"""
    local_count = 0
    for _ in range(increments):
        with lock:
            counter.value += 1
            local_count += 1
        time.sleep(0.0001)

    results_queue.put((worker_id, local_count))
    print(f"Worker {worker_id}: закончил (сделал {local_count})")


def demo_manager():
    """Демонстрация Manager - РАБОЧАЯ ВЕРСИЯ"""
    print("MANAGER - Высокоуровневая синхронизация")

    manager = Manager()
    counter = manager.Value('i', 0)
    lock = manager.Lock()
    results_queue = multiprocessing.Queue()

    num_workers = 5
    increments_per_worker = 1000

    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(target=worker, args=(i, increments_per_worker, counter, lock, results_queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    actual = counter.value
    expected = num_workers * increments_per_worker

    print(f"\nОжидаемое значение: {expected}")
    print(f"Фактическое значение: {actual}")

    if actual == expected:
        print(f"Победа")

    manager.shutdown()


# ============================================================================
# Value/Array с Lock (Низкоуровневая синхронизация)
# ============================================================================

class ValueArrayCounter:
    """Счетчик через Value и Array (с ручной синхронизацией)"""

    def __init__(self):
        # 'i' = integer
        self.value = Value('i', 0)
        self.history = Array('i', [0] * 10)
        self.lock = Lock()
        self.history_index = 0

    def increment(self):
        with self.lock:
            # Инкрементируем значение
            self.value.value += 1

            # Сохраняем в историю
            self.history[self.history_index % 10] = self.value.value
            self.history_index += 1

    def get(self):
        with self.lock:
            return self.value.value

    def get_history(self):
        with self.lock:
            return list(self.history)


def valuearray_worker(counter, worker_id, increments):
    """Worker с Value/Array счетчиком"""
    for _ in range(increments):
        counter.increment()
        time.sleep(0.0001)
    print(f"Worker {worker_id}: закончил, счетчик = {counter.get()}")


def demo_valuearray():
    """Демонстрация Value и Array"""
    print("VALUE/ARRAY - Разделяемая память с Lock")

    counter = ValueArrayCounter()
    num_workers = 3
    increments_per_worker = 100

    processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(target=valuearray_worker, args=(counter, i, increments_per_worker))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    actual = counter.get()
    expected = num_workers * increments_per_worker

    print(f"Ожидаемое значение: {expected}")
    print(f"Фактическое значение: {actual}")
    print(f"История значений: {counter.get_history()}")


if __name__ == "__main__":
    demo_unsafe()
    print("-" * 30)
    demo_lock()
    print("-" * 30)
    demo_rlock()
    print("-" * 30)
    demo_semaphore()
    print("-" * 30)
    demo_event()
    print("-" * 30)
    demo_barrier()
    print("-" * 30)
    demo_manager()
    print("-" * 30)
    demo_valuearray()
