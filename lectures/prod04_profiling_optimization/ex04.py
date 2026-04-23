import cProfile
import pstats
import time
from numba import jit

# def foo(x, y):
#     time.sleep(0.05)
#     return 2 * x + 2 * y

@jit(nopython=True, parallel=True)
def fibonacci(n):
    if n == 1:
        return [0]

    fib_list = [0, 1]

    for i in range(2, n):
        # time.sleep(0.05)
        fib_list.append(fib_list[i - 1] + fib_list[i - 2])

    return fib_list





start = time.time()
fibonacci(200)
end = time.time()
print(round(end - start, 4))

start = time.time()
fibonacci(200)
end = time.time()
print(end - start)
