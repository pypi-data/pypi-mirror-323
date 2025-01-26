import unittest
from scp_api_client.api_client import ScpApiClient

class TestSCPClient(unittest.TestCase):

    def setUp(self):
        self.client = ScpApiClient('test_key')

    def test_init(self):
        self.assertEqual(self.client.api_key, 'test_key')

if __name__ == '__main__':
    unittest.main()
