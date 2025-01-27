import unittest
from onelink.utils import is_valid_android_app_id, is_valid_ios_app_id

class TestUtils(unittest.TestCase):
    def test_valid_android_app_id(self):
        self.assertTrue(is_valid_android_app_id("com.aistyleapp"))
        self.assertFalse(is_valid_android_app_id("43634677"))

    def test_valid_ios_app_id(self):
        self.assertTrue(is_valid_ios_app_id("id6738657557"))
        self.assertFalse(is_valid_ios_app_id("not_a_number"))
