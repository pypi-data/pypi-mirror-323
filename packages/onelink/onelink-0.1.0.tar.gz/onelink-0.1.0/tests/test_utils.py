import unittest
from onelink.utils import is_valid_android_app_id, is_valid_ios_app_id

class TestUtils(unittest.TestCase):
    def test_valid_android_app_id(self):
        self.assertTrue(is_valid_android_app_id("com.example.app"))
        self.assertFalse(is_valid_android_app_id("invalid-app-id"))

    def test_valid_ios_app_id(self):
        self.assertTrue(is_valid_ios_app_id("123456789"))
        self.assertFalse(is_valid_ios_app_id("not_a_number"))
