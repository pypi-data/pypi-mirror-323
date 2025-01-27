from constantia import consts


@consts(['x', 'y', 'z'], check_at='import')
def func():  # pragma: no cover
    x = [1, 2, 3]
    y = 20
