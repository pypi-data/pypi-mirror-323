from setuptools import setup, find_packages

setup(
    name="selenium-uniq-driver",              
    version="1.0.5",                
    author="AlexanderTsk",              
    author_email="alex13jixy@gmail.com",  
    description="Create uniq selenium webdriver.",  
    long_description=open("README.md", "r").read(),  
    long_description_content_type="text/markdown",
    url="https://github.com/AlexanderTsk/selenium-uniq-driver",  
    packages=find_packages(),
    package_data={"selenium_uniq_driver": ["js/*.js"]},
    install_requires=[
        "blinker==1.4",
        "selenium-stealth",
        "selenium-wire",
        "random-user-agent",
        "setuptools",
        "pytest"
    ],     
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
