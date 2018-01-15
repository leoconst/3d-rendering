from math import isclose

from pytest import main, raises

from geometry import shapes, lines, Mesh, Point, RGBA, TriangleArray


class TestPoint:

    def setup(self):
        self.point = Point(2.1, -.3, 4)

    def test_slots(self):
        self.point.x = -.7
        self.point.y += 3
        assert self.point == Point(-0.7, 2.7, 4)

        with raises(AttributeError):
            self.point.w = 1

    def test_repr(self):
        assert repr(self.point) == 'Point(x=2.1, y=-0.3, z=4)'

    def test_str(self):
        assert str(self.point) == 'Point(2.10, -0.30, 4.00)'

    def test_format(self):
        point = Point(2, 4 / 3, -3.5)
        assert format(point, '.3f') == 'Point(2.000, 1.333, -3.500)'

    def test_iter(self):
        x, y, z = self.point
        assert (x, y, z) == tuple(self.point) == (2.1, -0.3, 4)

    def test_len(self):
        assert len(self.point) == 3

    def test_bool(self):
        assert bool(self.point)

    @staticmethod
    def assert_points_are_close(point_1: Point, point_2: Point) -> bool:
        for axis_1, axis_2 in zip(point_1, point_2):
            assert isclose(axis_1, axis_2)

    def test_add(self):
        self.assert_points_are_close(
            self.point + (3, -1, 0), Point(5.1, -1.3, 4))

    def test_sub(self):
        self.assert_points_are_close(
            self.point - (-1, 0.5, 4.2), Point(3.1, -0.8, -0.2))

    def test_radd(self):
        self.assert_points_are_close((3, 1, 3) + self.point, (5.1, 0.7, 7))

    def test_rsub(self):
        self.assert_points_are_close((-1, 3, 4) - self.point, (3.1, -3.3, 0))

    def test_iadd(self):
        self.point += 1, 3, 1
        self.assert_points_are_close(self.point, (3.1, 2.7, 5))

    def test_isub(self):
        self.point -= 0.1, -4, -4.12
        self.assert_points_are_close(self.point, (2, 3.7, 8.12))


class TestMesh:

    def setup(self):
        self.mesh = Mesh(shapes.cube(1), (1, 2, 3), color=(0.1, 1, 0))

    def test_attrs(self):
        # Check that attributes can be accessed:
        self.mesh.triangles
        self.mesh.triangles = 3    # You shouldn't do this, but you can.

        assert self.mesh.color == RGBA(0.1, 1, 0)

        # with raises(AttributeError):
        #     self.mesh.foo
        # with raises(AttributeError):
        #     self.mesh.bar = 3

    # def test_load(self):
    #     m = Mesh(((), ()), (0,0,0))
    #     m.load('data/test/cube.txt')

    # def test_save(self):
    #     self.mesh.save('data/test/mesh_1.txt')


class TestRGBA:

    def setup(self):
        self.color = RGBA(0.5, 0.0)

    def test_slots(self):
        with raises(AttributeError):
            self.color.foo = 1


class TestTriangleArray:

    def setup(self):
        _, triangles = shapes.circle(1, 5)
        self.array = TriangleArray(triangles)

    def test_len(self):
        assert len(self.array) == 3

    def test_setitem(self):
        self.array[2] = (3, 1, 3)

    def test_append(self):
        self.array.append((1, 3, 4))
        with raises(ValueError):
            self.array.append((3, 2))
        with raises(ValueError):
            self.array.append((3, 2, 2, 1))

    # def test_add(self):
    #     assert self.array + 3 


def test_lines():
    _, triangles = shapes.circle(1, 4)
    assert lines(triangles) == {frozenset(pair) for pair in
        [{0, 1}, {1, 2}, {2, 3}, {3, 0}, {0, 2}]}


if __name__ == '__main__':
    main()
    # m = Mesh.from_path('data/test/cube.txt')
    # print(repr(m))
