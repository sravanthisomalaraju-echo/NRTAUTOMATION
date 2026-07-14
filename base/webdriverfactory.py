from selenium.webdriver.chrome.options import Options
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
            
            chrome_options = Options()
            
            # This checks if the code is running on GitHub's cloud servers
            if os.environ.get('GITHUB_ACTIONS') == 'true':
                print("Cloud environment detected: Running Headless")
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--window-size=1920,1080")
            else:
                print("Local environment detected: Running Visible Browser")
            
            # Pass the options into the driver creation
            # --- THIS IS THE CRUCIAL LINE WE CHANGED ---
            # We removed the webdriver-manager completely!
            driver = webdriver.Chrome(options=chrome_options)
            # -------------------------------------------
            
            driver.maximize_window()
            driver.implicitly_wait(30)
            driver.get(baseURL)

        else:
            print('Please select chrome browser')

        return driver
