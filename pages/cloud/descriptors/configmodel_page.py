import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time
from utilities.util import Util

class ConfigModelPage(BasePage):
    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(ConfigModelPage, self).__init__(driver)
        self.driver = driver
        self.utilobj = Util()

    # Locators
    _configmodel_page_header = "//strong[.=' Configuration Data Model Management ']"
    _configmodel_table_filter_list = ['Name','Namespace','Upload Datetime']
    _select_configmodel_table_filter_item = "//div[@class='text-primary'][text()[normalize-space() = '{0}']]"

    # add configmodel related locator field
    _name_field = "//input[@id='name']"
    _select_descriptor_type = "//select[@id='descriptorType']"
    _select_data_modeltype = "//select[@id='dataModelType']"
    _vduid_field = "//input[@id='vduId']"
    _select_vdu_id = "//select[@id='vduId']"
    _select_nsd_id = "//select[@id='nsdId']"
    _select_vnfdid = "//select[@id='vnfdId']"
    _vnfType_field = "//input[@id='vnfType']"
    _buildVersion_field = "//input[@id='buildVersion']"

    _attach_button = "//main[@id='FormFields']/add-edit//input[@type='file']"
    _upload_button = "//div[@class='fileUpload btn btn-primary']/span"

    ##normalize-space()
    _data_model_name = "//table/tbody[@class='list']/tr/td[normalize-space()='{0}']"
    _del_data_model = "//table/tbody[@class='list']/tr/td[normalize-space()='{0}']/following-sibling::td/a[@id='dellink']/i"


    # configmodel page related Actions/Methods
    def checkconfigmodelPageElementsPresence(self):
        ExpectedElements = [self._configmodel_page_header, self._base_page_size, self._base_filter_type_field,
                                        self._base_filter_button,
                                        self._base_fllter_clear_button, self._base_result, self._base_action_header, self._base_add_button,
                                        self._select_configmodel_table_filter_item.format(self._configmodel_table_filter_list[0]),
                                        self._select_configmodel_table_filter_item.format(self._configmodel_table_filter_list[1]),
                                        self._select_configmodel_table_filter_item.format(self._configmodel_table_filter_list[2])]

        result = self.checkElementsPresenceOnPage(ExpectedElements)
        return result

    def enterNameInAddConfigModelNameField(self, data):
        self.sendKeysOnElement(data, self._name_field, locatorType="xpath")

    def enterVduId(self, data):
        self.sendKeysOnElement(data, self._vduid_field, locatorType="xpath")

    def selectDescriptorType(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_descriptor_type, locatorType="xpath")

    def selectNsdId(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_nsd_id, locatorType="xpath")

    def selectVnfdId(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_vnfdid, locatorType="xpath")

    def selectVduId(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_vdu_id, locatorType="xpath")

    def selectDataModeType(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_data_modeltype, locatorType="xpath")

    def enterBuildVersion(self, data):
        self.sendKeysOnElement(data, self._buildVersion_field, locatorType="xpath")

    def enterVnfType(self, data):
        self.sendKeysOnElement(data, self._vnfType_field, locatorType="xpath")

    def addConfigDatamodel(self, name, descriptortype,vduid,datamodeltype, nsdid, vnfdid,fileName):
        self.clickOnBaseAddButton()
        self.enterNameInAddConfigModelNameField(name)
        self.selectDescriptorType(descriptortype)
        if descriptortype == 'modelWithDescriptor':
            self.selectNsdId(nsdid)
            self.selectVnfdId(vnfdid)
            self.selectVduId(vduid)

        elif descriptortype == 'modelWithoutDescriptor':
            self.enterVduId(vduid)

        self.selectDataModeType(datamodeltype)
        if datamodeltype == 'modelWithSchema':
            self.mouseHoverAndElementClick(locator=self._upload_button, locatorType="xpath")
            self.util.sleep(2)
            self.utilobj.executeSikuliScript(fileName)

        self.util.sleep(2)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.waitForElement(locator=self._data_model_name.format(name), locatorType="xpath")
        status = self.isElementPresent(locator=self._data_model_name.format(name), locatorType="xpath")
        return status

    def addConfigDatamodelWithSchema(self, name, descriptortype,vduid,datamodeltype, nsdid, vnfdid,dirName,fileName):
        self.clickOnBaseAddButton()
        self.enterNameInAddConfigModelNameField(name)
        self.selectDescriptorType(descriptortype)
        if descriptortype == 'modelWithDescriptor':
            self.selectNsdId(nsdid)
            self.selectVnfdId(vnfdid)
            self.selectVduId(vduid)

        elif descriptortype == 'modelWithoutDescriptor':
            self.enterVduId(vduid)

        self.selectDataModeType(datamodeltype)
        if datamodeltype == 'modelWithSchema':
            self.mouseHoverAndElementClick(locator=self._upload_button, locatorType="xpath")
            self.util.sleep(2)
            self.utilobj.executeSikuliToUploadFileFromDirectory(dirName,fileName)

        self.util.sleep(2)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.waitForElement(locator=self._data_model_name.format(name), locatorType="xpath")
        status = self.isElementPresent(locator=self._data_model_name.format(name), locatorType="xpath")
        return status

    def addConfigDatamodelWithSchemaVnfTypeAndVer(self, name, descriptortype,vduid,datamodeltype, nsdid, vnfdid,vnftype,version,dirName,fileName):
        self.clickOnBaseAddButton()
        self.enterNameInAddConfigModelNameField(name)
        self.selectDescriptorType(descriptortype)
        if descriptortype == 'modelWithDescriptor':
            self.selectNsdId(nsdid)
            self.selectVnfdId(vnfdid)
            self.selectVduId(vduid)

        elif descriptortype == 'modelWithoutDescriptor':
            self.enterVduId(vduid)

        self.selectDataModeType(datamodeltype)
        if datamodeltype == 'modelWithSchema':
            self.mouseHoverAndElementClick(locator=self._upload_button, locatorType="xpath")
            #self.util.sleep(2)
            self.utilobj.executeSikuliToUploadFileFromDirectory(dirName,fileName)

        self.enterVnfType(vnftype)
        self.enterBuildVersion(version)
        self.util.sleep(1)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.waitForElement(locator=self._data_model_name.format(name), locatorType="xpath")
        status = self.isElementPresent(locator=self._data_model_name.format(name), locatorType="xpath")
        return status

    def addConfigDatamodelWithSchemaVnfTypeAndVerForLab(self, name, descriptortype,vduid,datamodeltype, nsdid, vnfdid,vnftype,version,dirName,fileName):
        self.clickOnBaseAddButton()
        self.enterNameInAddConfigModelNameField(name)
        self.selectDescriptorType(descriptortype)
        if descriptortype == 'modelWithDescriptor':
            self.selectNsdId(nsdid)
            self.selectVnfdId(vnfdid)
            self.selectVduId(vduid)

        elif descriptortype == 'modelWithoutDescriptor':
            self.enterVduId(vduid)

        self.selectDataModeType(datamodeltype)
        if datamodeltype == 'modelWithSchema':
            self.mouseHoverAndElementClick(locator=self._upload_button, locatorType="xpath")
            #self.util.sleep(2)
            self.utilobj.UploadProductDescriptorFileForLab(dirName,fileName)

        self.enterVnfType(vnftype)
        self.enterBuildVersion(version)
        self.util.sleep(1)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.waitForElement(locator=self._data_model_name.format(name), locatorType="xpath")
        status = self.isElementPresent(locator=self._data_model_name.format(name), locatorType="xpath")
        return status

    def deleteConfigModel(self, name):
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.waitForElement(locator=self._data_model_name.format(name), locatorType="xpath")
        status = self.isElementPresent(locator=self._data_model_name.format(name), locatorType="xpath")

        if status == True:
           self.elementClick(locator=self._del_data_model.format(name),locatorType="xpath")
           self.clickOnBaseOkButton()
        else:
            self.log.info('Config data model with name = :: '+ name + ' :: does not exists')

    def verifyAdditionOfCloudconfigmodel(self):
        pass