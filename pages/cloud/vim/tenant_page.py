import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time

class VimTenantPage(BasePage):
    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(VimTenantPage, self).__init__(driver)
        self.driver = driver

    # Locators
    _tenant_page_header = "//strong[.=' Cloud Tenant ']"
    _tenant_table_filter_list = ['Name', 'Cloud Profile ID', 'Username', 'Provider ID','Preferred Vnfm','Cloud Type','Sfc Type','Created Datetime']
    _select_tenant_table_filter_item = "//div[@class='text-primary'][text()[normalize-space() = '{0}']]"

    # add tenant related locator field
    _name_field = "//input[@id='name']"
    _cloud_profileId_field = "//input[@id='cloudProfileID']"
    _username_field = "//input[@id='username']"
    _password_field = "//input[@id='password']"
    _select_popid_field = "//select[@id='popID']"
    _select_prefered_vnfm_field = "//select[@id='preferredVnfm']"
    _select_cloudtype_field = "//select[@id='cloudType']"
    _select_sfctype_field = "//select[@id='sfcType']"

    _datacenter_field = "//input[@id='dataCenter']"
    _catalog_field = "//input[@id='catalog']"
    _organization_field = "//input[@id='organization']"
    _vpshereIp_field = "//input[@id='vsphereIp']"
    _vpshereUserName_field = "//input[@id='vsphereUserName']"
    _vpsherePassword_field = "//input[@id='vspherePassword']"

    _tenant_field = "//input[@id='tenant']"
    _select_keystone_ver = "//select[@id='keystoneversion']"
    _domain_field = "//input[@id='domain']"
    _verify_tenant_add = "//table/tbody[@class='list']/tr/td[normalize-space()='{0}']/following-sibling::td[normalize-space()='{1}']//following-sibling::td[normalize-space()='{2}']"


    # vim -tenant page related Actions/Methods
    def checkTenantPageElementsPresence(self):
        ExpectedElements = [self._tenant_page_header, self._base_page_size, self._base_filter_type_field,
                                        self._base_filter_button,self._base_fllter_clear_button, self._base_result,
                                        self._base_action_header, self._base_add_button,
                                        self._select_tenant_table_filter_item.format(self._tenant_table_filter_list[0]),
                                        self._select_tenant_table_filter_item.format(self._tenant_table_filter_list[1]),
                                        self._select_tenant_table_filter_item.format(self._tenant_table_filter_list[2]),
                                        self._select_tenant_table_filter_item.format(self._tenant_table_filter_list[3]),
                                        self._select_tenant_table_filter_item.format(self._tenant_table_filter_list[4]),
                                        self._select_tenant_table_filter_item.format(self._tenant_table_filter_list[5]),
                                        self._select_tenant_table_filter_item.format(self._tenant_table_filter_list[6]),
                                        self._select_tenant_table_filter_item.format(self._tenant_table_filter_list[7])]

        result = self.checkElementsPresenceOnPage(ExpectedElements)
        return result

    def enterNameInAddTenantNameField(self, data):
        self.sendKeysOnElement(data, self._name_field, locatorType="xpath")

    def enterUserNameInAddTenantUserNameField(self, data):
        self.sendKeysOnElement(data, self._username_field, locatorType="xpath")

    def enterPasswordInAddTenantPasswordField(self, data):
        self.sendKeysOnElement(data, self._password_field, locatorType="xpath")

    def enterDataCenterInAddTenantPageForVmwareType(self, data):
        self.sendKeysOnElement(data, self._datacenter_field, locatorType="xpath")

    def enterCatalogInAddTenantPageForVmwareType(self, data):
        self.sendKeysOnElement(data, self._catalog_field, locatorType="xpath")

    def enterOrganizationInAddTenantPageForVmwareType(self, data):
        self.sendKeysOnElement(data, self._organization_field, locatorType="xpath")

    def enterVpshereIpInAddTenantPageForVmwareType(self, data):
        self.sendKeysOnElement(data, self._vpshereIp_field, locatorType="xpath")

    def enterVpshereUserInAddTenantPageForVmwareType(self, data):
        self.sendKeysOnElement(data, self._vpshereUserName_field, locatorType="xpath")

    def enterVpsherePasswordInAddTenantPageForVmwareType(self, data):
        self.sendKeysOnElement(data, self._vpsherePassword_field, locatorType="xpath")

    def enterTenantInAddTenantPageForOpenstackType(self, data):
        self.sendKeysOnElement(data, self._tenant_field, locatorType="xpath")

    def enterDomainInAddTenantPageForOpenstackType(self, data):
        self.sendKeysOnElement(data, self._domain_field, locatorType="xpath")

    def selectKeyStoneVersionFromDropDownForOpenstackType(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_keystone_ver, locatorType="xpath")

    def selectPopIdFromDropDown(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_popid_field, locatorType="xpath")

    def selectPreferedVnfmFromDropDown(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_prefered_vnfm_field, locatorType="xpath")

    def selectCloudTypeFromDropDown(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_cloudtype_field, locatorType="xpath")

    def selectSfcTypeFromDropDown(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_sfctype_field, locatorType="xpath")

    def addVMwareTypeCloudTenant(self, name, username, password, popid, preferedVnfm, cloudtype, sfcType):
        self.clickOnBaseAddButton()
        self.waitForElement(locator=self._name_field, locatorType="xpath", pollFrequency=4)
        self.enterNameInAddTenantNameField(name)
        self.enterNameInAddTenantNameField(name)
        self.enterUserNameInAddTenantUserNameField(username)
        self.enterPasswordInAddTenantPasswordField(password)
        self.selectPopIdFromDropDown(popid)
        self.selectPreferedVnfmFromDropDown(preferedVnfm)
        self.selectCloudTypeFromDropDown(cloudtype)
        self.selectSfcTypeFromDropDown(sfcType)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")


    def addOpenStackTypeCloudTenant(self, name, username, password, popid, cloudtype, tenant,keyver, sfcType):
        self.clickOnBaseAddButton()
        #self.enterNameInAddTenantNameField(name)
        self.enterNameInAddTenantNameField(name)
        self.enterUserNameInAddTenantUserNameField(username)
        self.enterPasswordInAddTenantPasswordField(password)
        self.selectPopIdFromDropDown(popid)
        self.selectCloudTypeFromDropDown(cloudtype)
        self.enterTenantInAddTenantPageForOpenstackType(tenant)
        self.selectKeyStoneVersionFromDropDownForOpenstackType(keyver)
        #self.enterDomainInAddTenantPageForOpenstackType(domain)
        self.selectSfcTypeFromDropDown(sfcType)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")

    def addVmwareTypeCloudTenant(self, name, username, password, popid, preferedVnfm, cloudtype,datacenter,catalog,organisation,vspehereIp,vsphereUser	,vspherePasswd, sfcType):
        self.clickOnBaseAddButton()
        self.enterNameInAddTenantNameField(name)
        self.enterNameInAddTenantNameField(name)
        self.enterUserNameInAddTenantUserNameField(username)
        self.enterPasswordInAddTenantPasswordField(password)
        self.selectPopIdFromDropDown(popid)
        self.selectPreferedVnfmFromDropDown(preferedVnfm)
        self.selectCloudTypeFromDropDown(cloudtype)
        self.enterDataCenterInAddTenantPageForVmwareType(datacenter)
        self.enterCatalogInAddTenantPageForVmwareType(catalog)
        self.enterOrganizationInAddTenantPageForVmwareType(organisation)
        self.enterVpshereIpInAddTenantPageForVmwareType(vspehereIp)
        self.enterVpshereUserInAddTenantPageForVmwareType(vsphereUser)
        self.enterVpsherePasswordInAddTenantPageForVmwareType(vspherePasswd)
        self.selectSfcTypeFromDropDown(sfcType)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")

    def verifyAdditionOfCloudTenant(self,name, username,cloudtype):
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.waitForElement(locator=self._verify_tenant_add.format(name, username,cloudtype), locatorType="xpath")
        status = self.isElementPresent(locator=self._verify_tenant_add.format(name, username,cloudtype),locatorType="xpath")
        return status