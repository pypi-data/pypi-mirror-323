import numpy as np


class WrongCountOfArgs(Exception):
    def __init__(self, *args):
        self.message = "Interpolator support only 1D - f(x), 2D - f(x, y), or 3D f(x, y, z) interpolation"

    def __str__(self):
        return self.message

class WrongData(Exception):
    def __init__(self, type: int, count_of_args: int, function_arr_shape: np.ndarray):
        if type == 0:
            self.message = f"Your function data must be array with shape ({['some int'] * count_of_args}) but your array has shape {function_arr_shape}"
        if type == 1:
            self.message = f"array of resolutions must be array with shape ({count_of_args}), but your array has shape {function_arr_shape}"

    def __str__(self):
        return self.message

class ZeroResolution(Exception):
    def __str__(self):
        return "Resolution array can't consist 0 values"

class Interp:
    def __init__(self, function_array: np.ndarray, count_of_args: int, resolutions: np.ndarray):
        self.__function_array = function_array
        self.__count_of_args = count_of_args
        self.__resolutions = resolutions
        if count_of_args not in [1, 2, 3]:
            raise WrongCountOfArgs

        if len(self.__function_array.shape) != count_of_args:
            raise WrongData(0, count_of_args, function_array.shape)
        if list(self.__resolutions.shape) != [count_of_args]:
            raise WrongData(1, count_of_args, resolutions.shape)
        if 0 in resolutions:
            raise ZeroResolution


    def __get_n_for_1D_function(self, dot_1: np.ndarray, dot_2: np.ndarray) -> np.ndarray:
        vector = dot_2 - dot_1
        alpha = np.arctan(vector[1] / vector[0])
        alpha1 = alpha + np.pi / 2
        n = np.array([np.cos(alpha1), np.sin(alpha1)])
        return n

    def __get_n_for_2D_function(self, dot_1: np.ndarray, dot_2: np.ndarray, dot_3: np.ndarray) -> np.ndarray:
        vector1 = dot_2 - dot_1
        vector2 = dot_3 - dot_1
        n = np.cross(vector1, vector2)
        return n

    def __get_n_for_3D_function(self, dot_1: np.ndarray, dot_2: np.ndarray, dot_3: np.ndarray,
                              dot_4: np.ndarray) -> np.ndarray:
        w1 = dot_1[3]
        w2 = dot_2[3]
        w3 = dot_3[3]
        w4 = dot_4[3]
        A = 1
        D = -1 / (w2 - w1)
        B = (w3 - w1) / (w2 - w1)
        C = (w4 - w1) / (w2 - w1)
        n = np.array([A, B, C, D])
        return n

    def get_value(self, *args):
        args = args / self.__resolutions
        if len(args) != self.__count_of_args:
            raise ValueError
        for i in range(len(args)):
            if args[i] < 0 or args[i] >= self.__function_array.shape[i]:
                raise ValueError

        result = np.zeros(self.__count_of_args)

        if self.__count_of_args == 1:
            x0 = int(args[0])
            x1 = x0 + 1
            y0 = self.__function_array[x0]
            y1 = self.__function_array[x1]
            n = self.__get_n_for_1D_function(np.array([x0, y0]), np.array([x1, y1]))
            result = -n[0] * (args[0] - x0) / n[1] + y0

        elif self.__count_of_args == 2:
            x0, y0 = list(map(int, args))
            z0 = self.__function_array[x0, y0]
            x1 = x0 + 1
            y1 = y0 + 1
            z1 = self.__function_array[x1, y0]
            z2 = self.__function_array[x0, y1]

            m0 = np.array([x0, y0, z0])
            m1 = np.array([x1, y0, z1])
            m2 = np.array([x0, y1, z2])

            n = self.__get_n_for_2D_function(m0, m1, m2)

            result = (- n[0] * (args[0] - x0) - n[1] * (args[1] - y0)) / n[2] + z0
        elif self.__count_of_args == 3:
            x0, y0, z0 = list(map(int, args))
            w0 = self.__function_array[x0, y0, z0]
            x1 = x0 + 1
            y1 = y0 + 1
            z1 = z0 + 1
            w1 = self.__function_array[x1, y0, z0]
            w2 = self.__function_array[x0, y1, z0]
            w3 = self.__function_array[x0, y0, z1]

            m1 = np.array([x0, y0, z0, w0])
            m2 = np.array([x1, y0, z0, w1])
            m3 = np.array([x0, y1, z0, w2])
            m4 = np.array([x0, y0, z1, w3])

            n = self.__get_n_for_3D_function(m1, m2, m3, m4)
            result = (-n[0] * (args[0] - x0) - n[1] * (args[1] - y0) - n[2] * (args[2] - z0)) / n[3] + w0
        return result
#




#
# # a = []
# # for i in range(0, 10000):
# #     a.append((i / 100) ** 2)
# # c = np.array(a)
# # # b = np.array([[0, 1, 2, 3, 4, 5],
# # #               [1, 2, 3, 4, 5, 6],
# # #               [2, 3, 4, 5, 6, 7],
# # #               [3, 4, 5, 6, 7, 8],
# # #               [4, 5, 6, 7, 8, 9],
# # #               [5, 6, 7, 8, 9, 10]])
# c = np.zeros([100, 100, 100])
# for x in range(100):
#     for y in range(100):
#         for z in range(100):
#             c[x, y, z] = x * y * z / (10 * 10 * 10)
#
# interp = Interp(c, 3, np.array([0.1, 0.1, 0.1]))
# # print(interp.get_value(0.11, 0.5))
# print(interp.get_value(3, 3, 3.35))
