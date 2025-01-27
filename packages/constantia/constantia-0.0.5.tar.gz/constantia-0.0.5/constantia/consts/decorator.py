import ast
import inspect
from functools import wraps
from typing import Callable, Literal

from constantia.consts.const_assignment_visitor import ConstAssignmentVisitor
from constantia.consts.typing import OnType


def consts(var_names: OnType = 'uppercase', check_at: Literal["runtime", "import"] = "import"):
    # Handling the no-parameter call
    if callable(var_names):
        obj = var_names
        var_names = 'uppercase'
        check_at: Literal["runtime", "import"] = "import"
        return consts(var_names=var_names, check_at=check_at)(obj)

    def decorator(obj):
        cls = __class_from_obj(obj)

        @wraps(obj)
        def wrapper(*args, **kwargs):
            if check_at == "runtime":
                __assert_constants(func=obj, var_names=var_names, cls=cls)
            return obj(*args, **kwargs)

        if check_at == "import":
            __assert_constants(func=obj, var_names=var_names, cls=cls)

        return wrapper

    return decorator


def __class_from_obj(obj):
    if inspect.isclass(obj):
        return obj
    return None


def __assert_constants(cls: type | None, func: Callable, var_names: OnType = None):
    source_code = inspect.getsource(func)
    tree = ast.parse(source_code)

    visitor = ConstAssignmentVisitor(klass=cls, var_names=var_names, source_code=source_code)
    visitor.visit(tree)
