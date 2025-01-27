import ast

from constantia.consts.typing import OnType


class ConstAssignmentVisitor(ast.NodeVisitor):
    IMMUTABLE_TYPES = (ast.Constant, ast.Tuple)

    def __init__(self, source_code: str, var_names: OnType = None, klass: type | None = None):
        self.source_code_lines = source_code.splitlines()
        self.var_is_watched = self.__build_var_watch_predicate(var_names=var_names)
        self.cls = klass
        self.constants: set[str] = set()

    def visit(self, node):
        # Assign parent references to all child nodes
        for child in ast.iter_child_nodes(node):
            child.parent = node
        super().visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if not self.var_is_watched(target.id):
                    continue
                # Second assignment
                if target.id in self.constants:
                    code_line = self.__code_line(node)
                    raise ValueError(
                        f'Reassignment of constant "{target.id}" detected on line {node.lineno} ({code_line}).'
                    )
                # Do not allow immutable type assignment
                if not isinstance(node.value, self.IMMUTABLE_TYPES):
                    code_line = self.__code_line(node)
                    raise TypeError(
                        f'Assignment of non-immutable type to constant "{target.id}" detected on line {node.lineno} ({code_line}).'
                    )
                # First assignment of a watched variable
                self.constants.add(target.id)

            # Assignment through class name
            if (
                    isinstance(target, ast.Attribute)
                    and target.attr in self.constants
                    and isinstance(target.value, ast.Name)
                    and target.value.id == self.cls.__name__
            ):
                code_line = self.__code_line(node)
                raise ValueError(
                    f'Static reassignment of class constant "{target.attr}" detected on line {node.lineno} ({code_line}).'
                )

            if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Attribute)
                    and isinstance(target.value.value, ast.Name)
                    and target.value.value.id == "self"
                    and target.value.attr == "__class__"
                    and target.attr in self.constants
            ):
                code_line = self.__code_line(node)
                raise ValueError(
                    f'Reassignment of class constant "{target.attr}" detected on line {node.lineno} ({code_line}).'
                )

        self.generic_visit(node)

    def _is_self_class_const(self, node):
        """
        Check if the node represents `self.__class__.CONST`.
        """
        return (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Attribute)
                and isinstance(node.value.value, ast.Name)
                and node.value.value.id == "self"
                and node.value.attr == "__class__"
                and node.attr in self.constants
        )

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id in {'self', 'cls'}:
            if node.attr in self.constants:
                parent = getattr(node, "parent", None)
                if isinstance(parent, ast.Assign):
                    code_line = self.__code_line(node)
                    raise ValueError(
                        f'Reassignment of class constant "{node.attr}" detected on line {node.lineno} ({code_line}).'
                    )

        self.generic_visit(node)

    @staticmethod
    def __build_var_watch_predicate(var_names: OnType):
        if var_names is None:
            return lambda _var: False
        elif isinstance(var_names, list):
            return lambda var: var in var_names
        elif var_names == 'uppercase':
            return lambda var: var.isupper()
        elif callable(var_names):
            return var_names
        else:
            ValueError('Invalid value on on argument. Accepted values are None, a list of strings or a predicate')

    def __code_line(self, node) -> str:
        line = self.source_code_lines[node.lineno - 1]
        return line.strip()
