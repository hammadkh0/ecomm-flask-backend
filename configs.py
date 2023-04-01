from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def selenium_config():

    ua = UserAgent()
    user_agent = ua.random

    options = Options()
    options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent})')
    # add incognito mode to options
    options.add_argument("--incognito")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)

    print(options.arguments)
    print("----------------------------------------")

    driver.set_window_size(1366, 768)
    # simulate headless mode by minimizing the window
    #driver.set_window_position(-2000, 0)
    return driver
