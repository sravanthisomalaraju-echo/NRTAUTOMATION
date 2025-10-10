import  utilities.custom_logger as cl
import logging
from base.basepage import BasePage
from pages.home.navigation_basepage_menu_map import NavigationBasePageMenuMap
from pages.cloud.naviagtion_cloudpage_menu_map import NavigationCloudPageMenuMap

class CloudPage(BasePage):
    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(CloudPage, self).__init__(driver)
        self.driver = driver
        self.nav = NavigationBasePageMenuMap(driver)
        self.intnav = NavigationCloudPageMenuMap(driver)

