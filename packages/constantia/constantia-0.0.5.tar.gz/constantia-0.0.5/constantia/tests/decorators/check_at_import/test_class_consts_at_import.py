import unittest


class TestClassConstsAtImport(unittest.TestCase):
    def test_class_constants_cannot_be_reassigned_in_class_method(self):
        with self.assertRaises(ValueError) as context:
            from constantia.tests.decorators.check_at_import.cases.cls.constants_cannot_be_reassigned_in_class_method import Example  # noqa

        self.assertEqual(
            'Reassignment of class constant "X" detected on line 7 (cls.X = 8888).',
            str(context.exception)
        )

    def test_class_constants_cannot_be_reassigned_in_instance_method(self):
        with self.assertRaises(ValueError) as context:
            from constantia.tests.decorators.check_at_import.cases.cls.constants_cannot_be_reassigned_in_instance_method import Example  # noqa

        self.assertEqual(
            "Reassignment of class constant \"X\" detected on line 6 (self.__class__.X = 'new value').",
            str(context.exception)
        )

    def test_class_constants_cannot_be_reassigned_in_static_method(self):
        with self.assertRaises(ValueError) as context:
            from constantia.tests.decorators.check_at_import.cases.cls.constants_cannot_be_reassigned_in_static_method import Example  # noqa

        self.assertEqual(
            'Static reassignment of class constant "X" detected on line 7 (Example.X = 8888).',
            str(context.exception)
        )

    def test_function_constants_valid_constant_assignment(self):
        from constantia.tests.decorators.check_at_import.cases.function.valid_constant_assignment import func

        self.assertEqual((1, 2, 3), func())

    def test_class_constants_cannot_be_reassigned(self):
        with self.assertRaises(ValueError) as context:
            from constantia.tests.decorators.check_at_import.cases.cls.constants_cannot_be_reassigned import Example  # noqa

        self.assertEqual('Reassignment of constant "X" detected on line 4 (X = 9999).', str(context.exception))

    def test_named_class_constants_cannot_be_reassigned(self):
        with self.assertRaises(ValueError) as context:
            from constantia.tests.decorators.check_at_import.cases.cls.named_constants_cannot_be_reassigned import Example  # noqa

        self.assertEqual('Reassignment of constant "X" detected on line 4 (X = 9999).', str(context.exception))

    def test_uppercase_class_constants_cannot_be_reassigned(self):
        with self.assertRaises(ValueError) as context:
            from constantia.tests.decorators.check_at_import.cases.cls.uppercase_constants_cannot_be_reassigned import Example  # noqa

        self.assertEqual('Reassignment of constant "X" detected on line 4 (X = 9999).', str(context.exception))

    def test_class_constants_valid_assignment(self):
        from constantia.tests.decorators.check_at_import.cases.cls.valid_constant_assignment import Example

        Example()
