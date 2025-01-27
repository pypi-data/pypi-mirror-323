from constantia import consts


@consts(['x', 'y', 'z'], check_at='import')
def func():  # pragma: no cover
    x = 3
    x = 20
    y = 20
