import utilities.custom_logger as cl
import logging
from base.basepage import BasePage

class ActivityLoggingPage(BasePage):

    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(ActivityLoggingPage, self).__init__(driver)
        self.driver = driver

    # Locators
    _activity_log_link = "//span[contains(text(),'Activity Log')]"
    _activity_log_table_filter_list = ['Activity', 'Description', 'Status','Created Datetime']
    _select_activity_log_table_filter_item = "//div[@class='text-primary'][text()[normalize-space() = '{0}']]"
    _activity_log_text_header = "//strong[.=' Activity Log ']"
    _page_size = "//div[@class='container-fluid']/div[contains(text(),'Page Size')]"
    _filter_button = "//label[@type='text']"
    _filter_type_field = "//input[@id='filterId']"
    _fllter_clear_button = "//button[contains(text(),'Clear')]"
    _result = "//span[@class='pull-right']"

    # Vim-VnfM page related Actions/Methods
    def checkVnfmPageElementsPresence(self):
        ExpectedElements = [self._activity_log_link,self._page_size,self._filter_type_field,self._filter_button,
                            self._fllter_clear_button,self._result,
                            self._select_activity_log_table_filter_item.format(self._activity_log_table_filter_list[0]),
                            self._select_activity_log_table_filter_item.format(self._activity_log_table_filter_list[1]),
                            self._select_activity_log_table_filter_item.format(self._activity_log_table_filter_list[2]),
                            self._select_activity_log_table_filter_item.format(self._activity_log_table_filter_list[3])]

        result = self.checkElementsPresenceOnPage(ExpectedElements)
        return result

    def getNumberofMatchingResult(self):
        result = self.getText(locator=self._result, locatorType="xpath")
        return result


    def getActivityLogInfoDict(self):
        pass
