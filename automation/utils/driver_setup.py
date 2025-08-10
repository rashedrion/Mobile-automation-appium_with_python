import os
from appium import webdriver
from appium.options.android import UiAutomator2Options
def get_driver():
    apk_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/mobile-app.apk"))
    if not os.path.exists(apk_path):
        raise FileNotFoundError(f"APK not found at {apk_path}")

    # capabilities dict
    desired_caps = {
        "platformName": "Android",
        "deviceName": "Android Emulator",
        "app": apk_path,
        "automationName": "UiAutomator2",
        "autoGrantPermissions": True,
    }

    # options object caps load
    options = UiAutomator2Options().load_capabilities(desired_caps)

    # Appium server connect
    driver = webdriver.Remote("http://localhost:4723", options=options)
    return driver
