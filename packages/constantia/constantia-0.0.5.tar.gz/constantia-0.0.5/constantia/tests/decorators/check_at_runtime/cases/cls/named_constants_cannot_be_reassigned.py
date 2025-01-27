from constantia import consts


@consts(['X'], check_at='runtime')
class Example:
    X = 9999
    X = 8888

