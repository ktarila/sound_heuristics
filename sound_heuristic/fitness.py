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
    fit = 0
    length = len(value) + 1
    for i in range(1, length):
        fit = fit + np.power(np.sum(value[0:i]), 2)
    return fit


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
    content = (ind * np.power(value, 4))
    return np.sum(content) + cfg.RAND_VALUE


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
    ind = np.linspace(1, len(value), len(value))
    val_one = np.sum(np.power(value, 2)) / 400
    val_two = np.product(np.cos(value / np.sqrt(ind)))
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
    # print(new_u)
    return np.sum(new_u)


def f12(value):
    """multimodal function"""
    length = len(value)
    ff1 = 10 * np.power((np.sin(np.pi * (1 + (value[0] + 1) / 4))), 2)
    ff2 = np.power(((value[0:length - 1] + 1) / 4), 2)
    ff3 = (
        1 + 10 * np.power((np.sin(
            np.pi * (1 + (value[1:length] + 1) / 4))), 2)
    )
    ff4 = np.power(((value[length - 1] + 1) / 4), 2)
    total = (np.pi / length) * (ff1 + np.sum(ff2 * ff3) + ff4)
    return total + u_sum(value, 10, 100, 4)


def f13(value):
    """multi modal function"""
    last = len(value) - 1
    first = np.sin(3 * np.pi * value[0]) ** 2
    second = np.sum(
        np.power((value[0:len(value) - 1] - 1), 2) * (
            1 + np.sin(3 * np.pi * value[1:len(value)]) ** 2)
    )
    third = np.power((value[last] - 1), 2) * (
        1 + np.sin(2 * np.pi * value[last]) ** 2)
    return 0.1 * (first + second + third) + u_sum(value, 5, 100, 4)


