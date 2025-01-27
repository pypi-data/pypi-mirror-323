import unittest


class TestClassConstsAtRuntime(unittest.TestCase):
    def test_named_class_constants_cannot_be_reassigned(self):
        from constantia.tests.decorators.check_at_runtime.cases.cls.named_constants_cannot_be_reassigned import Example

        with self.assertRaises(ValueError) as context:
            Example()

        self.assertEqual('Reassignment of constant "X" detected on line 4 (X = 8888).', str(context.exception))

    def test_uppercase_class_constants_cannot_be_reassigned(self):
        from constantia.tests.decorators.check_at_runtime.cases.cls.uppercase_constants_cannot_be_reassigned import Example

        with self.assertRaises(ValueError) as context:
            Example()

        self.assertEqual('Reassignment of constant "X" detected on line 4 (X = 8888).', str(context.exception))

    def test_class_constants_cannot_be_reassigned_in_class_method(self):
        from constantia.tests.decorators.check_at_runtime.cases.cls.constants_cannot_be_reassigned_in_class_method import Example

        with self.assertRaises(ValueError) as context:
            e = Example()
            e.change_x()

        self.assertEqual('Reassignment of class constant "X" detected on line 7 (cls.X = 8888).', str(context.exception))

    def test_class_constants_cannot_be_reassigned_in_instance_method(self):
        from constantia.tests.decorators.check_at_runtime.cases.cls.constants_cannot_be_reassigned_in_instance_method import Example

        with self.assertRaises(ValueError) as context:
            e = Example()
            e.change_x()

        self.assertEqual(
            'Reassignment of class constant "X" detected on line 6 (self.__class__.X = 8888).',
            str(context.exception)
        )

    def test_class_constants_cannot_be_reassigned_in_static_method(self):
        from constantia.tests.decorators.check_at_runtime.cases.cls.constants_cannot_be_reassigned_in_static_method import Example

        with self.assertRaises(ValueError) as context:
            Example()

        self.assertEqual(
            'Static reassignment of class constant "X" detected on line 7 (Example.X = 8888).',
            str(context.exception)
        )

    def test_class_constants_valid_assignment(self):
        from constantia.tests.decorators.check_at_runtime.cases.cls.valid_constant_assignment import Example

        Example()
