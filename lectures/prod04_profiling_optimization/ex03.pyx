# cython: полноценный pyx
# Тоже надо будет скомпилировать через cython

def fibonacci(int n):
    cdef int i
    cdef int a = 0
    cdef int b = 1
    cdef list fib_list

    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib_list = [0, 1]

    for i in range(2, n):
        a = fib_list[i - 2]
        b = fib_list[i - 1]
        fib_list.append(a + b)

    return fib_list