from constantia import consts


@consts(['X'], check_at='runtime')
class Example:
    X = 9999

    @classmethod
    def change_x(cls):
        cls.X = 8888


