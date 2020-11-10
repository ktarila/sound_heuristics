"""Several fitness functions"""
import numpy as np

from sound_heuristic import config as cfg


def f1(value):
    """Unimodal test function for optimisation algo
       Sphere function domain range [-100, 100]^n
       # list of real values in domain range
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


def f10(value):
    """multimodal function"""
    val_one = -20 * np.exp(-0.2 * np.sqrt(
        (1 / len(value)) * np.sum(np.power(value, 2))))

    val_two = np.exp(
        (1 / len(value)) * np.sum(np.cos(2 * np.pi * value)))

    return val_one - val_two + 20 + np.e


def f11(value):
    """multimodal function"""
    val_one = (1 / 400) * np.sum(np.power(value, 2))
    val_two = np.product(np.cos(value / np.sqrt(1)))
    return val_one - val_two + 1


def u_sum(value, param_1, param_2, param_3):
    """Function to compute f12 and f13"""
    new_u = np.copy(value)
    minus_p1 = param_1 * -1
    new_u = np.where(
        new_u > param_1, param_2 * (new_u - param_1) ** param_3, new_u)
    new_u = np.where(
        np.logical_and(new_u > minus_p1, new_u < param_1), 0, new_u)
    new_u = np.where(
        new_u < minus_p1, param_2 * (-1 * new_u - param_1) ** param_3, new_u)
    return np.sum(new_u)


def f12(value):
    """multimodal function"""
    last = len(value) - 1
    val_y = 1 + ((1 + value) / 4)
    val_y_last = val_y[last]
    y_plus_1 = np.copy(val_y)
    # remove last because sum is to n - 1
    val_y = np.delete(val_y, last)
    # remove first because adding yi and yi+1
    y_plus_1 = np.delete(y_plus_1, 0)
    first = 10 * np.sin(np.pi * val_y[0])
    second = np.sum(
        np.power((val_y - 1), 2) * (
            1 + (10 * np.sin(np.pi * y_plus_1) ** 2))
    )
    third = np.power((val_y_last - 1), 2)
    return (np.pi / len(value)) * (
        first + second + third) + u_sum(value, 10, 100, 4)


def f13(value):
    """multi modal function"""
    last = len(value) - 1
    first = np.sin(3 * np.pi * value[0]) ** 2
    second = np.sum(
        np.power((value - 1), 2) * (
            1 + np.sin((3 * np.pi * value) + 1) ** 2)
    )
    third = np.power((value[last] - 1), 2) * (
        1 + np.sin(2 * np.pi * value[last]) ** 2)

    return 0.1 * (first + second + third) + u_sum(value, 5, 100, 4)


def f14(value):
    """Unimodal function
       dimension of value = 2
    """
    if len(value) != 2:
        raise Exception("Dimension of f14 must be equal to 2")
    array_a = np.array(
        [[-32.0, -16, 0, 16, 32, -32, -16, 0, 16, 32, -32,
          -16, 0, 16, 32, -32, -16, 0, 16, 32, -32, -16, 0, 16, 32], [
              -32, -32, -32, -32, -32, -16, -16, -16, -16, -16, 0, 0, 0, 0, 0,
              16, 16, 16, 16, 16, 32, 32, 32, 32, 32]])
    # get number of columns --- should be equal 25
    length = array_a[0, :].shape[0]

    bottom = np.array([np.sum(np.power((value - array_a[:, j]), 6))
                       for j in range(length)])

    line = np.linspace(1, length, length)
    fit = np.power((1 / 500 + np.sum(1 / (line + bottom))), -1)
    return fit
