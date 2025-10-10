import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time
import os
import subprocess
from utilities.util import Util


class ConfigDataPage(BasePage):
    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(ConfigDataPage, self).__init__(driver)
        self.driver = driver
        self.utilobj = Util()

    # Locators
    _configdata_page_header = "//strong[.=' Configuration Data Management ']"
    _configdata_table_filter_list = ['Name','Data Model']
    _select_configdata_table_filter_item = "//div[@class='text-primary'][text()[normalize-space() = '{0}']]"

    # add configdata related locator field
    _name_field = "//input[@id='name']"
    _select_data_model = "//select[@id='fkDataModel']"
    _attach_file_button = "//div[@class='fileUpload btn btn-primary']"
    _data_name = "//table/tbody[@class='list']/tr/td[normalize-space()='{0}']"
    _del_data = "//table/tbody[@class='list']/tr/td[normalize-space()='{0}']/following-sibling::td/a[@id='dellink']/i"

    # configdata page related Actions/Methods

    def checkconfigdataPageElementsPresence(self):
        ExpectedElements = [self._configdata_page_header, self._base_page_size, self._base_filter_type_field,
                                        self._base_filter_button,
                                        self._base_fllter_clear_button, self._base_result, self._base_action_header, self._base_add_button,
                                        self._select_configdata_table_filter_item.format(self._configdata_table_filter_list[0]),
                                        self._select_configdata_table_filter_item.format(self._configdata_table_filter_list[1])]

        result = self.checkElementsPresenceOnPage(ExpectedElements)
        return result

    def enterNameInAddconfigdataNameField(self, data):
        self.sendKeysOnElement(data, self._name_field, locatorType="xpath")

    def sendkeysafterAttachfilebutton(self,filename):
        self.isElementPresent(locator=self._attach_file_button, locatorType="xpath")
        self.elementClick(locator=self._attach_file_button, locatorType="xpath")
        time.sleep(2)
        self.sendKeysOnElement(filename,locator=self._attach_file_button, locatorType="xpath")

    def selectDataModel(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_data_model, locatorType="xpath")

    def enterAttachedfileNameinFileNameField(self,filename):
        self.JSExecuteAttachedFile(filename)

    def clickOnAttachedButton(self):
        self.elementClick(locator=self._attach_file_button, locatorType="xpath")

    def addConfigDataMangement(self, name,datmodel,fileName,dirName=None):
        self.clickOnBaseAddButton()
        self.enterNameInAddconfigdataNameField(name)
        self.selectDataModel(datmodel)
        self.clickOnAttachedButton()
        self.util.sleep(2)
        if dirName != None:
            self.utilobj.executeSikuliToUploadFileFromDirectory(dirName,fileName)
        else:
            self.utilobj.executeSikuliScript(fileName)
        self.util.sleep(2)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.filterByName(name)
        self.waitForElement(locator=self._data_name.format(name), locatorType="xpath")
        self.waitForElement(locator=self._data_name.format("Snapshot-"+name), locatorType="xpath")
        status = self.isElementPresent(locator=self._data_name.format(name), locatorType="xpath")
        status1 = self.isElementPresent(locator=self._data_name.format("Snapshot-"+name), locatorType="xpath")
        finalstatus = status and status1
        return finalstatus

    def addConfigDataMangementForLab(self, name,datmodel,fileName,dirName=None):
        self.clickOnBaseAddButton()
        self.enterNameInAddconfigdataNameField(name)
        self.selectDataModel(datmodel)
        self.clickOnAttachedButton()
        self.util.sleep(2)
        if dirName != None:
            self.utilobj.UploadProductDescriptorFileForLab(dirName,fileName)
        else:
            self.utilobj.executeSikuliScript(fileName)
        self.util.sleep(2)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.filterByName(name)
        self.waitForElement(locator=self._data_name.format(name), locatorType="xpath")
        self.waitForElement(locator=self._data_name.format("Snapshot-"+name), locatorType="xpath")
        status = self.isElementPresent(locator=self._data_name.format(name), locatorType="xpath")
        status1 = self.isElementPresent(locator=self._data_name.format("Snapshot-"+name), locatorType="xpath")
        finalstatus = status and status1
        return finalstatus

    def deleteConfigData(self, name):
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.waitForElement(locator=self._data_name.format(name), locatorType="xpath")
        #self.waitForElement(locator=self._data_name.format("Snapshot-" + name), locatorType="xpath")
        status = self.isElementPresent(locator=self._data_name.format(name), locatorType="xpath")
        status = self.isElementPresent(locator=self._data_name.format(name), locatorType="xpath")
        #status1 = self.isElementPresent(locator=self._data_name.format("Snapshot-"+name), locatorType="xpath")
        finalstatus = status #and status1

        if finalstatus == True:
           self.elementClick(locator=self._del_data.format(name),locatorType="xpath")
           self.clickOnBaseOkButton()
           time.sleep(1)
           #self.elementClick(locator=self._del_data.format("Snapshot-"+name), locatorType="xpath")
           #self.clickOnBaseOkButton()
        else:
            self.log.info('Config data with name = :: '+ name + ' :: does not exists')

    def verifyAdditionOfCloudconfigdata(self):
        pass
