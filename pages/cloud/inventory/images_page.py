import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time
from utilities.util import Util

class InventoryImagesPage(BasePage):
    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(InventoryImagesPage, self).__init__(driver)
        self.driver = driver
        self.utilobj = Util()

    # Locators
    _image_page_header = "//strong[.=' Image Management ']"
    _image_table_filter_list = ['Image Name', 'Tenant ID', 'Image File Path', 'Image Type','Cloud Type','Image Id','Status','Last Updated']
    _select_image_table_filter_item = "//div[@class='text-primary'][text()[normalize-space() = '{0}']]"

    # add image related locator field
    _image_name_field = "//input[@id='imageName']"
    _image_filepath_field = "//input[@id='imageFilePath']"
    _select_cloudProfileID = "//select[@id='cloudProfileID']"
    _select_image_type = "//select[@id='imageType']"
    _select_cloud_type = "//select[@id='cloudType']"

    _select_image_category ="//select[@id='imageCategory']"
    _image_ostype_field = "//input[@id='imageOSType']"
    _image_Size_field = "//input[@id='imageSize']"
    _hd_type_field = "//input[@id='hdType']"
    _hw_version_field = "//input[@id='hwVersion']"

    #_verify_image_add = "//table/tbody[@class='list']/tr/td[text()=' {0}']/following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']"
    # _image_status = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td[2]"
    # normalize-space()
    # _onboard_image_button = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td/a[@title='Onboard']"
    # _offboard_image_button = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td/a[@title='Offboard']"
    # _delete_image_button = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td/a[@id='dellink']/i"

    _verify_image_add = "//table/tbody[@class='list']/tr/td[normalize-space() ='{0}']/following-sibling::td[normalize-space() ='{1}']/following-sibling::td[normalize-space() ='{2}']"
    _image_status = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td[2]"


    _onboard_image_button = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td/a[@title='Onboard']"
    _offboard_image_button = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td/a[@title='Offboard']"
    _delete_image_button = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td/a[@id='dellink']/i"

    # vim -image page related Actions/Methods
    def checkImagePageElementsPresence(self):
        ExpectedElements = [self._image_page_header, self._base_page_size, self._base_filter_type_field,
                                        self._base_filter_button,self._base_fllter_clear_button, self._base_result,
                                        self._base_action_header, self._base_add_button,
                                        self._select_image_table_filter_item.format(self._image_table_filter_list[0]),
                                        self._select_image_table_filter_item.format(self._image_table_filter_list[1]),
                                        self._select_image_table_filter_item.format(self._image_table_filter_list[2]),
                                        self._select_image_table_filter_item.format(self._image_table_filter_list[3]),
                                        self._select_image_table_filter_item.format(self._image_table_filter_list[4]),
                                        self._select_image_table_filter_item.format(self._image_table_filter_list[5]),
                                        self._select_image_table_filter_item.format(self._image_table_filter_list[6]),
                                        self._select_image_table_filter_item.format(self._image_table_filter_list[7])]

        result = self.checkElementsPresenceOnPage(ExpectedElements)
        return result

    def enterImageName(self, data):
        self.sendKeysOnElement(data, self._image_name_field, locatorType="xpath")

    def enterImageFilePath(self, data):
        self.sendKeysOnElement(data, self._image_filepath_field, locatorType="xpath")

    def enterImageOsType(self, data):
        self.sendKeysOnElement(data, self._image_ostype_field, locatorType="xpath")

    def enterImageSize(self, data):
        self.sendKeysOnElement(data, self._image_Size_field, locatorType="xpath")

    def enterHdtype(self, data):
        self.sendKeysOnElement(data, self._hd_type_field, locatorType="xpath")

    def enterHwVersion(self, data):
        self.sendKeysOnElement(data, self._hw_version_field, locatorType="xpath")


    def selectCloudProfileId(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_cloudProfileID, locatorType="xpath")

    def selectImageType(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_image_type, locatorType="xpath")

    def selectImageCategory(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_image_category, locatorType="xpath")

    def selectCloudType(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_cloud_type, locatorType="xpath")

    def addVMwareTypeCloudImage(self, name,cloudpid, imagepath,imagetype,cloudtype,imagecategory,ostype,imagesize,hdtype,hwversion):
        self.clickOnBaseAddButton()
        self.enterImageName(name)
        self.selectCloudProfileId(cloudpid)
        self.enterImageFilePath(imagepath)
        self.selectImageType(imagetype)
        self.selectCloudType(cloudtype)
        self.selectImageCategory(imagecategory)
        self.enterImageOsType(ostype)
        self.enterImageSize(imagesize)
        self.enterHdtype(hdtype)
        self.enterHwVersion(hwversion)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath", pollFrequency=4)

    def addOpenStackTypeCloudImage(self, name,cloudpid, imagepath,imagetype,cloudtype):
        self.clickOnBaseAddButton()
        self.enterImageName(name)
        self.selectCloudProfileId(cloudpid)
        self.enterImageFilePath(imagepath)
        self.selectImageType(imagetype)
        self.selectCloudType(cloudtype)
        self.clickOnBaseAddButtonForFormFillPage()
        self.waitForElement(locator=self._base_add_button, locatorType="xpath", pollFrequency=4)

    def verifyAdditionOfCloudImage(self,name,imagetype,cloudtype):
        self.waitForElement(locator=self._base_add_button, locatorType="xpath")
        self.waitForElement(locator=self._verify_image_add.format(name,imagetype,cloudtype), locatorType="xpath")
        status = self.isElementPresent(locator=self._verify_image_add.format(name,imagetype,cloudtype),
                                       locatorType="xpath")
        return status

    def onBoardImage(self,name,imagetype,cloudtype):
            self.clickOnImageOnBoardButton(name, imagetype, cloudtype)
            self.clickOnBaseOkButton()
            self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)

    def offBoardImage(self,name,imagetype,cloudtype):
            self.clickOnImageOffBoardButton(name, imagetype, cloudtype)
            self.clickOnBaseOkButton()
            self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)

    def deleteImage(self,name,imagetype,cloudtype):
            self.clickOnImageDeleteButton(name, imagetype, cloudtype)
            self.clickOnBaseOkButton()
            self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)

    def clickOnImageDeleteButton(self,name,imagetype,cloudtype):
        self.elementClick(locator=self._delete_image_button.format(name,imagetype,cloudtype), locatorType="xpath")

    def clickOnImageOnBoardButton(self,name,imagetype,cloudtype):
        self.elementClick(locator=self._onboard_image_button.format(name,imagetype,cloudtype), locatorType="xpath")

    def clickOnImageOffBoardButton(self,name,imagetype,cloudtype):
        self.elementClick(locator=self._offboard_image_button.format(name,imagetype,cloudtype), locatorType="xpath")


    def getImageStatus(self,name,imagetype,cloudtype):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)
        self.waitForElement(locator=self._image_status.format(name,imagetype,cloudtype),locatorType="xpath", pollFrequency=4)
        self.isElementPresent(locator=self._image_status.format(name,imagetype,cloudtype),locatorType="xpath")
        status = self.getText(locator=self._image_status.format(name,imagetype,cloudtype),locatorType="xpath")
        return status

    def checkElementPresenceWithStatus(self,name,imagetype,cloudtype,status,iteration=4):
        state = False
        for i in range(iteration):
            self.clickOnBaseRefreshButton()
            self.util.sleep(2)
            #element_status = self._image_status.format(name,imagetype,cloudtype) + "[text()=' {0}']".format(status)
            element_status = self._image_status.format(name, imagetype, cloudtype) + "[normalize-space()='{0}']".format(status)

            state = self.isElementPresent(locator=element_status , locatorType="xpath")
            status2 = self.isElementEnabled(locator=element_status , locatorType="xpath")
            if state == True:
                self.log.info('Element found after :: at attempt :: ' + str(i))
                self.log.info('Element found ' + element_status + ' enable status:: ' + str(status2))
                break
            else:
                self.log.info('looking for the element ' + element_status + ' enablestatus :: '+ str(status2))
                self.log.info('Element did not found after :: at attempt :: ' + str(i))
        return state

    def verifyImageState(self,actualState,expectedState):
        status = self.utilobj.verifyTextMatch(actualState,expectedState)
        return status
