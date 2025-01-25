from .helper import uniqueness_percentage, uniq_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

def test_webgl_renderer_uniqness():
    renderer_list = []
    for _ in range(5):
        time.sleep(4)
        driver = uniq_driver(["device_webgl"])
        driver.get("https://bot.sannysoft.com/")
        renderer_td = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "webgl-renderer"))
        )
        if renderer_td.text:
            renderer_id = renderer_td.text
        else:
            print("WebGL Renderer not found!")
            renderer_id = "EMPTY_WEBGL_RENDERER"
        renderer_list.append(renderer_id)

    uniqness = uniqueness_percentage(renderer_list)
    print()
    print("WEBGL RENDERER LIST")
    print("============================================")
    for index, renderer_id in enumerate(renderer_list):
        print(f"{index+1}) {renderer_id}")
    print(f"WebGL Renderer UNIQNESS TEST PERCENTAGE: {uniqness}%")

    assert uniqness > 0

