import os
from time import sleep
from automation.utils.driver_setup import get_driver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def login(driver, username=None, password=None, wait_time=30, post_login_locator=None):

    username = username or os.getenv("APP_USERNAME")
    password = password or os.getenv("APP_PASSWORD")
    if not username or not password:
        raise ValueError("Username/password not provided or missing from environment variables.")

    wait = WebDriverWait(driver, wait_time)

    # Username
    try:
        username_field = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.EditText[@text="Enter Email"]'))
        )
        username_field.clear()
        username_field.send_keys(username)
    except TimeoutException:
        raise TimeoutException("Username field not found or clickable.")

    # Password
    try:
        password_field = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.EditText[@text="Enter Password"]'))
        )
        password_field.clear()
        password_field.send_keys(password)
    except TimeoutException:
        raise TimeoutException("Password field not found or clickable.")

    # Login button
    try:
        login_button = wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.TextView[@text="Login"]'))
        )
        login_button.click()
    except TimeoutException:
        raise TimeoutException("Login button not found or clickable.")

    # Optional post-login check
    if post_login_locator:
        wait.until(EC.visibility_of_element_located(post_login_locator))

    # Small buffer delay to ensure page load
    sleep(2)


if __name__ == "__main__":
    driver = get_driver()
    try:
        login(
            driver,
            username="azmin@excelbd.com",
            password="D!m77(2SJ,5j",
            # post_login_locator=(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Dashboard")')
        )
        print("Login successful!")
    finally:
        driver.quit()
