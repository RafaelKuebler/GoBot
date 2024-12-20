from gobot.go.vec2 import Vec2


class TestVec2:
    def test_point(self):
        point = Vec2(1, 2)
        assert point.x == 1
        assert point.y == 2

    def test_equal(self):
        assert Vec2(1, 2) == Vec2(1, 2)

    def test_equal_tuple(self):
        assert Vec2(1, 2) == (1, 2)

    def test_not_equal(self):
        assert Vec2(2, 3) != Vec2(3, 6)

    def test_not_equal_swapped(self):
        assert Vec2(1, 3) != Vec2(3, 1)

    def test_add(self):
        point1 = Vec2(2, 3)
        point2 = Vec2(4, 5)
        point_sum = point1 + point2
        assert point_sum.x == 2 + 4
        assert point_sum.y == 3 + 5

    def test_add_int(self):
        point = Vec2(2, 3)
        point_sum = point + 4
        assert point_sum.x == 2 + 4
        assert point_sum.y == 3 + 4

    def test_add_float(self):
        point = Vec2(2, 3)
        point_sum = point + 4.5
        assert point_sum.x == 2 + 4.5
        assert point_sum.y == 3 + 4.5

    def test_add_tup(self):
        point = Vec2(2, 3)
        point_sum = point + (4, 5)
        assert point_sum.x == 2 + 4
        assert point_sum.y == 3 + 5

    def test_sub(self):
        point1 = Vec2(2, 3)
        point2 = Vec2(4, 5)
        point_sub = point1 - point2
        assert point_sub.x == 2 - 4
        assert point_sub.y == 3 - 5

    def test_sub_int(self):
        point = Vec2(2, 3)
        point_sub = point - 3
        assert point_sub.x == 2 - 3
        assert point_sub.y == 3 - 3

    def test_sub_float(self):
        point = Vec2(2, 3)
        point_sub = point - 3.5
        assert point_sub.x == 2 - 3.5
        assert point_sub.y == 3 - 3.5

    def test_sub_tup(self):
        point = Vec2(2, 3)
        point_sub = point - (4, 5)
        assert point_sub.x == 2 - 4
        assert point_sub.y == 3 - 5

    def test_mult_scalar(self):
        point = Vec2(2, 3)
        point_scaled = point * 3
        assert point_scaled.x == 2 * 3
        assert point_scaled.y == 3 * 3

    def test_mult_scalar_float(self):
        point = Vec2(2, 3)
        point_scaled = point * 4.5
        assert point_scaled.x == 2 * 4.5
        assert point_scaled.y == 3 * 4.5

    def test_mult_dot(self):
        point1 = Vec2(2, 3)
        point2 = Vec2(3, 4)
        point_dot = point1 * point2
        assert point_dot.x == 2 * 3
        assert point_dot.y == 3 * 4

    def test_mult_tuple(self):
        point = Vec2(2, 3)
        point_dot = point * (3, 4)
        assert point_dot.x == 2 * 3
        assert point_dot.y == 3 * 4

    def test_div(self):
        point1 = Vec2(2, 3)
        point2 = Vec2(3, 4)
        point_div = point1 / point2
        assert point_div.x == 2 / 3
        assert point_div.y == 3 / 4

    def test_div_int(self):
        point = Vec2(2, 3)
        point_div = point / 3
        assert point_div.x == 2 / 3
        assert point_div.y == 3 / 3

    def test_div_float(self):
        point = Vec2(2, 3)
        point_div = point / 3.5
        assert point_div.x == 2 / 3.5
        assert point_div.y == 3 / 3.5

    def test_div_tuple(self):
        point = Vec2(2, 3)
        point_div = point / (3, 4)
        assert point_div.x == 2 / 3
        assert point_div.y == 3 / 4

    def test_unpack(self):
        point = Vec2(3, 4)
        assert (3, 4) == tuple(point)
