from .helper import uniqueness_percentage, uniq_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

def test_viewport_uniqness():
    resolution_list = []
    for _ in range(5):
        time.sleep(4)
        driver = uniq_driver(["device_viewport"])
        driver.get("https://webbrowsertools.com/screen-size/")
        resolution_td = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "resolution"))
        )
        if resolution_td.text:
            resolution = resolution_td.text
        else:
            print("Resolution not found!")
            resolution = "EMPTY_RESOLUTION"
        resolution_list.append(resolution)

    uniqness = uniqueness_percentage(resolution_list)
    print()
    print("RESOLUTION LIST")
    print("============================================")
    for index, resolution in enumerate(resolution_list):
        print(f"{index+1}) {resolution}")
    print(f"RESOLUTION UNIQNESS TEST PERCENTAGE: {uniqness}%")

    assert uniqness > 0

