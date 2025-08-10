import os
from pathlib import Path
from datetime import datetime

from selenium.common.exceptions import TimeoutException
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from automation.utils.driver_setup import get_driver
from automation.tests.test_login import login  # use your existing reusable login()

# ========= Config =========
WAIT_TIME   = int(os.getenv("APP_WAIT_TIME", "30"))
LEAVE_TYPE  = os.getenv("APP_LEAVE_TYPE", "Leave Without Pay")
FROM_DATE   = os.getenv("APP_FROM_DATE", "2025-08-10")  # YYYY-MM-DD
TO_DATE     = os.getenv("APP_TO_DATE",   "2025-08-15")
LEAVE_REASON= os.getenv("APP_LEAVE_REASON", "Medical appointment")

THIS_FILE   = Path(__file__).resolve()
AUTOMATION_DIR = THIS_FILE.parent.parent
SCREEN_DIR  = AUTOMATION_DIR / "screenshots"
SCREEN_DIR.mkdir(parents=True, exist_ok=True)

# ========= tiny helpers =========
def tap(wait, loc, timeout=WAIT_TIME):
    WebDriverWait(wait._driver, timeout).until(EC.element_to_be_clickable(loc)).click()

def type_into(wait, loc, text, timeout=WAIT_TIME):
    el = WebDriverWait(wait._driver, timeout).until(EC.element_to_be_clickable(loc))
    el.clear(); el.send_keys(text)

MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

def ensure_month_year(driver, target_dt: datetime, steps=18):
    tgt_m = MONTHS[target_dt.month-1]; tgt_y = target_dt.year
    def header():
        for by, val in [
            (AppiumBy.ID, "com.google.android.material:id/month_navigation_fragment_toggle"),
            (AppiumBy.ID, "android:id/date_picker_header_date"),
            (AppiumBy.ID, "android:id/date_picker_header_year"),
        ]:
            try: return driver.find_element(by, val).text
            except Exception: pass
        return ""
    for _ in range(steps):
        h = header()
        if (tgt_m[:3] in h or tgt_m in h) and str(tgt_y) in h:
            return True
        # try prev first; then next
        moved = False
        try: driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Previous month").click(); moved = True
        except Exception: pass
        if not moved:
            try: driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Next month").click(); moved = True
            except Exception: pass
        if not moved:
            break
    h = header()
    return (tgt_m[:3] in h or tgt_m in h) and str(tgt_y) in h

def pick_date(driver, wait, open_locator, dt: datetime):
    # open picker (supports both id/spinner and your calendar glyphs)
    tap(wait, open_locator)
    ensure_month_year(driver, dt)  # best-effort align month/year

    day  = dt.day
    month= MONTHS[dt.month-1]
    year = dt.year

    # try accessibility label first (handles zero-padded day too)
    for desc in (f"{day:02d} {month} {year}", f"{day} {month} {year}"):
        try:
            tap(wait, (AppiumBy.ACCESSIBILITY_ID, desc), timeout=6)
            break
        except TimeoutException:
            continue
    else:
        # fallback by visible day number
        tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{day}")'), timeout=6)

    # OK / confirm
    try:
        tap(wait, (AppiumBy.ID, "android:id/button1"), timeout=4)
    except TimeoutException:
        tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("OK")'), timeout=4)


if __name__ == "__main__":
    # ===== 1) Launch the app =====
    driver = get_driver()
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, WAIT_TIME)

    try:
        # login once
        login(driver,
              username=os.getenv("APP_USERNAME", "azmin@excelbd.com"),
              password=os.getenv("APP_PASSWORD", "D!m77(2SJ,5j"))

        # ===== 2) Navigate to HR -> Check-IN =====
        try:
            tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Check-IN")'))
        except TimeoutException:
            tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("HR")'))
            tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Check-IN")'))

        # ===== 3) Complete the check-in process =====
        # Use your known id; keep a generic fallback if the id differs on some builds.
        try:
            tap(wait, (AppiumBy.ID, "check_in_button"))
        except TimeoutException:
            # try a generic text-based button
            tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Check")'))

        # (optional) small wait to allow toast/banner
        WebDriverWait(driver, 5).until(lambda d: True)

        # ===== 4) Navigate to HR -> Leave Application =====
        try:
            tap(wait, (AppiumBy.ACCESSIBILITY_ID, "Leave Application"))
        except TimeoutException:
            tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("HR")'))
            tap(wait, (AppiumBy.ACCESSIBILITY_ID, "Leave Application"))

        # ===== 5) Create a new leave application =====
        # "+" add application (support both recorder variants)
        try:
            tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("")'), timeout=6)
        except TimeoutException:
            try:
                tap(wait, (AppiumBy.ACCESSIBILITY_ID, "+, Application"), timeout=6)
            except TimeoutException:
                # generic FAB fallback
                tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Add")'))

        # open leave type (caret glyph or spinner)
        try:
            tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("")'), timeout=5)
        except TimeoutException:
            # recorder fallback container
            try:
                tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR,
                           'new UiSelector().className("android.view.ViewGroup").instance(14)'), timeout=5)
            except TimeoutException:
                # if your app exposes an id, prefer it:
                # tap(wait, (AppiumBy.ID, "leave_type_spinner"))
                pass

        # choose leave type
        tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{LEAVE_TYPE}")'))

        # dates
        f_dt = datetime.fromisoformat(FROM_DATE)
        t_dt = datetime.fromisoformat(TO_DATE)
        assert t_dt >= f_dt, "TO_DATE must be on/after FROM_DATE."

        # From date icon (first calendar glyph)
        pick_date(driver, wait,
                  (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("").instance(0)'),
                  f_dt)

        # To date icon (second calendar glyph)
        pick_date(driver, wait,
                  (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("")'),
                  t_dt)

        # reason (EditText.instance(2) from recorder; keep class fallback)
        try:
            type_into(wait,
                      (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText").instance(2)'),
                      LEAVE_REASON)
        except TimeoutException:
            type_into(wait, (AppiumBy.CLASS_NAME, "android.widget.EditText"), LEAVE_REASON)

        # Apply
        try:
            tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Apply")'))
        except TimeoutException:
            tap(wait, (AppiumBy.ACCESSIBILITY_ID, "Apply"))

        # Confirm OK
        try:
            tap(wait, (AppiumBy.ACCESSIBILITY_ID, "OK"), timeout=8)
        except TimeoutException:
            tap(wait, (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("OK")'))

        # ===== 6) Validate + Screenshot =====
        # Best-effort: confirm something with "Leave" shows up in listing/confirmation
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Leave")')
            )
        )

        shot = SCREEN_DIR / f"task2_checkin_leave_{f_dt:%d-%m-%Y}_to_{t_dt:%d-%m-%Y}.png"
        driver.save_screenshot(str(shot))
        assert shot.exists() and shot.stat().st_size > 0, f"Screenshot not saved: {shot}"
        print(f"✅ Screenshot saved at: {shot}")

    finally:
        # ===== 7) Close the app =====
        try:
            driver.quit()
        except Exception:
            pass