def f14(value):
    """Multi modal function
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


def f15(value):
    """Multi modal function
       dimension of value = 4
    """
    if len(value) != 4:
        raise Exception("Dimension of f15 must be equal to 4")

    array_a = np.array([0.1957, 0.1947, 0.1735, 0.16, 0.0844,
                        0.0627, 0.0456, 0.0342, 0.0323, 0.0235, 0.0246])
    array_b = np.array([0.25, 0.5, 1, 2, 4, 6, 8, 10, 12, 14, 16])
    array_b = 1 / array_b

    top = value[0] * (np.power(array_b, 2) + array_b * value[1])
    bottom = np.power(array_b, 2) + (array_b * value[2]) + value[3]

    return np.sum(np.power((array_a - (top / bottom)), 2))


def f16(value):
    """multi modal function
       dimension of value = 2
    """
    if len(value) != 2:
        raise Exception("Dimension of f16 must be equal to 2")
    return (4 * np.power(value[0], 2)) - (
        2.1 * np.power(value[0], 4)) + (
            (1 / 3) * np.power(value[0], 6)) + value[0] * value[1] - (
                4 * np.power(value[1], 2)) + (
                    4 * np.power(value[1], 4))


def f17(value):
    """multi modal function
       dimension of value = 2
    """
    first = np.power((value[1] - (
        np.power(value[0], 2)) * 5.1 / (
            4 * np.power(np.pi, 2)) + (
                5 / np.pi) * value[0] - 6), 2)

    second = 10 * (1 - (1 / (8 * np.pi))) * np.cos(value[0])
    return first + second + 10


def f18(value):
    """multimodal function
       dimension of value = 2
    """
    first = 1 + np.power((value[0] + value[1] + 1), 2) * (
        19 - 14 * value[0] + 3 * np.power(value[0], 2) - (
            14 * value[1]) + 6 * value[0] * value[1] + (
                3 * np.power(value[1], 2))
    )

    second = 30 + np.power((2 * value[0] - 3 * value[1]), 2) * (
        18 - 32 * value[0] + 12 * np.power(value[0], 2) + (
            48 * value[1]) - 36 * value[0] * value[1] + (
                27 * np.power(value[1], 2))
    )

    return first * second


def f19(value):
    """multimodal function
       dimension of value = 3
    """
    if len(value) != 3:
        raise Exception("Dimension of f19 must be equal to 3")
    array_a = np.array([[3, 10, 30],
                        [0.1, 10, 35],
                        [3, 10, 30],
                        [0.1, 10, 35]])
    array_c = np.array([1, 1.2, 3, 3.2])
    array_p = np.array([[0.3689, 0.117, 0.2673],
                        [0.4699, 0.4387, 0.747],
                        [0.1091, 0.8732, 0.5547],
                        [0.03815, 0.5743, 0.8828]])

    # fit = 0
    # for i in range(4):
    #     col_sum = 0
    #     length = len(value)
    #     for j in range(length):
    #         col_sum = col_sum - array_a[i, j] * (
    #             value[j] - array_p[i, j]) ** 2
    #     cont = array_c[i] * np.exp(col_sum)
    #     fit = fit - cont

    fit = 0
    for i in range(4):
        fit = fit - array_c[i] * np.exp(
            -(np.sum(
                array_a[i, :] * np.power(
                    (value - array_p[i, :]), 2)
            ))
        )
    return fit


def f20(value):
    """multimodal function
       dimension of value = 6
    """
    if len(value) != 6:
        raise Exception("Dimension of f19 must be equal to 6")
    array_a = np.array([[10, 3, 17, 3.5, 1.7, 8],
                        [0.05, 10, 17, 0.1, 8, 14],
                        [3, 3.5, 1.7, 10, 17, 8],
                        [17, 8, 0.05, 10, 0.1, 14]])

    array_c = np.array([1, 1.2, 3, 3.2])
    array_p = np.array([[0.1312, 0.1696, 0.5569, 0.0124, 0.8283, 0.5886],
                        [0.2329, 0.4135, 0.8307, 0.3736, 0.1004, 0.9991],
                        [0.2348, 0.1415, 0.3522, 0.2883, 0.3047, 0.6650],
                        [0.4047, 0.8828, 0.8732, 0.5743, 0.1091, 0.0381]])

    fit = 0
    for i in range(4):
        fit = fit - array_c[i] * np.exp(
            -(np.sum(
                array_a[i, :] * np.power(
                    (value - array_p[i, :]), 2)
            ))
        )
    return fit


def f21_23(value, last):
    """method for function 21 - 23
       difference between these functions is the last
       index in range
    """
    a_array = np.array([[4, 4, 4, 4],
                        [1, 1, 1, 1],
                        [8, 8, 8, 8],
                        [6, 6, 6, 6],
                        [3, 7, 3, 7],
                        [2, 9, 2, 9],
                        [5, 5, 3, 3],
                        [8, 1, 8, 1],
                        [6, 2, 6, 2],
                        [7, 3.6, 7, 3.6]])
    c_array = np.array([0.1, 0.2, 0.2, 0.4, 0.4, 0.6, 0.3, 0.7, 0.5, 0.5])

    fit = 0
    for i in range(last):
        fit = fit - np.power(
            (np.sum((value - a_array[i, :]) * (
                value - a_array[i, :]).transpose()) + c_array[i]), -1
        )

    return fit


def f21(value):
    """multi modal function
       fixed dimension. dimension value = 4
    """
    if len(value) != 4:
        raise Exception("Dimension of f21 must be equal to 4")
    return f21_23(value, 5)


def f22(value):
    """multi modal function
       fixed dimension. dimension value = 4
    """
    if len(value) != 4:
        raise Exception("Dimension of f22 must be equal to 4")
    return f21_23(value, 7)


def f23(value):
    """multi modal function
       fixed dimension. dimension value = 4
    """
    if len(value) != 4:
        raise Exception("Dimension of f23 must be equal to 4")
    return f21_23(value, 10)
