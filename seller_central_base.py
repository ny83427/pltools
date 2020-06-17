import chromedriver_autoinstaller
from selenium import webdriver
from time import sleep
import os


def init_web_driver(email, reuse):
    chromedriver_autoinstaller.install()

    options = webdriver.ChromeOptions()
    ddir = os.path.expanduser('~\\.amazon_seller_management\\US') if reuse else f'C:\\Tmp\\pltools\\{email.lower()}'
    options.add_argument(f'user-data-dir={ddir}')
    options.add_argument('--disable-extensions')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-notifications')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('prefs', {'profile.default_content_setting_values.notifications': 2})

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(7)

    driver.get('https://sellercentral.amazon.com/orders-v3/ref=xx_myo_dnav_xx?page=1')
    while len(driver.find_elements_by_css_selector('#myo-search-input')) == 0:
        print('Please login manually to initialize')
        sleep(5)
    return driver
