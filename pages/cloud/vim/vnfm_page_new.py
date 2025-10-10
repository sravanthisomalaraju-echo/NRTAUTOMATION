import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time
from utilities.read_ini_file_configparser import getConfigOptionValue

class VimVnfMPageNew(BasePage):

    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(VimVnfMPageNew, self).__init__(driver)
        self.driver = driver

    vnfm_page_header = getConfigOptionValue("C:\\Automation-TestEnviornment\\CRAN-CMS-Automation\\configfiles\\common_locatior.ini","LoginPageLocator","_vnfm_page_header")

    # Vim-VnfM page related Actions/Methods
    def checkVnfmPageElementsPresence(self):
        vnfmPageExpectedElements = [self.vnfm_page_header]
        result = self.checkElementsPresenceOnPage(vnfmPageExpectedElements)
        return result

    def clickOnAddButtonVnFM(self):
        self.isElementDisplayed(locator=self._add_button, locatorType="xpath")
        self.isElementEnabled(locator=self._add_button, locatorType="xpath")
        self.elementClick(locator=self._add_button, locatorType="xpath")

    def enterNameInAddVnfmNameField(self,data):
            self.sendKeysOnElement(data, self._name_field, locatorType="xpath")

    def enterIpAddressInAddVnfmIpAddressField(self, data):
        self.sendKeysOnElement(data, self._ipaddress_field, locatorType="xpath")

    def enterPortNumberInAddVnfmPortField(self, data):
        self.sendKeysOnElement(data, self._port_field, locatorType="xpath")

    def enterUsernameInAddVnfmUsernameField(self, data):
        self.sendKeysOnElement(data, self._username_field, locatorType="xpath")

    def enterPasswordInAddVnfmPasswordField(self, data):
        self.sendKeysOnElement(data, self._password_field, locatorType="xpath")

    def selectIpTypeFromDropDown(self,data):
        self.selectElementFromDropDownMenuByVisibleText(data,self._ipType_field, locatorType="xpath")

    def selectProtocolFromDropDown(self,data):
        self.selectElementFromDropDownMenuByVisibleText(data,self._protocol_type, locatorType="xpath")

    def selectModeFromDropDown(self,data):
        self.selectElementFromDropDownMenuByVisibleText(data,self._mode_field, locatorType="xpath")

    def clickOnAddButtonVnFMFormFill(self):
        self.isElementDisplayed(locator=self._vnfm_form_add__button, locatorType="xpath")
        self.isElementEnabled(locator=self._vnfm_form_add__button, locatorType="xpath")
        self.elementClick(locator=self._vnfm_form_add__button, locatorType="xpath")

    def clickOnCancelButtonVnFMFormFill(self):
        self.isElementDisplayed(locator=self._vnfm_form_cancel_button, locatorType="xpath")
        self.isElementEnabled(locator=self._vnfm_form_cancel_button, locatorType="xpath")
        self.elementClick(locator=self._vnfm_form_cancel_button, locatorType="xpath")

    def addVirtualNetworkFuntionManger(self,name,ip,iptype,port,protocoltype,username,password,mode):
        self.waitForElement(locator=self._add_button, locatorType="xpath", pollFrequency=4)
        self.clickOnAddButtonVnFM()
        self.waitForElement(locator=self._name_field, locatorType="xpath", pollFrequency=4)
        self.enterNameInAddVnfmNameField(name)
        self.enterIpAddressInAddVnfmIpAddressField(ip)
        self.selectIpTypeFromDropDown(iptype)
        self.enterPortNumberInAddVnfmPortField(port)
        self.selectProtocolFromDropDown(protocoltype)
        self.enterUsernameInAddVnfmUsernameField(username)
        self.enterPasswordInAddVnfmPasswordField(password)
        self.selectModeFromDropDown(mode)
        time.sleep(6)
        self.clickOnCancelButtonVnFMFormFill()
