from .helper import uniqueness_percentage, uniq_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

def test_canvas_uniqness():
    canvas_id_list = []
    for _ in range(5):
        time.sleep(4)
        driver = uniq_driver(["canvas_fingerprint"])
        driver.get("https://webbrowsertools.com/canvas-fingerprint/")
        canvas_id_td = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "fp_spoofed_random_before"))
        )
        if canvas_id_td.text:
            canvas_id = canvas_id_td.text
        else:
            print("Canvas ID not found!")
            canvas_id = "EMPTY_CANVAS_ID"
        canvas_id_list.append(canvas_id)

    uniqness = uniqueness_percentage(canvas_id_list)
    print()
    print("CANVAS ID LIST")
    print("============================================")
    for index, canvas_id in enumerate(canvas_id_list):
        print(f"{index+1}) {canvas_id}")
    print(f"CANVAS UNIQNESS TEST PERCENTAGE: {uniqness}%")

    assert uniqness > 0

