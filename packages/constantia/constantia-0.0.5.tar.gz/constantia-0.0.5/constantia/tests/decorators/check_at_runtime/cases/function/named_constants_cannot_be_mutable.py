from constantia import consts


@consts(['x', 'y', 'z'], check_at='runtime')
def func():
    x = [1, 2, 3]
    y = 20
