import re

def is_valid_android_app_id(app_id):
    return bool(re.match(r"^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)+$", app_id))

def is_valid_ios_app_id(app_id):
    return app_id.isdigit() or app_id.startswith("id")
