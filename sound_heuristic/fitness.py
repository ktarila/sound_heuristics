"""Several fitness functions"""
import numpy as np


def f1(value):
    """Unimodal test function for optimisation algo
       Sphere function domain range [-100, 100]^n
       #list of real values in domain range
       Input: [value1, value2, ..., valuen]
       Output: value1^2 + value2^2 + ... + valuen^2
    """
    # value_array = np.array(value)
    return sum(np.square(value))


def f2(value):
    """Unimodal Test Function"""
    prod = np.product(np.abs(value))
    add = np.sum(np.abs(value))
    # print(prod, "+", add, " = ", prod + add)
    return prod + add
