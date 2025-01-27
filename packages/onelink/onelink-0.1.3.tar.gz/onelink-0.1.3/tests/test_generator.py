import unittest
from onelink.generator import AppLinkGenerator

class TestAppLinkGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = AppLinkGenerator(base_url="https://customdomain.com")

    def test_android_link_generation(self):
        self.generator.set_android_app_id("com.example.app")
        self.generator.set_custom_param("utm_source", "email", platform="android")
        link = self.generator.generate_android_link()
        self.assertIn("com.example.app", link)
        self.assertIn("utm_source=email", link)

    def test_ios_link_generation(self):
        self.generator.set_ios_app_id("123456789")
        self.generator.set_custom_param("utm_campaign", "holiday", platform="ios")
        link = self.generator.generate_ios_link()
        self.assertIn("123456789", link)
        self.assertIn("utm_campaign=holiday", link)

    def test_invalid_base_url(self):
        with self.assertRaises(ValueError):
            AppLinkGenerator(base_url="http://customdomain.com")

    def test_missing_app_id(self):
        with self.assertRaises(ValueError):
            self.generator.generate_android_link()
