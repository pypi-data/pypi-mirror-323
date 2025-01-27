import unittest


class TestFunctionConstsAtImport(unittest.TestCase):
    def test_function_constants_cannot_be_mutable(self):
        with self.assertRaises(TypeError) as context:
            from constantia.tests.decorators.check_at_import.cases.function.constants_cannot_be_mutable import func  # noqa

        self.assertEqual('Assignment of non-immutable type to constant "x" detected on line 3 (x = [1, 2, 3]).', str(context.exception))

    def test_no_parameter_call(self):
        with self.assertRaises(TypeError) as context:
            from constantia.tests.decorators.check_at_import.cases.function.no_parameter_call import func  # noqa

        self.assertEqual('Assignment of non-immutable type to constant "MY_CONSTANT" '
                         'detected on line 3 (MY_CONSTANT = [1, 2, 3]).',
                         str(context.exception))

    def test_uppercase_function_constants_cannot_be_mutable(self):
        with self.assertRaises(TypeError) as context:
            from constantia.tests.decorators.check_at_import.cases.function.uppercase_constants_cannot_be_mutable import func  # noqa

        self.assertEqual('Assignment of non-immutable type to constant "MY_CONSTANT" '
                         'detected on line 3 (MY_CONSTANT = [1, 2, 3]).',
                         str(context.exception))

    def test_function_constants_cannot_be_reassigned(self):
        with self.assertRaises(ValueError) as context:
            from constantia.tests.decorators.check_at_import.cases.function.constants_cannot_be_reassigned import func  # noqa

        self.assertEqual('Reassignment of constant "x" detected on line 4 (x = 20).', str(context.exception))
