from selenium.webdriver.chrome.options import Options
from selenium import webdriver
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
                chrome_options.add_argument("--disable-gpu")
                
                # --- NEW: The Disguise! ---
                # This tricks the website into thinking we are on a normal Windows laptop
                chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            else:
                print("Local environment detected: Running Visible Browser")
            
            # Pass the options into the driver creation
            # --- THIS IS THE CRUCIAL LINE WE CHANGED ---
            # We removed the webdriver-manager completely!
            driver = webdriver.Chrome(options=chrome_options)
            
            # --- THE FIX ---
            # Remove driver.maximize_window() and use this instead:
            driver.set_window_size(1920, 1080)
            
            driver.implicitly_wait(30)
           # --- NEW: Force a crash if the page hangs for more than 45 seconds ---
            driver.set_page_load_timeout(45) 
            
            print(f"Navigating to {baseURL}...")
            driver.get(baseURL)
            print("Successfully loaded the login page!")

        else:
            print('Please select chrome browser')

        return driver
