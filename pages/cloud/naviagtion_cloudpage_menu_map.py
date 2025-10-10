import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time

class NavigationCloudPageMenuMap(BasePage):

    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(NavigationCloudPageMenuMap, self).__init__(driver)
        self.driver = driver

    # Locators
    _Cloud_page_header = "//h1[contains(text(),'Cloud')]"

    _cloudpage_menu_list = ['vim', 'Volume Management', 'Inventory', 'Descriptors', 'Catalog']
    _vim_sub_menu_list = ['vnfm_config','cloud_provider_config','cloud_tenant_config']
    _vol_man_sub_menu_list = ['volume_flavor', 'volume_preconfig']
    _inventory_sub_menu_list = ['image_config']
    _descriptors_sub_menu_list = ['descriptor', 'rolling_upgrade', 'vdu_product', 'data_model','vnf_data_config']

    _catalog_sub_menu_list = ['nsd', 'vnfd', 'lvnd', 'vld', 'lcmd']

    _select_sub_menu_item = "//a[@href='#/menu/vnfm/{0}']/span"

    _search_box_field = "//form[@id='custom-search-input']//input[@type='text']"

    def navigateToVimVnfmMenu(self):
        #self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[0]), locatorType="xpath")
        self.waitForElement(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[0]),locatorType="xpath", pollFrequency=4)
        self.elementClick(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[0]), locatorType="xpath")

    def navigateToVimProviderMenu(self):
        #self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[1]),locatorType="xpath")
        self.waitForElement(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[1]),locatorType="xpath", pollFrequency=4)
        self.elementClick(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[1]), locatorType="xpath")

    def navigateToVimTenantMenu(self):
        #self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[2]),locatorType="xpath")
        self.waitForElement(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[2]),locatorType="xpath", pollFrequency=4)
        self.elementClick(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[2]), locatorType="xpath")

    def navigateToVolManageflavourMenu(self):
        self.waitForElement(locator=self._select_sub_menu_item.format(self._vol_man_sub_menu_list[0]),locatorType="xpath", pollFrequency=4)
        #self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._vol_man_sub_menu_list[0]),locatorType="xpath")
        self.elementClick(locator=self._select_sub_menu_item.format(self._vol_man_sub_menu_list[0]), locatorType="xpath")

    def navigateToVolManagePreConfigMenu(self):
        self.waitForElement(locator=self._select_sub_menu_item.format(self._vol_man_sub_menu_list[1]),locatorType="xpath", pollFrequency=4)
        #self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._vol_man_sub_menu_list[1]),locatorType="xpath")
        self.elementClick(locator=self._select_sub_menu_item.format(self._vol_man_sub_menu_list[1]),locatorType="xpath")

    def navigateToInventoryImagesMenu(self):
        #self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._inventory_sub_menu_list[0]),locatorType="xpath")
        self.waitForElement(locator=self._select_sub_menu_item.format(self._inventory_sub_menu_list[0]),locatorType="xpath", pollFrequency=4)
        self.elementClick(locator=self._select_sub_menu_item.format(self._inventory_sub_menu_list[0]), locatorType="xpath")

    def navigateToDescriptorsDescriptorMenu(self):
        self.webScroll("down")
        self.waitForElement(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[0]),locatorType="xpath",pollFrequency=4)
        self.elementClick(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[0]),locatorType="xpath")

    def navigateToDescriptorsRollingUpgradeMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[1]), locatorType="xpath")

    def navigateToDescriptorsProductMappingMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[2]), locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[2]),locatorType="xpath")

    def navigateToDescriptorsConfigModelMenu(self):
        #self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[3]), locatorType="xpath")
        self.webScrollIntoView(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[3]), locatorType="xpath")
        self.elementClick(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[3]),locatorType="xpath")

    def navigateToDescriptorsConfigDataMenu(self):
        self.webScrollIntoView(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[4]), locatorType="xpath")
        self.elementClick(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[4]),locatorType="xpath")

    def navigateToCatalogNsdMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[0]), locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[0]),locatorType="xpath")

    def navigateToCatalogVnfdMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[1]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[1]),locatorType="xpath")

    def navigateToCatalogLvndMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[2]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[2]),locatorType="xpath")

    def navigateToCatalogVldMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[3]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[3]),locatorType="xpath")

    def navigateToCatalogLcmdMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[4]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[4]),locatorType="xpath")

    def EnteritemToBeSearchInSearchBox(self,item):
        self.waitForElement(locator=self._search_box_field,locatorType="xpath", pollFrequency=4)
        self.sendKeysOnElement(item,self._search_box_field, locatorType="name")
