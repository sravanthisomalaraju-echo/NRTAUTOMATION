import  utilities.custom_logger as cl
import logging
from base.basepage import BasePage
from pages.home.navigation_basepage_menu_map import NavigationBasePageMenuMap
import time
from configfiles.common_variable import *

class LoginPage(BasePage):

    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self,driver):
        super(LoginPage,self).__init__(driver)
        self.driver = driver
        self.nav = NavigationBasePageMenuMap(driver)
        self.baseURL = LOGIN_CONFIG['baseurl']

    #loginPage locators
    _login_Button = '//button[@id="login-submit"]'
    _username_field = '//input[@name="username"]'
    _password_field = '//input[@name="password"]'
    _product_title = '//span[contains(text(),"SIGN IN")]' #just to keep is page loaded
    _LogOutIcon = '//a/i[@title="Sign out"]'
    
    
    # loginPage Actions/Methods
    def isLoginPageLoaded(self):
        #self.waitForElement(self._product_title, locatorType="xpath")
        self.isElementDisplayed(self._product_title, locatorType="xpath")
        result = self.isElementPresent(self._product_title, locatorType="xpath")
        return result


    def clickLoginButton(self):
        self.waitForElement(self._login_Button,locatorType="xpath",pollFrequency=2,maxtimeout=6)
        self.elementClick(self._login_Button,locatorType="xpath")



    def enterUsernameField(self,username):
        #self.waitForElement(self._username_field, locatorType="xpath")
        time.sleep(1)
        self.sendKeysOnElement(username,self._username_field, locatorType="xpath")

    def enterPasswordField(self,password):
        #self.waitForElement(self._password_field, locatorType="xpath")
        time.sleep(1)
        self.sendKeysOnElement(password,self._password_field, locatorType="xpath")

    def login(self, username="", password=""):
        self.enterUsernameField(username)
        self.enterPasswordField(password)
        self.clickLoginButton()



    def verifySucessfulLogin(self):
        self.nav.waitForElement(locator=self._LogOutIcon, locatorType="xpath", pollFrequency=4)
        result = self.isElementPresent(self._LogOutIcon,locatorType="xpath")
        return result



    def verify_title(self):
        return self.verifyPageTitle('nVentory')

    def login_with_validation(self, username="", password=""):
        result = None

        result = self.isLoginPageLoaded()
        if result == False:
            self.log.error('Weburl is not getting loaded -- is Appication server not running ???')
            return result
        else:
            self.log.info('WebUrl is accessible')
            self.login_with_reset(username,password)
            #time.sleep(1)
            loginstatus = self.verifyLoginFailure()
            result = not loginstatus
            return result

    def check_login_internal(self):
        status = self.isElementPresent(locator=self._login_Button,locatorType="xpath")
        if status  == False:
            print('user is already logged in')
        return status

    def inventory_gui_login(self,username=LOGIN_CONFIG['defaultloginusername'],password=LOGIN_CONFIG['defaultloginpassword']):
        status = self.check_login_internal()

        if status == False:
            self.log.info('User is already logged in')
            return status

        result = None
        result = self.isLoginPageLoaded()

        if result == False:
            self.log.error('Weburl is not getting loaded -- is Appication server not running ???')
            return result
        else:
            self.log.info('WebUrl is accessible')
            self.login(username, password)
            result = self.isElementPresent(self._LogOutIcon, locatorType="xpath")
            
            return result
