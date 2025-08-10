
import os
import time
from automation.utils.driver_setup import get_driver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automation.tests.test_login import login
from pathlib import Path

WAIT_TIME = 30
THIS_FILE = Path(__file__).resolve()
AUTOMATION_DIR = THIS_FILE.parent.parent          # .../automation
SCREEN_DIR = AUTOMATION_DIR / "screenshots"       # .../automation/screenshots
os.makedirs(SCREEN_DIR, exist_ok=True)

# Ensure folder exists
os.makedirs(SCREEN_DIR, exist_ok=True)

driver = get_driver()
driver.implicitly_wait(10)
wait = WebDriverWait(driver, WAIT_TIME)

try:
    # Login
    login(
        driver,
        username="azmin@excelbd.com",
        password="D!m77(2SJ,5j"
    )


    # Navigate and filter
    wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("My Attendance")'))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.TextView").instance(1)'))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Previous month"))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Previous month"))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "20 June 2025"))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ID, "android:id/button1"))).click()

    wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.TextView").instance(4)'))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Previous month"))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Previous month"))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "30 June 2025"))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ID, "android:id/button1"))).click()

    wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("All")'))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("On Leave")'))).click()
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "1., Shaid Azmin, On Leave, 26-Jun-2025, --, --, HQ, Baridhara")))

    # Screenshot with date range in name
    screenshot_path = SCREEN_DIR / "attendance-filter.png"
    driver.save_screenshot(str(screenshot_path))
    print(f"Screenshot saved successfully at: {screenshot_path}")


finally:
    driver.quit()


