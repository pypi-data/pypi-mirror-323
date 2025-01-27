from constantia import consts


@consts('uppercase', check_at='import')
def func():
    MY_CONSTANT = [1, 2, 3]
    MY_CONSTANT = 20
