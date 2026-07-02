from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
os.environ['WDM_SSL_VERIFY'] = '0'
from configfiles.common_variable import *


'''
    WebDriver Factory class implementation
    It creates a webdriver instance based on browser configurations
'''

class WebDriverFactory():
    def __init__(self,browser):
        self.browser = browser

    def getWebDriverInstance(self):
        '''
        Get WebDriver Instance based on the browser configuration
               Returns:
                   WebDriver Instance
        '''
        driver = None
        baseURL = LOGIN_CONFIG['baseurl']

        if self.browser == "chrome":
            print('Running test on Chrome')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.maximize_window()
            driver.implicitly_wait(30)
            driver.get(baseURL)

        else:
            print('Please select chrome browser')

        return driver

