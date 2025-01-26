# cython: language_level=3, freethreading_compatible=True
# distutils: language = c++
cimport cython
from libc.stdint cimport int64_t, uint64_t

cdef extern from "nazo_rand.hpp" namespace "Storm":
    void seed(uint64_t seed)
    int64_t uniform_int_variate_noargs()
    int64_t random_range(int64_t start, int64_t stop, int64_t step) nogil
    int64_t random_below(int64_t number) nogil
    int64_t uniform_int_variate(int64_t a, int64_t b) nogil
    double uniform_real_variate_noargs()
    double uniform_real_variate(double a, double b) nogil

cdef inline int64_t cy_random_below(int64_t number) except -1 nogil:
    return random_below(number)

cdef inline int64_t cy_uniform_int_variate(int64_t a, int64_t b) except -1 nogil:
    return uniform_int_variate(a, b)

cpdef int random_integer_noargs():
    return uniform_int_variate_noargs()

cpdef void shuffle(list array):
    cdef int i, j
    cdef object temp
    cdef int length = len(array)
    for i in range(length - 1, 0, -1):
        j = cy_uniform_int_variate(0, i)
        temp = array[i]
        array[i] = array[j]
        array[j] = temp


def randbelow(a:int) -> int:
    return random_below(a)

def randint(a:int, b:int) -> int:
    return cy_uniform_int_variate(a, b)



@cython.boundscheck(False)
@cython.wraparound(False)
cpdef object random_choice(object container):
    cdef Py_ssize_t index = cy_random_below(len(container))
    return container[index]

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef list[object] random_choices(object container, Py_ssize_t count):
    cdef Py_ssize_t container_length = len(container)
    return [container[cy_random_below(container_length)] for _ in range(count)]

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef list[object] random_sample(object container, Py_ssize_t count):
    cdef Py_ssize_t container_length = len(container)
    cdef Py_ssize_t i, j
    cdef list result = [None] * count
    cdef list temp = list(container)

    if count > container_length:
        raise ValueError("Sample larger than population")

    for i in range(count):
        j = uniform_int_variate(i, container_length - 1)
        result[i] = temp[j]
        temp[j] = temp[i]

    return result

cpdef int randrange(int start, int stop=0, int step=1):
    if stop == 0:
        stop, start = start, 0
    return random_range(start, stop, step)


cpdef double random_double(double a, double b):
    return uniform_real_variate(a, b)


cpdef double random_double_noargs():
    return uniform_real_variate_noargs()
