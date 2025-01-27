from constantia import consts


@consts(['X'], check_at='runtime')
class Example:
    X = 9999

    def change_x(self):
        self.__class__.X = 8888


