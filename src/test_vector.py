import inspect
from math import isclose

import pytest

from vector import Vector2D


def parametrize(*data):
    def decorator(function):
        sig = ', '.join(inspect.signature(function).parameters)
        pytest.mark.parametrize(sig, data)(function)
        return function
    return decorator


VALID_VECTOR_DATA = (
    [3, 4],
    [-4, 5],
    [0.4, 2],
    [0, 0],
    [-43.1, -4],
    [5.0, 41.542],
)

VECTORS = tuple(Vector2D(x, y) for x, y in VALID_VECTOR_DATA)


@parametrize(
    ('a', 3),
    (3, None),
    ('2', 4),
)
def test_invalid_init(x, y):
    with pytest.raises(TypeError):
        Vector2D(x, y)


@parametrize(
    ([3.2, 0.1], [-3.2, -0.1]),
    ([-4, 0], [4, 0]),
)
def test_neg(vector_xy, result_xy):
    vector = Vector2D(*vector_xy)
    result = Vector2D(*result_xy)

    assert -vector == result


@parametrize(
    (0, 0, 0),
    (3, 4, 5),
    (12, -5, 13),
    (-2, -1.5, 2.5),
)
def test_length(x, y, length):
    assert Vector2D(x, y).length == length
    assert Vector2D(y, x).length == length


@parametrize(
    ([3, 4], 10, [6, 8]),
    ([0, 2.2], 93, [0, 93]),
)
def test_set_length(vector_xy, length, result_xy):
    vector = Vector2D(*vector_xy)
    result = Vector2D(*result_xy)

    vector.length = length
    assert vector == result


@parametrize(*range(-5, 6))
def test_set_length_zero_vector_error(length):
    with pytest.raises(ValueError):
        Vector2D(0, 0).length = length


@parametrize(
    ([3, 2], (-1.5, 3), [1.5, 5]),
    ([4, -1], [2.1, 0], [6.1, -1]),
    ([4, 1.8], Vector2D(2.1, 0), [6.1, 1.8]),
)
def test_add(vector_xy, other, result_xy):
    vector = Vector2D(*vector_xy)
    result = Vector2D(*result_xy)

    assert vector + other == result
    assert other + vector == result


@parametrize(
    ([3, 9], Vector2D(2, 3), [1, 6]),
    ([4.3, 0], [3, 5], [1.2999999999999998, -5]),
    ([-2, -12.43], (-5.1, 4), [3.0999999999999996, -16.43])
)
def test_sub(vector_xy, other, result_xy):
    vector = Vector2D(*vector_xy)
    result = Vector2D(*result_xy)

    assert vector - other == result


@parametrize(
    ((4, 0.2), 4, (16, 0.8)),
    ((-2, 0), 5.5, (-11, 0)),
    ((4, 7), 0.3, (1.2, 2.1)),
)
def test_mul(vector_xy, other, result_xy):
    vector = Vector2D(*vector_xy)
    result = Vector2D(*result_xy)

    assert vector*other == result
    assert other*vector == result


@parametrize(*VECTORS)
def test_mul_by_1(vector):
    assert vector*1 == vector
    assert 1*vector == vector


@parametrize(*VECTORS)
def test_mul_by_0(vector):
    zero_vector = Vector2D(0, 0)

    assert vector*0 == zero_vector
    assert 0*vector == zero_vector


@parametrize(
    ([2, 3], 2, [4, 6]),
    ([0.5, 0], 29, [14.5, 0]),
    ([4.53, 54.32], 0, [0, 0]),
)
def test_imul(vector_xy, other, result_xy):
    vector = Vector2D(*vector_xy)
    result = Vector2D(*result_xy)

    vector *= other
    assert vector == result


@parametrize(
    ([3, 4], 2, [1.5, 2]),
    ([2.1, -4], 4, [0.525, -1]),
    ([0.5, 8.1], 0.5, [1, 16.2]),
)
def test_div(vector_xy, other, result_xy):
    vector = Vector2D(*vector_xy)
    result = Vector2D(*result_xy)

    assert vector / other == result


@parametrize(*VECTORS)
def test_div_by_0(vector):
    with pytest.raises(ZeroDivisionError):
        vector / 0


@parametrize(
    ([3, 4], 90, [4.000000000000001, -2.999999999999999]),
    ([0, 1.4142135623730951], 45, [1, 1.0000000000000002]),
)
def test_rotate_clockwise(vector_xy, angle, result_xy):
    vector = Vector2D(*vector_xy)
    result = Vector2D(*result_xy)

    vector.rotate_clockwise(angle)
    assert vector == result


@parametrize(
    ([1, 1], [-1, -1], -2),
)
def test_matmul(vector_xy, other, result):
    vector = Vector2D(*vector_xy)

    assert vector @ other == result


if __name__ == '__main__':
    pytest.main()
