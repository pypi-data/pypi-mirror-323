import os
from unittest import TestCase

from inject_environment_variables import EnvironmentVariableInjector
from inject_environment_variables.decorator import inject_environment_variables


class TestInjector(TestCase):
    def test_with_statement(self):
        starting_variables = os.environ
        length = len(starting_variables)

        with EnvironmentVariableInjector({
            'NEW_VARIABLE': 'testing',
            'TEST_VARIABLE': 'testing_variables',
        }):
            altered_variables = os.environ
            altered_length = len(altered_variables)

            # Assert variables have been injected
            self.assertEqual(
                os.getenv('NEW_VARIABLE'),
                'testing'
            )
            self.assertEqual(
                os.getenv('TEST_VARIABLE'),
                'testing_variables'
            )
            self.assertEqual(length + 2, altered_length)

        # Assert original variables have been restored
        self.assertEqual(
            len(os.environ),
            length
        )
        self.assertEqual(
            os.environ,
            starting_variables
        )
        self.assertIsNone(os.getenv('NEW_VARIABLE'))
        self.assertIsNone(os.getenv('TEST_VARIABLE'))

    def test_decorated_function(self):
        @inject_environment_variables({
            'INJECTED_VARIABLE': 'foo',
            'ANOTHER_TEST': 'bar'
        })
        def function_with_decorator():
            # Test vars from decorator are present
            altered_variables = os.environ
            altered_length = len(altered_variables)
            self.assertEqual(
                os.getenv('INJECTED_VARIABLE'),
                'foo'
            )
            self.assertEqual(
                os.getenv('ANOTHER_TEST'),
                'bar'
            )
            self.assertEqual(length + 2, altered_length)

        # Take initial variables
        starting_variables = os.environ
        length = len(starting_variables)
        # Run decorated function
        function_with_decorator()
        # Test state after function
        self.assertEqual(
            len(os.environ),
            length
        )
        self.assertEqual(
            os.environ,
            starting_variables
        )
        self.assertIsNone(os.getenv('NEW_VARIABLE'))
        self.assertIsNone(os.getenv('TEST_VARIABLE'))
