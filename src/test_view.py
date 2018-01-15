from math import isclose

import pytest

from view import Point


class TestPoint:

    def setup(self):
        self.point = Point(2.1, -.3, 4)

    def test_slots(self):
        self.point.x = -.7
        self.point.y += 3
        assert self.point == Point(-0.7, 2.7, 4)

        with pytest.raises(AttributeError):
            self.point.w = 1

    def test_repr(self):
        assert repr(self.point) == 'Point(x=2.1, y=-0.3, z=4)'

    def test_str(self):
        assert str(self.point) == 'Point(2.100, -0.300, 4.000)'

    def test_format(self):
        point = Point(2, 4 / 3, -3.5)
        assert format(point, '.2f') == 'Point(2.00, 1.33, -3.50)'

    # def test_iter(self):
    #     x, y, z = self.point
    #     assert (x, y, z) == tuple(self.point) == (2.1, -0.3, 4)

    # def test_len(self):
    #     assert len(self.point) == 3

    def test_bool(self):
        assert bool(self.point)

    @staticmethod
    def assert_points_are_close(point_1: Point, point_2: Point) -> bool:
        assert isclose(point_1.x, point_2.x)
        assert isclose(point_1.y, point_2.y)
        assert isclose(point_1.z, point_2.z)

    def test_add(self):
        self.assert_points_are_close(
            self.point + (3, -1, 0), Point(5.1, -1.3, 4))

    def test_sub(self):
        self.assert_points_are_close(
            self.point - (-1, 0.5, 4.2), Point(3.1, -0.8, -0.2))

    def test_radd(self):
        self.assert_points_are_close(
            (3, 1, 3) + self.point, Point(5.1, 0.7, 7))

    def test_rsub(self):
        self.assert_points_are_close(
            (-1, 3, 4) - self.point, Point(3.1, -3.3, 0))

    def test_iadd(self):
        self.point += 1, 3, 1
        self.assert_points_are_close(self.point, Point(3.1, 2.7, 5))

    def test_isub(self):
        self.point -= 0.1, -4, -4.12
        self.assert_points_are_close(self.point, Point(2, 3.7, 8.12))


if __name__ == '__main__':
    pytest.main()
