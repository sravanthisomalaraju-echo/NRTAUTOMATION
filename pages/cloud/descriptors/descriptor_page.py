import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time
import subprocess
from utilities.util import Util
import pytest

class DescriptorPage(BasePage):
    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(DescriptorPage, self).__init__(driver)
        self.driver = driver
        self.utilobj = Util()

    # Locators
    _descriptor_page_header = "//strong[.=' Descriptor ']"
    _upload_button = "//div[@class='fileUpload btn btn-primary btn-sm']"

    _select_template = "//select[@name='type']"
    _confirm_upload_header = "//h4[contains(text(),'Confirm')]"
    _select_descriptor = "//select[@name='type']"
    _select_nsd_type = "//div[contains(text(),'NSD')]/following-sibling::select"
    _select_vnfd_type = "//div[contains(text(),'VNFD')]/following-sibling::select"
    _select_tenant_to_be_terminate = "//select[@name='cloudProfileId']"
    _select_tenant_to_be_deployed = "//select[@id='fkcloud_tenant_config']"
    _select_prefered_vnfm = "//select[@id='fkvnfm_config']"

    _descriptor_table_filter_list = ['Name','Descriptor Id','Parent Descriptor Id', 'Type','Version','Upload Datetime','Cloud NS Id','Status','Deploy Type','Last Updated']
    _select_descriptor_table_filter_item = "//div[@class='text-primary'][text()[normalize-space() = '{0}']]"

    _terminate_confirmation_msg = "//div[contains(text(),'Are you sure you want to terminate {0}?')]"
    _select_tenant_terminate_msg = "//p[contains(text(),'Please select a tenant to terminate')]"
    _terminate_confirm_button = "//button[contains(text(),'Terminate')]"
    #normalize-space()
    _descriptor_onboard_button_wo_version = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td/a[@title='Onboard']/i"
    _descriptor_offboard_button_wo_version = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td/a[@title='Offboard']/i"
    _descriptor_delete_button_wo_version = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td/a[@id='dellink']/i"
    _descriptor_onboard_button = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td/a[@title='Onboard']/i"
    _descriptor_deploy_button = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']//following-sibling::td/a[@title='Deploy']/i"
    _descriptor_offboard_button_with_version = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td/a[@title='Offboard']/i"
    _descriptor_delete_button_with_version = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td/a[@id='dellink']/i"

    _expFirstElement = "//td[normalize-space()='{0}']/a/i[@title='TOGGLE_EXPAND' and @class='fa fa-plus']"
    _expNextItem = "//td[normalize-space() ='{0}']/following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/preceding-sibling::td[4]/a/i[@class='fa fa-plus']"
    _desc_status = "//td[normalize-space() ='{0}']/following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td[3]"
    _desc_deploy_type = "//td[normalize-space() ='{0}']/following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td[4]"
    _desc_deploy_button = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td/a[@title='Deploy']/i"

    #
    #_descriptor_onboard_button_wo_version = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td/a[@title='Onboard']/i"
    #_descriptor_offboard_button_wo_version = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td/a[@title='Offboard']/i"
    #_descriptor_delete_button_wo_version = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td/a[@id='dellink']/i"
    #_descriptor_onboard_button = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td/a[@title='Onboard']/i"
    #_descriptor_deploy_button = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']//following-sibling::td/a[@title='Deploy']/i"
    #_descriptor_offboard_button_with_version = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td/a[@title='Offboard']/i"
    #_descriptor_delete_button_with_version = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td/a[@id='dellink']/i"

    #_expFirstElement = "//td[text()=' {0}']/a/i[@title='TOGGLE_EXPAND' and @class='fa fa-plus']"
    #_expNextItem = "//td[text() =' {0}']/following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/preceding-sibling::td[4]/a/i[@class='fa fa-plus']"
    #_desc_status = "//td[text() =' {0}']/following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td[3]"
    #_desc_deploy_type = "//td[text() =' {0}']/following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td[4]"
    #_desc_deploy_button = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td/a[@title='Deploy']/i"
    #_des_deploy_confirm_button = "//button[contains(text(),'Deploy')]"

    _des_terminate_button = "//td[normalize-space() ='{0}']//following-sibling::td[normalize-space()='{1}']/following-sibling::td[normalize-space()='{2}']/following-sibling::td/a[@title='Terminate']/i[@class='fa fa-power-off  infinite rotateIn']"

    # _upload_state = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']/following-sibling::td[text()=' {2}']/following-sibling::td[text()=' {3}']"
    # _ download_descriptor_button = "//td[text() =' {0}']//following-sibling::td[text()=' {1}']//following-sibling::td/a[@title='Download']/i[@class='fa fa-download infinite tada']"

    ###
    # descriptor page related Actions/Methods

    def checkdescriptorPageElementsPresence(self):
        ExpectedElements = [self._descriptor_page_header, self._base_page_size, self._base_filter_type_field,
                                        self._base_filter_button,
                                        self._base_fllter_clear_button, self._base_result, self._base_action_header,
                                        self._select_descriptor_table_filter_item.format(self._descriptor_table_filter_list[0]),
                                        self._select_descriptor_table_filter_item.format(self._descriptor_table_filter_list[1]),
                                        self._select_descriptor_table_filter_item.format(self._descriptor_table_filter_list[2]),
                                        self._select_descriptor_table_filter_item.format(self._descriptor_table_filter_list[3]),
                                        self._select_descriptor_table_filter_item.format(self._descriptor_table_filter_list[4]),
                                        self._select_descriptor_table_filter_item.format(self._descriptor_table_filter_list[5]),
                                        self._select_descriptor_table_filter_item.format(self._descriptor_table_filter_list[6]),
                                        self._select_descriptor_table_filter_item.format(self._descriptor_table_filter_list[7])]

        result = self.checkElementsPresenceOnPage(ExpectedElements)
        return result

    def selectDescriptorType(self,data):
        self.selectElementFromDropDownMenuByVisibleText(data,self._select_descriptor, locatorType="xpath")

    def selectNSDType(self,data):
        self.selectElementFromDropDownMenuByVisibleText(data,self._select_nsd_type, locatorType="xpath")

    def selectVNFDType(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_vnfd_type, locatorType="xpath")

    def selectTenantName(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_tenant_to_be_deployed, locatorType="xpath")

    def selectTenantToBeTerminate(self, data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_tenant_to_be_terminate, locatorType="xpath")

    def selectPreferredVnfm(self,data):
        self.selectElementFromDropDownMenuByVisibleText(data, self._select_prefered_vnfm, locatorType="xpath")

    def clickOnTerimanteConfirmButton(self):
        self.elementClick(locator=self._terminate_confirm_button, locatorType="xpath")

    def clickOnUploadButtonOndescriptorPage(self):
        self.waitForElement(locator=self._upload_button, locatorType="xpath", pollFrequency=4)
        status = self.isElementDisplayed(locator=self._upload_button, locatorType="xpath")
        for i in range(2):
            if status == False:
                self.waitForElement(locator=self._upload_button, locatorType="xpath", pollFrequency=4)
            else:
                self.isElementEnabled(locator=self._upload_button, locatorType="xpath")
                break
        self.elementClick(locator=self._upload_button, locatorType="xpath")

    def uploadNSDDescriptor(self,descriptorType='NSD',filePath=''):
        self.clickOnUploadButtonOndescriptorPage()
        self.util.sleep(2)
        self.utilobj.executeSikuliScript(filePath)
        self.waitForElement(locator=self._confirm_upload_header, locatorType="xpath", pollFrequency=4)

    def checkExpansionForParentDescriptorNode(self,descriptorName):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)
        self.waitForElement(locator=self._expFirstElement.format(descriptorName),locatorType="xpath")
        status = self.isElementPresent(locator=self._expFirstElement.format(descriptorName),locatorType="xpath")
        return status

    def expandAllDescriptorNodes(self,items):
        self.clickOnBaseRefreshButton()
        count = len(items)
        print('number of items in the expansion list=' + str(count))
        status = self.checkExpansionForParentDescriptorNode(items[0])
        if status == True:
            self.elementClick(locator=self._expFirstElement.format(items[0]),locatorType="xpath")
            #self.util.sleep(2)
            self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)
        try:
            for i in range(1,count):
                if items[i] is not "None":
                    currentDescriptorList = items[i].split(",")
                    descriptorName = currentDescriptorList[0]
                    descriptorType = currentDescriptorList[1]
                    descriptorVersion = currentDescriptorList[2]
                    print('Current Descriptor to be expanded name :: ' + descriptorName + ' :: type :: ' + descriptorType + ' :: version :: ' + descriptorVersion )
                    self.waitForElement(locator=self._expNextItem.format(descriptorName,descriptorType,descriptorVersion), locatorType="xpath")
                    status1 = self.isElementPresent(locator=self._expNextItem.format(descriptorName,descriptorType,descriptorVersion), locatorType="xpath")
                    if status1 == True:
                        print('Element to be expanded ::' + self._expNextItem.format(descriptorName,descriptorType,descriptorVersion))
                        self.elementClick(locator=self._expNextItem.format(descriptorName,descriptorType,descriptorVersion), locatorType="xpath")
                        #self.util.sleep(2)
                        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)
                    else:
                        print("Element did not get expanded, May be already expanded :: " + self._expNextItem.format(descriptorName,descriptorType,descriptorVersion))
                else:
                    print('no more expansion required..')
        except:
            print('Exception occcured while expanding the elements')

    def uploadDescriptorFile(self,descriptorType,nsdType="--Select NSD--",vnfdType = "--Select VNFD--",fileName=''):
        self.clickOnUploadButtonOndescriptorPage()
        self.util.sleep(1)
        self.utilobj.executeSikuliScript(fileName)
        self.waitForElement(locator=self._confirm_upload_header, locatorType="xpath", pollFrequency=4)
        if descriptorType == "NSD":
            self.selectDescriptorType(descriptorType)
        elif descriptorType == "LVND" or descriptorType == "VNFD" or descriptorType == "VLD":
            self.selectDescriptorType(descriptorType)
            self.util.sleep(1)
            self.selectNSDType(nsdType)
        elif descriptorType == "LCMD":
            self.selectDescriptorType(descriptorType)
            self.util.sleep(1)
            self.selectVNFDType(vnfdType)
        self.util.sleep(1)
        self.clickOnBaseUploadConfirmButton()

    def uploadDescriptorFileFromDirectory(self,descriptorType,nsdType="--Select NSD--",vnfdType = "--Select VNFD--",dirName='',fileName='',tenantName=''):
        self.clickOnUploadButtonOndescriptorPage()
        #self.util.sleep(3)
        self.utilobj.executeSikuliToUploadFileFromDirectory(dirName,fileName)
        self.waitForElement(locator=self._confirm_upload_header, locatorType="xpath", pollFrequency=4)
        if descriptorType == "NSD":
            self.selectDescriptorType(descriptorType)
            self.selectTenantToBeTerminate(tenantName)
        elif descriptorType == "LVND" or descriptorType == "VNFD" or descriptorType == "VLD":
            self.selectDescriptorType(descriptorType)
            self.selectNSDType(nsdType)
        elif descriptorType == "LCMD":
            self.selectDescriptorType(descriptorType)
            self.selectVNFDType(vnfdType)
        #self.util.sleep(3)
        self.clickOnBaseUploadConfirmButton()

    def uploadProductDescriptorFileForLab(self,descriptorType,nsdType="--Select NSD--",vnfdType = "--Select VNFD--",dirName='',fileName='',tenantName=''):
        self.clickOnUploadButtonOndescriptorPage()
        #self.util.sleep(3)
        self.utilobj.UploadProductDescriptorFileForLab(dirName,fileName)
        self.waitForElement(locator=self._confirm_upload_header, locatorType="xpath", pollFrequency=4)
        if descriptorType == "NSD":
            self.selectDescriptorType(descriptorType)
            self.selectTenantToBeTerminate(tenantName)
        elif descriptorType == "LVND" or descriptorType == "VNFD" or descriptorType == "VLD":
            self.selectDescriptorType(descriptorType)
            self.selectNSDType(nsdType)
        elif descriptorType == "LCMD":
            self.selectDescriptorType(descriptorType)
            self.selectVNFDType(vnfdType)
        #self.util.sleep(3)
        self.clickOnBaseUploadConfirmButton()

    def uploadDescriptorZipFileForLab(self,dirName,fileName,tenantName=''):
        self.clickOnUploadButtonOndescriptorPage()
        self.utilobj.UploadProductDescriptorFileForLab(dirName,fileName)
        self.waitForElement(locator=self._confirm_upload_header, locatorType="xpath", pollFrequency=4)
        self.selectTenantToBeTerminate(tenantName)
        self.clickOnBaseUploadConfirmButton()

    def verifyDescriptorState(self,actualState,expectedState):
        status = self.utilobj.verifyTextMatch(actualState,expectedState)
        return status

    def getDescriptorStateFinal(self,descriptorName,version,descriptorType):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)
        self.waitForElement(locator=self._desc_status.format(descriptorName, descriptorType,version),
                            locatorType="xpath", pollFrequency=4)
        status = self.isElementPresent(locator=self._desc_status.format(descriptorName, descriptorType,version),
                              locatorType="xpath")
        if status == True:
            state = self.getText(locator=self._desc_status.format(descriptorName, descriptorType,version),
                         locatorType="xpath")
        else:
            state = "None"

        return state

    def getDescriptorDeploTypeFinalNew(self,descriptorName,version,descriptorType):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)
        self.waitForElement(locator=self._desc_deploy_type.format(descriptorName, descriptorType,version),
                            locatorType="xpath", pollFrequency=4)
        status = self.isElementPresent(locator=self._desc_deploy_type.format(descriptorName, descriptorType,version),
                              locatorType="xpath")
        if status == True:
            state = self.getText(locator=self._desc_deploy_type.format(descriptorName, descriptorType,version),
                         locatorType="xpath")
        else:
            state = "None"

        return state

    def clickOnBoardDescriptorButton(self,descriptorName,version,descriptorType):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=2)
        try:
            if version == "None" or version == None:
                self.waitForElement(locator=self._descriptor_onboard_button_wo_version.format(descriptorName, descriptorType),
                                locatorType="xpath")
                status = self.isElementPresent(locator=self._descriptor_onboard_button_wo_version.format(descriptorName, descriptorType))
                status2 = self.isElementEnabled(locator=self._descriptor_onboard_button_wo_version.format(descriptorName, descriptorType))
                print('element presence status :: ' + str(status) + ' :: enable status :: ' + str(status2))
                if status == True :
                    self.elementClick(locator=self._descriptor_onboard_button_wo_version.format(descriptorName, descriptorType),
                              locatorType="xpath")
            else:
                self.waitForElement(locator=self._descriptor_onboard_button.format(descriptorName, descriptorType,version), locatorType="xpath")
                status = self.isElementPresent(
                    locator=self._descriptor_onboard_button.format(descriptorName, descriptorType,version))
                status2 = self.isElementEnabled(
                    locator=self._descriptor_onboard_button.format(descriptorName, descriptorType,version))
                print('element presence status :: ' + str(status) + ' :: enable status :: ' + str(status2))

                if status == True:
                    self.elementClick(locator=self._descriptor_onboard_button.format(descriptorName, descriptorType,version), locatorType="xpath")
                else:
                    self.log.info(':: --> onboard button did not found <-- ::' + self._descriptor_onboard_button.format(descriptorName, descriptorType,version) )
        except:
            self.log.info("!!! Exception occured !!! onboard of descriptor did not work !!! ")

    def onBoardDescriptorsFinal(self,descriptorName,version,descriptorType):
        self.log.info('##### Started Descriptor :: OnBoarding  :: '+ descriptorName + ' :: descriptorType :: '+ descriptorType)
        self.util.sleep(1)
        self.clickOnBoardDescriptorButton(descriptorName,version,descriptorType)
        self.util.sleep(1)
        self.clickOnBaseOkButton()
        self.util.sleep(1)
        self.log.info('##### Completed Descriptor :: OnBoarding  :: ' + descriptorName + ' :: descriptorType :: ' + descriptorType)
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)
        self.util.sleep(2)

    def clickOnDeployButton(self):
        self.elementClick(locator=self._des_deploy_confirm_button, locatorType="xpath")

    def DeployDescriptorFinal(self,descriptorName,version,descriptorType,tenantName):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=2)
        self.waitForElement(locator=self._desc_deploy_button.format(descriptorName,descriptorType,version), locatorType="xpath", pollFrequency=2)
        status = self.isElementPresent(locator=self._desc_deploy_button.format(descriptorName,descriptorType,version), locatorType="xpath")
        status2 = self.isElementEnabled(locator=self._desc_deploy_button.format(descriptorName, descriptorType, version),locatorType="xpath")
        print('Deploy Descriptor Button status :: ' + str(status) + ' :: enabled status :: '+ str(status2))
        if status == True:
            self.elementClick(locator=self._desc_deploy_button.format(descriptorName,descriptorType,version), locatorType="xpath")
        else:
            self.log.info('Deploy Button not found :: ' + self._desc_deploy_button.format(descriptorName,descriptorType,version))

        self.waitForElement(locator=self._des_deploy_confirm_button,locatorType="xpath")
        self.isElementDisplayed(locator=self._des_deploy_confirm_button, locatorType="xpath")
        self.selectTenantName(tenantName)
        self.clickOnDeployButton()
        time.sleep(4)


    def DeployDescriptorWithPreferedVNFMFinalOld(self, descriptorName, version, descriptorType, tenantName, preferredVnfm):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=2)
        self.waitForElement(locator=self._desc_deploy_button.format(descriptorName, descriptorType, version),
                            locatorType="xpath", pollFrequency=2)
        status = self.isElementPresent(locator=self._desc_deploy_button.format(descriptorName, descriptorType, version),
                                       locatorType="xpath")
        status2 = self.isElementEnabled(
            locator=self._desc_deploy_button.format(descriptorName, descriptorType, version), locatorType="xpath")
        print('Deploy Descriptor Button status :: ' + str(status) + ' :: enabled status :: ' + str(status2))
        if status == True:
            self.elementClick(locator=self._desc_deploy_button.format(descriptorName, descriptorType, version),
                              locatorType="xpath")
        else:
            self.log.info(
                'Deploy Button not found :: ' + self._desc_deploy_button.format(descriptorName, descriptorType,
                                                                                version))

        self.waitForElement(locator=self._des_deploy_confirm_button, locatorType="xpath")
        self.isElementDisplayed(locator=self._des_deploy_confirm_button, locatorType="xpath")
        self.selectTenantName(tenantName)
        self.selectPreferredVnfm(preferredVnfm)
        self.clickOnDeployButton()
        time.sleep(4)

    ### deploy confirmation popup comes into picture
    def DeployDescriptorFinalNew(self, descriptorName, version, descriptorType):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=2)
        self.waitForElement(locator=self._desc_deploy_button.format(descriptorName, descriptorType, version),
                            locatorType="xpath", pollFrequency=2)
        status = self.isElementPresent(locator=self._desc_deploy_button.format(descriptorName, descriptorType, version),
                                       locatorType="xpath")
        status2 = self.isElementEnabled(
            locator=self._desc_deploy_button.format(descriptorName, descriptorType, version), locatorType="xpath")
        print('Deploy Descriptor Button status :: ' + str(status) + ' :: enabled status :: ' + str(status2))
        if status == True:
            self.elementClick(locator=self._desc_deploy_button.format(descriptorName, descriptorType, version),
                              locatorType="xpath")
        else:
            self.log.info(
                'Deploy Button not found :: ' + self._desc_deploy_button.format(descriptorName, descriptorType,
                                                                                version))
        self.clickOnBaseOkButton()

    def checkElementPresenceWithStatus(self,descriptorName, descriptorType, version,status,iteration=6):
        state = False
        for i in range(iteration):
            self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=2)
            self.elementClick(locator=self._base_refresh_button, locatorType="xpath")
            self.util.sleep(2)
            element_status = self._desc_status.format(descriptorName, descriptorType, version) + "[normalize-space()='{0}']".format(status)
            self.waitForElement(locator=element_status,locatorType="xpath", pollFrequency=4)
            state = self.isElementPresent(locator=element_status , locatorType="xpath")
            status2 = self.isElementEnabled(locator=element_status , locatorType="xpath")
            if state == True:
                self.log.info('Element found after :: ' + str(int(i * 2)) + ' :: seconds at attempt :: ' + str(i) + ' with status :: ' +  status)
                self.log.info('Element found ' + element_status + ' enable status:: ' + str(status2))
                break
            else:
                self.log.info('looking for the element ' + element_status + ' enablestatus :: '+ str(status2))
                self.log.info('Element did not found after :: ' + str(int(i * 2)) + ' :: seconds at attempt :: ' + str(i) + ' with status :: ' +  status)
        return state

    def checkElementPresenceWithDeployType(self,descriptorName, descriptorType, version,status,iteration=6):
        state = False
        for i in range(iteration):
            self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=2)
            self.elementClick(locator=self._base_refresh_button, locatorType="xpath")
            self.util.sleep(2)
            #element_status = self._desc_deploy_type.format(descriptorName, descriptorType, version) + "[text()=' {0}']".format(status)
            element_status = self._desc_deploy_type.format(descriptorName, descriptorType,
                                                           version) + "[normalize-space()='{0}']".format(status)

            self.waitForElement(locator=element_status,locatorType="xpath", pollFrequency=4)
            state = self.isElementPresent(locator=element_status , locatorType="xpath")
            status2 = self.isElementEnabled(locator=element_status , locatorType="xpath")
            if state == True:
                self.log.info('Element found after :: ' + str(int(i * 2)) + ' :: seconds at attempt :: ' + str(i) + ' with status :: ' +  status)
                self.log.info('Element found ' + element_status + ' enable status:: ' + str(status2))
                break
            else:
                self.log.info('looking for the element ' + element_status + ' enablestatus :: '+ str(status2))
                self.log.info('Element did not found after :: ' + str(int(i * 2)) + ' :: seconds at attempt :: ' + str(i) + ' with status :: ' +  status)
        return state

    def TerminateDescriptorFinal(self,descriptorName,version,descriptorType,tenantName):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=2)

        deployTypeState = self.getDescriptorDeploTypeFinalNew(descriptorName, version, descriptorType)

        if deployTypeState != "PRE_PRODUCTION":
            self.waitForElement(locator=self._des_terminate_button.format(descriptorName,descriptorType,version), locatorType="xpath", pollFrequency=2)
            status = self.isElementPresent(locator=self._des_terminate_button.format(descriptorName,descriptorType,version), locatorType="xpath")
            status2 = self.isElementEnabled(locator=self._des_terminate_button.format(descriptorName, descriptorType, version),locatorType="xpath")
            print('terminate Descriptor Button status :: ' + str(status) + ' :: enabled status :: '+ str(status2))
            if status == True:
                self.elementClick(locator=self._des_terminate_button.format(descriptorName,descriptorType,version), locatorType="xpath")
            else:
                self.log.info('terminate Button not found :: ' + self._des_terminate_button.format(descriptorName,descriptorType,version))

            self.waitForElement(locator=self._terminate_confirmation_msg.format(descriptorName), locatorType="xpath",
                            pollFrequency=2)
            self.clickOnBaseOkButton()

            ''' commeted below 3 lines as no tenant need to be selected
            #self.waitForElement(locator=self._select_tenant_terminate_msg, locatorType="xpath", pollFrequency=2)
            #self.selectTenantToBeTerminate(tenantName)
            #self.clickOnTerimanteConfirmButton()'''

        else:
            self.log.info('\n\n :: '+ descriptorName + ' :: '  +version + ' :: '+ descriptorType + ' :: IS ALREADY TERMINATED  :: \n and \t Its DeployState == ' + deployTypeState + '\n')


    def offBoardDescriptorsFinalNew(self,descriptorName,version,descriptorType):
        self.util.sleep(1)
        self.log.info('\n\t ##### Started Descriptor :: OffBoarding  :: '+ descriptorName + ' :: descriptorType :: '+ descriptorType + '\t\n')
        offboardState = self.getDescriptorStateFinal(descriptorName, version, descriptorType)
        if offboardState != "Deleted":
            self.clickOffBoardDescriptorButton(descriptorName,version,descriptorType)
            self.clickOnBaseOkButton()
            self.util.sleep(1)
            self.log.info('\n\t ##### Completed Descriptor :: OffBoarding  :: ' + descriptorName + ' :: descriptorType :: ' + descriptorType + '\t\n')
            self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=4)
        else:
            self.log.info(
                '\n\n :: ' + descriptorName + ' :: ' + version + ' :: ' + descriptorType + ' :: IS ALREADY OFF-BOARDED  :: \n and \t Its offboard State == ' + offboardState + '\n')

    def clickOffBoardDescriptorButton(self,descriptorName,version,descriptorType):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=2)
        try:
            if version == "None" or version == None:
                self.waitForElement(locator=self._descriptor_offboard_button_wo_version.format(descriptorName, descriptorType),
                                locatorType="xpath",maxtimeout=20,pollFrequency=4)
                status = self.isElementPresent(locator=self._descriptor_offboard_button_wo_version.format(descriptorName, descriptorType))
                status2 = self.isElementEnabled(locator=self._descriptor_offboard_button_wo_version.format(descriptorName, descriptorType))
                print('element presence status :: ' + str(status) + ' :: enable status :: ' + str(status2))
                if status == True :
                    self.elementClick(locator=self._descriptor_offboard_button_wo_version.format(descriptorName, descriptorType),
                              locatorType="xpath")
                else:
                    self.log.info(':: --> offboard button did not found <-- ::' + self._descriptor_offboard_button_wo_version.format(descriptorName, descriptorType))
            else:
                self.waitForElement(locator=self._descriptor_offboard_button_with_version.format(descriptorName, descriptorType,version), locatorType="xpath",maxtimeout=20,pollFrequency=4)
                status = self.isElementPresent(
                    locator=self._descriptor_offboard_button_with_version.format(descriptorName, descriptorType,version))
                status2 = self.isElementEnabled(
                    locator=self._descriptor_offboard_button_with_version.format(descriptorName, descriptorType,version))
                print(self._descriptor_offboard_button_with_version.format(descriptorName, descriptorType,version) + 'element presence status :: ' + str(status) + ' :: enable status :: ' + str(status2))

                if status == True:
                    self.elementClick(locator=self._descriptor_offboard_button_with_version.format(descriptorName, descriptorType,version), locatorType="xpath")
                    self.util.sleep(1)
                    self.elementClick(locator=self._base_refresh_button, locatorType="xpath")
                    self.util.sleep(1)
                else:
                    self.log.info(':: --> offboard button did not found <-- ::' + self._descriptor_offboard_button_with_version.format(descriptorName, descriptorType,version) )
        except:
            self.log.info("!!! Exception occured !!! offboard of descriptor did not work !!! ")

    def clickOnDeleteDescriptorButton(self,descriptorName,version,descriptorType):
        self.waitForElement(locator=self._base_refresh_button, locatorType="xpath", pollFrequency=2)
        try:
            if version == "None" or version == None:
                self.waitForElement(locator=self._descriptor_delete_button_wo_version.format(descriptorName, descriptorType),
                                locatorType="xpath",maxtimeout=20,pollFrequency=4)
                status = self.isElementPresent(locator=self._descriptor_delete_button_wo_version.format(descriptorName, descriptorType))
                status2 = self.isElementEnabled(locator=self._descriptor_delete_button_wo_version.format(descriptorName, descriptorType))
                print('element presence status :: ' + str(status) + ' :: enable status :: ' + str(status2))
                if status == True :
                    self.elementClick(locator=self._descriptor_delete_button_wo_version.format(descriptorName, descriptorType),
                              locatorType="xpath")
            else:
                self.waitForElement(locator=self._descriptor_delete_button_with_version.format(descriptorName, descriptorType,version), locatorType="xpath",maxtimeout=20,pollFrequency=4)
                status = self.isElementPresent(
                    locator=self._descriptor_delete_button_with_version.format(descriptorName, descriptorType,version))
                status2 = self.isElementEnabled(
                    locator=self._descriptor_delete_button_with_version.format(descriptorName, descriptorType,version))
                print('element presence status :: ' + str(status) + ' :: enable status :: ' + str(status2))

                if status == True:
                    self.elementClick(locator=self._descriptor_delete_button_with_version.format(descriptorName, descriptorType,version), locatorType="xpath")
                    self.util.sleep(1)
                    self.elementClick(locator=self._base_refresh_button, locatorType="xpath")
                else:
                    self.log.info(':: --> delete button did not found <-- ::' + self._descriptor_delete_button_with_version.format(descriptorName, descriptorType,version) )
        except:
            self.log.info("!!! Exception occured !!! deletion of descriptor did not work !!! ")

    def deleteDescriptorsFinalNew(self, descriptorName, version, descriptorType):
        self.log.info(
            '##### Started Descriptor :: Deletion  :: ' + descriptorName + ' :: descriptorType :: ' + descriptorType)
        self.util.sleep(2)
        self.clickOnDeleteDescriptorButton(descriptorName, version, descriptorType)
        self.clickOnBaseOkButton()
        self.log.info(
            '##### Completed Descriptor :: Deletion  :: ' + descriptorName + ' :: descriptorType :: ' + descriptorType)


    def getDescriptorElementPresence(self,descriptorName,version,descriptorType):
        status = self.isElementPresent(
            locator=self._descriptor_delete_button_with_version.format(descriptorName, descriptorType, version))
        return status
