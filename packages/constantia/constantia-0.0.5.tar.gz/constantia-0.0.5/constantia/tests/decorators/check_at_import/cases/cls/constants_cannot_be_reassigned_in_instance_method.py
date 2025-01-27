from constantia import consts


@consts(['X'], check_at='import')
class Example:  # pragma: no cover
    X = 9999

    def change_x(self):
        self.__class__.X = 'new value'


