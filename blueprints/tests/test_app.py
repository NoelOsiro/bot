import unittest
from flask import Flask
from app import app


class AppTestCase(unittest.TestCase):
    """
    Test case for the app module.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        self.app = app.test_client()
        self.app.testing = True

    def test_hello_route(self):
        """
        Test the hello route.
        """
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello, World!')



if __name__ == '__main__':
    unittest.main()
