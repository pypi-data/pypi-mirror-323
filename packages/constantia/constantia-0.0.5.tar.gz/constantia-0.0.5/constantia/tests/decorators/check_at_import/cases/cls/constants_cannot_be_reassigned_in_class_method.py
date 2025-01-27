from constantia import consts


@consts(['X'], check_at='import')
class Example:  # pragma: no cover
    X = 9999

    @classmethod
    def change_x(cls):
        cls.X = 8888


