import unittest
from server.driver import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_hello(self):
        result = self.app.get('/api/hello')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json, {"message": "Hello, Python function was called!"})

if __name__ == '__main__':
    unittest.main()