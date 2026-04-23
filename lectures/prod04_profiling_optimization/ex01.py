import cProfile
import pstats
import time

def foo(x, y):
    time.sleep(0.05)
    return 2 * x + 2 * y


def fibonacci(n, foo):
    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib_list = [0, 1]

    for i in range(2, n):
        time.sleep(0.05)
        fib_list.append(foo(fib_list[i - 1], fib_list[i - 2]))

    return fib_list


with cProfile.Profile() as pr:
    fibonacci(50, foo)

res = pstats.Stats(pr)
res.sort_stats(pstats.SortKey.TIME)
res.print_stats()
res.dump_stats("res.prof")
# print(end - start) 

# timeit
# cprofile
# 
# tuna
