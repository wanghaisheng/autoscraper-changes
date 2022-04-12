#template for scrape
from selenium import webdriver
import undetected_chromedriver as uc
import seleniumwire.undetected_chromedriver as seleniumwirewebdriver

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
print('demo scrape using playwright')

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]
for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

driver.get('http://nytimes.com')
print(driver.title)

#https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/347


# from webdriver_manager.utils import get_browser_version_from_os

# version = get_browser_version_from_os("google-chrome")

# print(version)



# # undetected_chromedriver==3.1.3
# from undetected_chromedriver import Chrome

# if __name__ == "__main__":
#     ctx = Chrome(headless=True)
#     try:
#         ctx.get("https://www.baidu.com")
#     finally:
#         ctx.quit()