from .params import HardwareType, SoftwareName, OperatingSystem
from .randomizer import Randomize
from .stealth import stealth
from seleniumwire import webdriver
import random
import logging
import os
from pathlib import Path

class UniqDriver:
    
    def __init__(self, hardware_type: HardwareType, operating_system: OperatingSystem, software_name: SoftwareName):
        self._hardware_type = hardware_type
        self._operating_system = operating_system
        self._software_name = software_name

        self.randomizer = Randomize(self._hardware_type,  self._operating_system, self._software_name)

        self._options = None
        self._seleniumwire_options = {}
        self._scripts_dir = Path(__file__).parent.joinpath("js")

        self._entropy_methods = {
            "user_agent_and_language": self._change_user_agent_and_language,
            "device_viewport": self._change_device_viewport,
            "device_timezone": self._change_device_timezone,
            "device_webgl": self._change_device_webgl,
            "canvas_fingerprint": self._change_canvas_fingerprint,
            "audio_fingerprint": self._change_audio_fingerprint,
        }

    def create(self, entropy_methods: list[str] = None) -> webdriver.Chrome:
        """
        Creates a web driver with the specified entropy modification methods.
        :param entropy_methods: List of method names for modifications. If None, all methods are used.
        :return: A configured Chrome WebDriver instance.
        """

        if self._options is None:
            self._options = webdriver.ChromeOptions()
        #self._options.add_argument("--headless")

        self._options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self._options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(options=self._options, seleniumwire_options=self._seleniumwire_options)
        
        stealth(driver)
        self._add_entropy(driver, entropy_methods)
      

        return driver

    def _add_entropy(self, driver: webdriver.Chrome, entropy_methods: list[str] = None):
        if entropy_methods is None:
            entropy_methods = list(self._entropy_methods.keys())

        for method_name in entropy_methods:
            method = self._entropy_methods.get(method_name)
            if method:
                method(driver)
            else:
                logging.warning(f"Method '{method_name}' is not recognized and will be skipped.")

    def _change_user_agent_and_language(self, driver: webdriver.Chrome):
        # CHANGING USER AGENT/PLATFORM/BROWSER LANGUAGE
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": self.randomizer.get_user_agent(),
            "acceptLanguage": self.randomizer.get_language(),
            "platform": self.randomizer.get_platform()
        })

    def _change_device_viewport(self, driver: webdriver.Chrome):
        # CHANGING DEVICE VIEWPORT
        is_mobile = self._hardware_type == HardwareType.MOBILE
        width, height = self.randomizer.get_viewport()
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            "width": width,
            "height": height,
            "deviceScaleFactor": random.randint(0, 3),
            "mobile": is_mobile
        })

    def _change_device_timezone(self, driver: webdriver.Chrome):
        # CHANGING DEVICE TIMEZONE
        driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {
            "timezoneId": self.randomizer.get_timezone() 
        })
     
    def _change_canvas_fingerprint(self, driver: webdriver.Chrome):
        # CHANGING CANVAS FINGERPRINT
        script_path = os.path.join(self._scripts_dir, "for_canvas.js")
        with open(script_path, "r") as file:
            for_canvas = file.read()
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": for_canvas
        })

    def _change_audio_fingerprint(self, driver: webdriver.Chrome):
        # CHANGING AUDIO FINGERPRINT
        script_path = os.path.join(self._scripts_dir, "for_audio.js")
        with open(script_path, "r") as file:
            for_audio = file.read()
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": for_audio
        })
    
    def _change_device_webgl(self, driver: webdriver.Chrome):
        # CHANGING WEBGL DATA
        script_path = os.path.join(self._scripts_dir, "for_webgl.js")
        with open(script_path, "r") as file:
            for_webgl = file.read()

        vendor = self.randomizer.get_webgl_vendor()
        renderer = self.randomizer.get_webgl_renderer()
        if vendor is None:
            vendor = 'undefined'
        if renderer is None:
            renderer = 'undefined'

        for_webgl = for_webgl.replace('vendor_flag_placeholder', vendor)
        for_webgl = for_webgl.replace('renderer_flag_placeholder', renderer)

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": for_webgl
        })
    
    def set_options(self, options: webdriver.ChromeOptions):
        self._options = options


    def set_proxy(self, host: str, port: str, login: str, password: str, type: str):
        """
        Sets a proxy for the WebDriver.
        :param host: Proxy host address.
        :param port: Proxy port.
        :param login: Proxy username.
        :param password: Proxy password.
        :param proxy_type: Proxy type ('socks5', 'http', 'https').
        :raises ValueError: If the proxy type is unsupported.
        """

        if type in ['socks5', 'http', 'https']:
            self._seleniumwire_options = {
                'proxy': {
                    'http': f"{type}://{login}:{password}@{host}:{port}",
                    'https': f"{type}://{login}:{password}@{host}:{port}",
                }
            }
        else:
            raise ValueError(f"Unsupported proxy type: {type}. Supported types are 'socks5', 'http', 'https'.")
