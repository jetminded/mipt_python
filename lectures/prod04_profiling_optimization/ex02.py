# Cython via decorators - py file
# Нужно будет потом всё равно скомпилировать через cython
import cython

@cython.boundscheck(False)
@cython.wraparound(False)
def fibonacci(int n):
    cdef int i
    cdef list fib_list

    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib_list = [0, 1]

    for i in range(2, n):
        fib_list.append(fib_list[i - 1] + fib_list[i - 2])

    return fib_list