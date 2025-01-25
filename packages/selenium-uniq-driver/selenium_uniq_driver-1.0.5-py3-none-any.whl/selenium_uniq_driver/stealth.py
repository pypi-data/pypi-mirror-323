from selenium.webdriver import Chrome as Driver

from selenium_stealth import chrome_app
from selenium_stealth import iframe_content_window
from selenium_stealth import media_codecs
from selenium_stealth import navigator_permissions
from selenium_stealth import navigator_plugins
from selenium_stealth import navigator_webdriver
from selenium_stealth import with_utils
from selenium_stealth import window_outerdimensions

def stealth(driver: Driver, **kwargs) -> None:
    if not isinstance(driver, Driver):
        raise ValueError("driver must is selenium.webdriver.Chrome, currently this lib only support Chrome")

    with_utils(driver, **kwargs)
    chrome_app(driver, **kwargs)
    iframe_content_window(driver, **kwargs)
    media_codecs(driver, **kwargs)
    navigator_permissions(driver, **kwargs)
    navigator_plugins(driver, **kwargs)
    navigator_webdriver(driver, **kwargs)
    window_outerdimensions(driver, **kwargs)
