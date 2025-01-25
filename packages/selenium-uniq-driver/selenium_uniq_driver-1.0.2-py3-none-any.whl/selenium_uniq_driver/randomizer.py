from .params import HardwareType, SoftwareName, OperatingSystem
from . import data as UniqData
from random_user_agent.user_agent import UserAgent
import random

class Randomize:

    def __init__(self, hardware_type: HardwareType, operating_system: OperatingSystem, software_name: SoftwareName):
        self._hardware_type = hardware_type
        self._operating_system = operating_system
        self._software_name = software_name

    def get_user_agent(self) -> str:
        """
        Generates a random User-Agent based on hardware, operating system, and software.
        :return: A random User-Agent string.
        """
        user_agent_rotator = UserAgent(software_names=[self._software_name.value], operating_systems=[self._operating_system.value], hardware_types=[self._hardware_type.value])
        return user_agent_rotator.get_random_user_agent()

    def get_language(self) -> str:
        """
        Generates a random browser language setting.
        :return: A string representing the language setting.
        """
        languages = UniqData.LANGUAGES

        primary_language = random.choice(languages)

        additional_languages = [
            f"{lang};q={round(random.uniform(0.5, 0.9), 1)}"
            for lang in random.sample(languages, k=min(len(languages), 3))
            if lang != primary_language
        ]

        return ','.join([primary_language] + additional_languages)
    
    def get_timezone(self) -> str:
        """
        Generates a random browser timezone setting.
        :return: A string representing the timezone setting.
        """
        timezones = UniqData.TIMEZONES
        random_timezone = random.choice(timezones)

        return random_timezone
    
    def get_webgl_vendor(self)->str | None:
        """
        Generates a random webgl vendor value based on the operating system.
        :return: A string representing the vendor, or None if unsupported.
        """
        if self._operating_system == OperatingSystem.WINDOWS:
            return random.choice(UniqData.WEBGL_VENDORS["WINDOWS"])
        if self._operating_system == OperatingSystem.LINUX:
            return random.choice(UniqData.WEBGL_VENDORS["LINUX"])
        if self._operating_system == OperatingSystem.ANDROID:
            return random.choice(UniqData.WEBGL_VENDORS["ANDROID"])
        if self._operating_system == OperatingSystem.IOS:
            return random.choice(UniqData.WEBGL_VENDORS["IOS"])

        return None
    
    def get_webgl_renderer(self)->str | None:
        """
        Generates a random webgl renderer value based on the operating system.
        :return: A string representing the renderer, or None if unsupported.
        """
        if self._operating_system == OperatingSystem.WINDOWS:
            return random.choice(UniqData.WEBGL_RENDERERS["WINDOWS"])
        if self._operating_system == OperatingSystem.LINUX:
            return random.choice(UniqData.WEBGL_RENDERERS["LINUX"])
        if self._operating_system == OperatingSystem.ANDROID:
            return random.choice(UniqData.WEBGL_RENDERERS["ANDROID"])
        if self._operating_system == OperatingSystem.IOS:
            return random.choice(UniqData.WEBGL_RENDERERS["IOS"])

        return None

    def get_platform(self) -> str | None:
        """
        Generates a random platform value based on the operating system.
        :return: A string representing the platform, or None if unsupported.
        """
        if self._operating_system == OperatingSystem.WINDOWS:
            return random.choice(UniqData.PLATFORMS["WINDOWS"])
        if self._operating_system == OperatingSystem.LINUX:
            return random.choice(UniqData.PLATFORMS["LINUX"])
        if self._operating_system == OperatingSystem.ANDROID:
            return random.choice(UniqData.PLATFORMS["ANDROID"])
        if self._operating_system == OperatingSystem.IOS:
            return random.choice(UniqData.PLATFORMS["IOS"])

        return None
    
    def get_viewport(self) -> tuple[int, int]:
        """
        Generates a random viewport size based on the hardware type.
        :return: A tuple (width, height) representing the viewport size.
        """
        desktop_viewports = [(1920, 1080), (1366, 768), (1536, 864), (1280, 720), (1440, 900)]
        mobile_viewports = [(360, 800), (390, 844), (414, 896), (375, 667), (412, 732)]

        if self._hardware_type == HardwareType.COMPUTER:
            return random.choice(desktop_viewports)
        if self._hardware_type == HardwareType.MOBILE:
            return random.choice(mobile_viewports)

        return (0, 0)  # Default in case of unexpected hardware type
