"""Several fitness functions"""
import numpy as np

from sound_heuristic import config as cfg


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


def f3(value):
    """unimodal test function"""
    total = 0
    for index in range(1, len(value)):
        total += np.power(np.sum(value[:index]), 2)
    return total


def f4(value):
    """unimodal test function"""
    return np.amax(np.abs(value))


def f5(value):
    """unimodal function
       RHO = 60 seems to get best results
    """
    val_x = np.copy(value)
    x_plus_1 = np.copy(value)
    # remove last element
    val_x = np.delete(val_x, len(value) - 1)
    # remove first element
    x_plus_1 = np.delete(x_plus_1, 0)
    new_vec = 100 * np.power(
        (x_plus_1 - np.power(val_x, 2)), 2) + np.power((val_x - 1), 2)
    return np.sum(new_vec)


def f6(value):
    """unimodal function"""
    return np.sum(np.power((value + 0.5), 2))


def f7(value):
    """unimodal function"""
    ind = np.linspace(1, len(value), len(value))
    content = (ind * np.power(value, 4)) + cfg.RAND_VALUE
    return np.sum(content)


def f8(value):
    """multimodal function"""
    return np.sum((-1 * value) * np.sin(np.sqrt(np.abs(value))))


def f9(value):
    """multimodal function"""
    return np.sum(np.power(value, 2) - (10 * np.cos(
        2 * np.pi * value)) + 10)
