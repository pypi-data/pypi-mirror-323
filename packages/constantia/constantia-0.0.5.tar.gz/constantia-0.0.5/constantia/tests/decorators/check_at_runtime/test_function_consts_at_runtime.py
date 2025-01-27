import unittest


class TestFunctionConstsAtRuntime(unittest.TestCase):
    def test_named_function_constants_cannot_be_mutable(self):
        from constantia.tests.decorators.check_at_runtime.cases.function.named_constants_cannot_be_mutable import func

        with self.assertRaises(TypeError) as context:
            func()

        self.assertEqual('Assignment of non-immutable type to constant "x" detected on line 3 (x = [1, 2, 3]).',
                         str(context.exception))

    def test_uppercase_function_constants_cannot_be_mutable(self):
        from constantia.tests.decorators.check_at_runtime.cases.function.uppercase_constants_cannot_be_mutable import func

        with self.assertRaises(TypeError) as context:
            func()

        self.assertEqual('Assignment of non-immutable type to constant "MY_CONSTANT" '
                         'detected on line 3 (MY_CONSTANT = [1, 2, 3]).',
                         str(context.exception))

    def test_function_constants_cannot_be_reassigned(self):
        from constantia.tests.decorators.check_at_runtime.cases.function.constants_cannot_be_reassigned import func

        with self.assertRaises(ValueError) as context:
            func()

        self.assertEqual('Reassignment of constant "x" detected on line 4 (x = 20).', str(context.exception))

    def test_function_constants_valid_assignment(self):
        from constantia.tests.decorators.check_at_runtime.cases.function.valid_constant_assignment import func

        self.assertEqual((1, 2, 3), func())
