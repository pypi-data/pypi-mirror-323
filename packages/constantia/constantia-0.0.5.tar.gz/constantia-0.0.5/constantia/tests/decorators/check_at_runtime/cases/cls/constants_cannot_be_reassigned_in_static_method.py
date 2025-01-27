from constantia import consts


@consts(['X'], check_at='runtime')
class Example:
    X = 9999

    @staticmethod
    def change_x():
        Example.X = 8888


