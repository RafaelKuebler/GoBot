class Vec2(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self._map_add = {float: self.add_num, int: self.add_num, Vec2: self.add_point, tuple: self.add_tuple}
        self._map_sub = {float: self.sub_num, int: self.sub_num, Vec2: self.sub_point, tuple: self.sub_tuple}
        self._map_eq = {Vec2: self.eq_point, tuple: self.eq_tuple}
        self._map_mul = {float: self.scale, int: self.scale, Vec2: self.dot, tuple: self.dot_tuple}
        self._map_div = {float: self.div_num, int: self.div_num, Vec2: self.div_point, tuple: self.div_tuple}

    def __add__(self, point):
        return self._map_add[type(point)](point)

    def add_num(self, num):
        return Vec2(self.x + num, self.y + num)

    def add_point(self, point):
        return Vec2(self.x + point.x, self.y + point.y)

    def add_tuple(self, tup):
        x, y = tup
        return Vec2(self.x + x, self.y + y)

    def __sub__(self, point):
        return self._map_sub[type(point)](point)

    def sub_num(self, num):
        return Vec2(self.x - num, self.y - num)

    def sub_point(self, point):
        return Vec2(self.x - point.x, self.y - point.y)

    def sub_tuple(self, tup):
        x, y = tup
        return Vec2(self.x - x, self.y - y)

    def __eq__(self, point):
        return self._map_eq[type(point)](point)

    def eq_point(self, point):
        return self.x == point.x and self.y == point.y

    def eq_tuple(self, tup):
        x, y = tup
        return self.x == x and self.y == y

    def __ne__(self, point):
        return self.x != point.x or self.y != point.y

    def __mul__(self, obj):
        return self._map_mul[type(obj)](obj)

    def scale(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)

    def dot(self, point):
        return Vec2(self.x * point.x, self.y * point.y)

    def dot_tuple(self, tup):
        x, y = tup
        return Vec2(self.x * x, self.y * y)

    def __truediv__(self, point):
        return self._map_div[type(point)](point)

    def div_point(self, point):
        return Vec2(self.x / point.x, self.y / point.y)

    def div_num(self, num):
        return Vec2(self.x / num, self.y / num)

    def div_tuple(self, tup):
        x, y = tup
        return Vec2(self.x / x, self.y / y)

    def __iter__(self):
        return iter((self.x, self.y))

    def __str__(self):
        return "({}, {})".format(self.x, self.y)
