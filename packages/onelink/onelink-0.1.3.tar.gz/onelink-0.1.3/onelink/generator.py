from urllib.parse import urlencode
from onelink.utils import is_valid_android_app_id, is_valid_ios_app_id

class AppLinkGenerator:
    def __init__(self, base_url="https://yourdomain.com"):
        if not base_url.startswith("https://"):
            raise ValueError("Base URL must start with 'https://'.")
        self.base_url = base_url.rstrip("/")
        self.android_params = {}
        self.ios_params = {}

    def set_android_app_id(self, app_id):
        if not is_valid_android_app_id(app_id):
            raise ValueError("Android App ID must be alphanumeric.")
        self.android_params["app_id"] = app_id

    def set_ios_app_id(self, app_id):
        if not is_valid_ios_app_id(app_id):
            raise ValueError("iOS App ID must be numeric.")
        self.ios_params["app_id"] = app_id

    def set_android_fallback_url(self, url):
        if not url.startswith("https://"):
            raise ValueError("Fallback URL must start with 'https://'.")
        self.android_params["fallback_url"] = url

    def set_ios_fallback_url(self, url):
        if not url.startswith("https://"):
            raise ValueError("Fallback URL must start with 'https://'.")
        self.ios_params["fallback_url"] = url

    def set_custom_param(self, key, value, platform=None):
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("Custom parameters must be strings.")
        if platform == "android":
            self.android_params[key] = value
        elif platform == "ios":
            self.ios_params[key] = value
        else:
            raise ValueError("Platform must be either 'android' or 'ios'.")

    def generate_android_link(self):
        if "app_id" not in self.android_params:
            raise ValueError("Android App ID is required.")
        query_string = urlencode(self.android_params)
        return f"{self.base_url}/android?{query_string}"

    def generate_ios_link(self):
        if "app_id" not in self.ios_params:
            raise ValueError("iOS App ID is required.")
        query_string = urlencode(self.ios_params)
        return f"{self.base_url}/ios?{query_string}"
