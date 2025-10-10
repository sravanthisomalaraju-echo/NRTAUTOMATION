import utilities.custom_logger as cl
from base.basepage import BasePage

class NavigationAdministrationPageMenuMap(BasePage):
    log = cl.customLoggerMethod()

    def __init__(self, driver):
        super(NavigationAdministrationPageMenuMap, self).__init__(driver)
        self.driver = driver

    # Locators
    _adminstration_page_header = "//h1[contains(text(),'Administration')]"

    _adminstration_page_menu_list = ['User Management', 'LDAP Management', 'Radius Management', 'Logging', 'Configuration','Backup & Restore','VLB Configuration']
    _user_mgmt_sub_menu_list = ['service_group','user_roles','user','remote_auth_config']
    _ldap_mgmt_sub_menu_list = ['ldap_config', 'ldap_server','ldap_roles']
    _radius_mgmt_sub_menu_list = ['radius_config','radius_server','radius_roles']
    _logging_sub_menu_list = ['activity_log']
    _configuration_sub_menu_list = ['purge_config', 'kpi_config', 'site_config']
    _back_and_restore_sub_menu_list = ['system_backup', 'system_restore', 'system_backup_file']
    _vlb_configuration_sub_menu_list = ['vlb_port_config']

    _select_sub_menu_item = "//a[@href='#/menu/admin/{0}']/span"

    _search_box_field = "//form[@id='custom-search-input']//input[@type='text']"

    def navigateToUserManagementServiceGroupMenu(self):
        #self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[0]), locatorType="xpath")
        self.elementClick(locator=self._select_sub_menu_item.format(self._user_mgmt_sub_menu_list[0]), locatorType="xpath")

    def navigateToUserManagementRolesMenu(self):
        #self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[1]),locatorType="xpath")
        self.elementClick(locator=self._select_sub_menu_item.format(self._user_mgmt_sub_menu_list[1]), locatorType="xpath")

    def navigateToUserManagementUsersMenu(self):
        #self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._vim_sub_menu_list[2]),locatorType="xpath")
        self.elementClick(locator=self._select_sub_menu_item.format(self._user_mgmt_sub_menu_list[2]), locatorType="xpath")

    def navigateToUserManagementRemoteAuthConfigMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._user_mgmt_sub_menu_list[3]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._vol_man_sub_menu_list[0]), locatorType="xpath")

    def navigateToLdapMangementConfigurationMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._ldap_mgmt_sub_menu_list[0]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._vol_man_sub_menu_list[1]),locatorType="xpath")

    def navigateToLdapMangementLdapServerMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._ldap_mgmt_sub_menu_list[1]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._inventory_sub_menu_list[0]), locatorType="xpath")

    def navigateToLdapMangementRoleMappingMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._ldap_mgmt_sub_menu_list[2]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[0]),locatorType="xpath")

    def navigateToRadiusMangementConfigurationMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._radius_mgmt_sub_menu_list[0]), locatorType="xpath")

    def navigateToRadiusMangementRadiusServerMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._radius_mgmt_sub_menu_list[1]), locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[2]),locatorType="xpath")

    def navigateToRadiusMangementRoleMappingMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._radius_mgmt_sub_menu_list[2]), locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[3]),locatorType="xpath")

    def navigateToLoggingActivityLogMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._logging_sub_menu_list[0]), locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._descriptors_sub_menu_list[4]),locatorType="xpath")

    def navigateToConfigurationPureConfigMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._configuration_sub_menu_list[0]), locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[0]),locatorType="xpath")

    def navigateToConfigurationKpiConfigMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._configuration_sub_menu_list[1]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[1]),locatorType="xpath")

    def navigateToConfigurationSiteConfigMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._configuration_sub_menu_list[2]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[2]),locatorType="xpath")

    def navigateToBackupRestoreBackupMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._back_and_restore_sub_menu_list[0]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[3]),locatorType="xpath")

    def navigateToBackupRestoreRestoreMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._back_and_restore_sub_menu_list[1]),locatorType="xpath")
        #self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[4]),locatorType="xpath")

    def navigateToBackupRestoreStatusMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._back_and_restore_sub_menu_list[2]), locatorType="xpath")
        # self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[4]),locatorType="xpath")

    def navigateToVlbConfigurationVlbPortConfigMenu(self):
        self.webScrollIntoViewAndClickElement(locator=self._select_sub_menu_item.format(self._vlb_configuration_sub_menu_list[0]), locatorType="xpath")
        # self.elementClick(locator=self._select_sub_menu_item.format(self._catalog_sub_menu_list[4]),locatorType="xpath")
