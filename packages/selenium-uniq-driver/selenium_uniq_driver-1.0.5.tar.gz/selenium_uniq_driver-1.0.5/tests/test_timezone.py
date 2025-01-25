from .helper import uniqueness_percentage, uniq_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

def test_timezone_uniqness():
    timezone_list = []
    for _ in range(5):
        time.sleep(4)
        driver = uniq_driver(["device_timezone"])
        driver.get("https://webbrowsertools.com/timezone/")
        timezone_td = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "timeZone"))
        )
        if timezone_td.text:
            timezone = timezone_td.text
        else:
            print("Timezone not found!")
            timezone = "EMPTY_TIMEZONE"
        timezone_list.append(timezone)

    uniqness = uniqueness_percentage(timezone_list)
    print()
    print("TIMEZONE LIST")
    print("============================================")
    for index, timezone in enumerate(timezone_list):
        print(f"{index+1}) {timezone}")
    print(f"TIMEZONE UNIQNESS TEST PERCENTAGE: {uniqness}%")

    assert uniqness > 0

