from constantia import consts


@consts(['x', 'y', 'z'], check_at='runtime')
def func():
    x = 3
    x = 20
    y = 20
