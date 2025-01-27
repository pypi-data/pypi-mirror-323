from constantia import consts


@consts(['X'], check_at='import')
class Example:  # pragma: no cover
    X = 9999
    X = 9999

