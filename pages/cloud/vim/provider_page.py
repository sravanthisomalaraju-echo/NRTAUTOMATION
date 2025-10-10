import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time

class VimProviderPage(BasePage):
    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(VimProviderPage, self).__init__(driver)
        self.driver = driver

    # Locators
    _provider_page_header = "//strong[.=' Cloud Provider ']"
    _provider_table_filter_list = ['Name', 'Pop ID', 'Pop IP', 'Cloud Type','Created Datetime']
    _select_provider_table_filter_item = "//div[@class='text-primary'][text()[normalize-space() = '{0}']]"

    # add provider related locator field
    _name_field = "//input[@id='name']"
    _pop_id_field = "//input[@id='popID']"
    _pop_ip_field = "//input[@id='popIP']"
    _select_pop_ip = "//select[@id='popIP']"
    _cloud_type_field = "//select[@id='cloudType']"
    _region_field = "//input[@id='region']"
    _keystone_port_field = "//input[@id='keystoneport']"
    #_verify_provider_add = "//table/tbody[@class='list']/tr/td[text()=' {0}']/following-sibling::td[text()=' {1}']//following-sibling::td[text()=' {2}']"
    #_verify_provider_Add popip comes with hyper link break the verification
    _verify_provider_add = "//tr/td[normalize-space()='{0}']/following-sibling::td[normalize-space()='{2}-{1}']"
    # Vim-VnfM page related Actions/Methods
    def checkProviderPageElementsPresence(self):
        ExpectedElements = [self._provider_page_header, self._base_page_size, self._base_filter_type_field,
                                        self._base_filter_button,
                                        self._base_fllter_clear_button, self._base_result, self._base_action_header, self._base_add_button,
                                        self._select_provider_table_filter_item.format(self._provider_table_filter_list[0]),
                                        self._select_provider_table_filter_item.format(self._provider_table_filter_list[1]),
                                        self._select_provider_table_filter_item.format(self._provider_table_filter_list[2]),
                                        self._select_provider_table_filter_item.format(self._provider_table_filter_list[3])]

        result = self.checkElementsPresenceOnPage(ExpectedElements)
        return result

    def enterNameInAddProviderNameField(self, data):
        self.sendKeysOnElement(data, self._name_field, locatorType="xpath")


    def enterPopIpInAddProviderPopIpField(self, data):
        self.sendKeysOnElement(data, self._pop_ip_field, locatorType="xpath")

    def enterPopIdInAddProviderPopIdField(self, data):
        self.sendKeysOnElement(data, self._pop_id_field, locatorType="xpath")

    def enterRegionInAddProviderRegionFieldForopenstack(self, data):
        self.sendKeysOnElement(data, self._region_field, locatorType="xpath")

    def enterkeystoneportInAddProviderRegionFieldForopenstack(self, data):
        self.sendKeysOnElement(data, self._keystone_port_field, locatorType="xpath")

    def selectPopIp(self,data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_pop_ip, locatorType="xpath")

    def selectCloudTypeFromDropDown(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._cloud_type_field, locatorType="xpath")


    def addCloudProvider(self, name, popip, cloudtype,region = "None",keystoneport = "None"):
        self.clickOnBaseAddButton()
        self.enterNameInAddProviderNameField(name)
        #self.enterPopIpInAddProviderPopIpField(popip) #older build has input popip field
        self.selectPopIp(popip)
        self.selectCloudTypeFromDropDown(cloudtype)
        if cloudtype == 'Openstack':
            self.enterRegionInAddProviderRegionFieldForopenstack(region)
            self.enterkeystoneportInAddProviderRegionFieldForopenstack(keystoneport)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button,locatorType="xpath")

    def verifyAdditionOfCloudProvider(self,name, popip, cloudtype):
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.waitForElement(locator=self._verify_provider_add.format(name, popip, cloudtype), locatorType="xpath")
        status = self.isElementPresent(locator=self._verify_provider_add.format(name, popip, cloudtype), locatorType="xpath")
        return status