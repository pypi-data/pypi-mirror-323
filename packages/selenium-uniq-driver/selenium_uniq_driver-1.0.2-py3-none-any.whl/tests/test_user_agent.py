from .helper import uniqueness_percentage, uniq_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

def test_user_agent_uniqness():
    user_agents_list = []
    for _ in range(5):
        time.sleep(4)
        driver = uniq_driver(["user_agent_and_language"])
        driver.get("https://webbrowsertools.com/useragent/")
        user_agent_span = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ua_n"))
        )
        if user_agent_span.get_attribute("textContent"):
            user_agent = user_agent_span.get_attribute("textContent")
        else:
            print("User-agent not found or empty!")
            user_agent = "EMPTY_USER_AGENT"
        user_agents_list.append(user_agent)

    uniqness = uniqueness_percentage(user_agents_list)
    print()
    print("USER AGENTS LIST")
    print("============================================")
    for index, user_agent in enumerate(user_agents_list):
        print(f"{index+1}) {user_agent}")
    print(f"USER AGENT UNIQNESS TEST PERCENTAGE: {uniqness}%")

    assert uniqness > 0
