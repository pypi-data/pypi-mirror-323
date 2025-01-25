from selenium_uniq_driver import UniqDriver, HardwareType, SoftwareName, OperatingSystem
from selenium import webdriver

def uniqueness_percentage(lst)->int:
    if not lst: 
        return 0

    from collections import Counter
    
    total_elements = len(lst)
    element_counts = Counter(lst)  
    unique_count = sum(1 for count in element_counts.values() if count == 1)  
    
    uniqueness = unique_count / total_elements * 100
    return int(uniqueness)


def uniq_driver(entropy_methods:list[str] | None = None):

    hardware_type = HardwareType.MOBILE
    operating_system = OperatingSystem.ANDROID
    software_name = SoftwareName.CHROME

    driver_creator = UniqDriver(hardware_type=hardware_type, software_name=software_name, operating_system=operating_system)
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver_creator.set_options(options)


    return driver_creator.create(entropy_methods)