import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time

class VimVnfMPage(BasePage):

    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(VimVnfMPage, self).__init__(driver)
        self.driver = driver

    # Locators
    _vnfm_page_header = "//strong[.=' Virtual Network Functions Manager ']"
    _vnfm_table_filter_list = ['Name', 'Ip Address', 'Ip Type','Port','Protocol Type','User Name','Mode','Status','Created Datetime']
    _select_vnfm_table_filter_item = "//div[@class='text-primary'][text()[normalize-space() = '{0}']]"

    #add vnfm related locator field
    _name_field = "//input[@id = 'name']"
    _ipaddress_field = "// input[@id = 'ipAddress']"
    _ipType_field = "//select[@id='ipType']"
    _port_field = "//input[@id='port']"
    _protocol_type = "//select[@id='protocolType']"
    _username_field = "//input[@id='userName']"
    _password_field = "//input[@id='password']"
    _pop_id_field = "//input[@id='popIP']"
    _mode_field = "//select[@id='mode']"
    _is_prefervnfm_field = "//select[@id='isPreferredVnfm']"
    _verify_vnfm_add ="//table/tbody[@class='list']/tr/td[normalize-space()='{0}']/following-sibling::td[normalize-space()='{1}']//following-sibling::td[normalize-space()='{2}']//following-sibling::td[normalize-space()='{3}']"
    _vnfm_status = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td[normalize-space()='{3}']/following-sibling::td[1]"

    # Vim-VnfM page related Actions/Methods
    def checkVnfmPageElementsPresence(self):
        vnfmPageExpectedElements = [self._vnfm_page_header,self._base_page_size,self._base_filter_type_field,self._base_filter_button,
                            self._base_fllter_clear_button,self._base_result,self._base_action_header,self._base_add_button,
                            self._select_vnfm_table_filter_item.format(self._vnfm_table_filter_list[0]),
                            self._select_vnfm_table_filter_item.format(self._vnfm_table_filter_list[1]),
                            self._select_vnfm_table_filter_item.format(self._vnfm_table_filter_list[2]),
                            self._select_vnfm_table_filter_item.format(self._vnfm_table_filter_list[3]),
                            self._select_vnfm_table_filter_item.format(self._vnfm_table_filter_list[4]),
                            self._select_vnfm_table_filter_item.format(self._vnfm_table_filter_list[5]),
                            self._select_vnfm_table_filter_item.format(self._vnfm_table_filter_list[6]),
                            self._select_vnfm_table_filter_item.format(self._vnfm_table_filter_list[7]),
                            self._select_vnfm_table_filter_item.format(self._vnfm_table_filter_list[8])]

        result = self.checkElementsPresenceOnPage(vnfmPageExpectedElements)
        return result

    def enterNameInAddVnfmNameField(self,data):
            self.sendKeysOnElement(data, self._name_field, locatorType="xpath")

    def enterPopIp(self,data):
            self.sendKeysOnElement(data, self._pop_id_field, locatorType="xpath")

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

    def selectIsPreferedVnfmFromDropDown(self,data):
        self.selectElementFromDropDownMenuByVisibleText(data,self._is_prefervnfm_field, locatorType="xpath")

    def addVirtualNetworkFuntionMangerOld(self,name,ip,iptype,port,protocoltype,username,password,mode):
        self.clickOnBaseAddButton()
        self.enterNameInAddVnfmNameField(name)
        self.enterIpAddressInAddVnfmIpAddressField(ip)
        self.selectIpTypeFromDropDown(iptype)
        self.enterPortNumberInAddVnfmPortField(port)
        self.selectProtocolFromDropDown(protocoltype)
        self.enterUsernameInAddVnfmUsernameField(username)
        self.enterPasswordInAddVnfmPasswordField(password)
        self.selectModeFromDropDown(mode)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button,locatorType="xpath")

    def addVirtualNetworkFuntionManger(self,name,ip,iptype,port,protocoltype,username,password,mode,popip,isPreferVnfm):
        self.clickOnBaseAddButton()
        self.enterNameInAddVnfmNameField(name)
        self.enterIpAddressInAddVnfmIpAddressField(ip)
        self.selectIpTypeFromDropDown(iptype)
        #self.enterPortNumberInAddVnfmPortField(port) # these field are not present in latest cem build
        self.selectProtocolFromDropDown(protocoltype)
        #self.enterUsernameInAddVnfmUsernameField(username) # these field are not present in latest cem build
        #self.enterPasswordInAddVnfmPasswordField(password) # these field are not present in latest cem build
        self.selectModeFromDropDown(mode)
        self.enterPopIp(popip)
        self.selectIsPreferedVnfmFromDropDown(isPreferVnfm.upper())
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button,locatorType="xpath")

    def verifyAdditionOfVirtualNetworkFuntionManger(self,name,ip,protocoltype,mode):
        self.waitForElement(locator=self._base_add_button,locatorType="xpath")
        self.waitForElement(locator=self._verify_vnfm_add.format(name,ip,protocoltype,mode),locatorType="xpath")
        status = self.isElementPresent(locator=self._verify_vnfm_add.format(name,ip,protocoltype,mode),locatorType="xpath")
        return status

    def checkVNFMPresenceWithStatus(self,name,ip,protocoltype,mode,status,iteration=10):
        state = False
        self.waitForElement(locator=self._base_add_button, locatorType="xpath", pollFrequency=2)
        for i in range(iteration):
            element_status = self._vnfm_status.format(name,ip,protocoltype,mode) + "[normalize-space()='{0}']".format(status)
            state = self.isElementPresent(locator=element_status , locatorType="xpath")
            status2 = self.isElementEnabled(locator=element_status , locatorType="xpath")
            if state == True:
                self.log.info('Element found after :: ' + str(int(i * 10)) + ' :: seconds at attempt :: ' + str(i))
                self.log.info('Element found ' + element_status + ' enable status:: ' + str(status2))
                break
            else:
                time.sleep(2)
                self.log.info('looking for the element ' + element_status + ' enablestatus :: '+ str(status2))
                self.log.info('Element did not found after :: ' + str(int(i * 10)) + ' :: seconds at attempt :: ' + str(i))
        return state