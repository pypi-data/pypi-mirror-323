from .helper import uniqueness_percentage, uniq_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

def test_audio_uniqness():
    audio_id_list = []
    for _ in range(5):
        time.sleep(4)
        driver = uniq_driver(["audio_fingerprint"])
        driver.get("https://webbrowsertools.com/audiocontext-fingerprint/")
        audio_id_td = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "fp_dynamics_compressor"))
        )
        if audio_id_td.text:
            audio_id = audio_id_td.text
        else:
            print("Audio ID not found!")
            audio_id = "EMPTY_AUDIO_ID"
        audio_id_list.append(audio_id)

    uniqness = uniqueness_percentage(audio_id_list)
    print()
    print("AUDIO ID LIST")
    print("============================================")
    for index, audio_id in enumerate(audio_id_list):
        print(f"{index+1}) {audio_id}")
    print(f"AUDIO UNIQNESS TEST PERCENTAGE: {uniqness}%")

    assert uniqness > 0

