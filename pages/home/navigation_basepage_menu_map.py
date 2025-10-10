import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time
from pathlib import Path

class NavigationBasePageMenuMap(BasePage):

    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(NavigationBasePageMenuMap, self).__init__(driver)
        self.driver = driver

    # Locators
    _inventory_menu = '//a[@id="inventory"]'
    _blockDashboard = '//a[contains(text(),"Block Dashboard")]' # first element index0
    _blockDashboardClose = '//button[@id="BlockDashboard-close"]/i'
    _tnDashnoard = '//a[contains(text(),"TN Dashboard")]'
    _tnDashboardClose = '//button[@id="TnDashboard-close"]/i'
    _LogOutIcon = '//a/i[@title="Sign out"]'
    _close_release_note = '//button[@id="modal-cancel-btn"]'

    _serachOpen = "//div[@data-click='searchOpen']"
    _advanceSearchOpen = "//div[@id='tb_TnInventory-Table_toolbar_item_w2ui-search-advanced']/div/span"
    _selectStatusDropDownField = "//div[@class='w2ui-field-helper w2ui-list']/following-sibling::input[@placeholder='Select a Status']"
    _type_select_status = "//input[@placeholder='Select a Status']"
    _select_status = "//div[@id='w2overlay-grid_BlkInventory-Table_field_1_menu']//div[@class='menu-text']"
    
    _selectSourceDropDownField = "//div[@class='w2ui-field-helper w2ui-list']/following-sibling::input[@placeholder='Select a Source']"
    _type_source_status = "//input[@placeholder='Select a Source']"
    _select_source = "//div[@id='w2overlay-grid_BlkInventory-Table_field_5_menu']//div[@class='menu-text']"
    
    _search_button = "//button[contains(text(),'Search')]"
    
    _effective_field_coloum = "//div[@id='grid_BlkInventory-Table_columns']/table/tbody/tr/td//div[2][contains(normalize-space(.), 'Effective Date')]"
    
    _getBlockList = "//div[@id='grid_BlkInventory-Table_records']//tr[td/div[@title='{0}']]/td//a"
    _block_number_tn_field = "//tr[1]/td/input[@rel='search']"
    _requester_name_tn_field = "//tr[12]/td/input[@rel='search']"
    _tn_value = "//tr[@id='grid_TnInventory-Table_rec_1']/td[2]/div/div"
    _lata_name = "//tr[@id='grid_TnInventory-Table_rec_1']/td[9]/div"
    _custome_val = "//td[@id='grid_TnInventory-Table_data_0_17']/div/div"
    _reqester_drop_down = "//td[contains(text(),'Requester')]/following-sibling::td/select"
    
    def navigateToInventoryMenu(self):
        self.elementClick(locator=self._inventory_menu, locatorType="xpath")
     
    def clickOnSearchButton(self):
        #self.webScroll("down")
        #self.webScrollIntoViewAndClickElement(self._search_button, "xpath")
        self.executeJsToClickSearch()
        
    def clickOnEffectiveFieldCoulum(self):
        for i in range(3):
            time.sleep(2)
            self.elementClick(locator=self._effective_field_coloum, locatorType="xpath")
        
    def navigateToblockDashboardMenu(self):
        self.navigateToInventoryMenu()
        self.elementClick(locator=self._blockDashboard, locatorType="xpath")

    def navigateToTnDashboardMenu(self):
        self.navigateToInventoryMenu()
        self.elementClick(locator=self._tnDashnoard, locatorType="xpath")
        
    def closeblockDashboardMenu(self):
        self.elementClick(locator=self._blockDashboardClose, locatorType="xpath")
      
    def closeTnDashboardMenu(self):
        self.elementClick(locator=self._tnDashboardClose, locatorType="xpath")
          

    def clickOnLogoutLink(self):
        #wait = self.waitForElement(locator=self._logout_link, locatorType="xpath", pollFrequency=4)
        self.isElementDisplayed(locator=self._LogOutIcon, locatorType="xpath")
        self.isElementPresent(locator=self._LogOutIcon, locatorType="xpath")
        self.isElementEnabled(locator=self._LogOutIcon, locatorType="xpath")
        self.elementClick(locator=self._LogOutIcon, locatorType="xpath")

    def closeReleaseNote(self):
        self.isElementDisplayed(locator=self._close_release_note, locatorType="xpath")
        self.isElementPresent(locator=self._close_release_note, locatorType="xpath")
        self.isElementEnabled(locator=self._close_release_note, locatorType="xpath")
        self.elementClick(locator=self._close_release_note, locatorType="xpath")

    def logout(self):
        self.clickOnLogoutLink()
         
    def searchOpen(self):
        self.isElementDisplayed(locator=self._serachOpen, locatorType="xpath")
        self.isElementPresent(locator=self._serachOpen, locatorType="xpath")
        self.isElementEnabled(locator=self._serachOpen, locatorType="xpath")
        self.elementClick(locator=self._serachOpen, locatorType="xpath")
        
    def advancedSearchOpen(self):
        self.isElementDisplayed(locator=self._advanceSearchOpen, locatorType="xpath")
        self.isElementPresent(locator=self._advanceSearchOpen, locatorType="xpath")
        self.isElementEnabled(locator=self._advanceSearchOpen, locatorType="xpath")
        self.elementClick(locator=self._advanceSearchOpen, locatorType="xpath")
    
    def enterBlockNumberInTnField(self,block_num):
        self.isElementDisplayed(locator=self._block_number_tn_field, locatorType="xpath")
        self.isElementPresent(locator=self._block_number_tn_field, locatorType="xpath")
        self.sendKeysOnElement(block_num,locator=self._block_number_tn_field, locatorType="xpath")
  
    def enterRequesterInfoInTnField(self,requester_name):
        #self.isElementDisplayed(locator=self._requester_name_tn_field, locatorType="xpath")
        #self.isElementPresent(locator=self._requester_name_tn_field, locatorType="xpath")
        #self.sendKeysOnElement(requester_name,locator=self._requester_name_tn_field, locatorType="xpath")
        self.executeJsToFillRequester(requester_name)
        
    def getTnNumberForBlock(self):
        val = self.getText(locator=self._tn_value, locatorType="xpath")
        #print(val)
        return val
    
    def getLataNameForBlock(self):
        val = self.getText(locator=self._lata_name, locatorType="xpath")
        #print(val)
        return val

    def getCustomEForBlock(self):
        #self.getElementTextifHidden(self._custome_val)
        #time.sleep(2)
        #self.isElementDisplayed(self._custome_val)
        #self.isElementPresent(self._custome_val)
        self.webScroll(direction = "horizontal")
        time.sleep(1)
        val = self.scrollMultipleTimeToSeeHiddenElement()
        val = self.getText(locator=self._custome_val, locatorType="xpath")
        #print(val)
        return val
        
    def getTnBlockInfo(self,requester_name, masterLst):
            new_list = [str(num)[:-1] for num in masterLst]
            
            block_dict = {}
            for i, current_block in enumerate(new_list):
                tn_block = None
                lata_name = None
                custom_e = None
                
                self.navigateToTnDashboardMenu()
                time.sleep(2)
                self.advancedSearchOpen()
                time.sleep(2)

                self.enterBlockNumberInTnField(current_block)
                self.selectRequesterContainsField()
                self.enterRequesterInfoInTnField(requester_name)
                self.clickOnSearchButton()
                time.sleep(5)
                tn_block = self.getTnNumberForBlock()
                lata_name = self.getLataNameForBlock()
                custom_e = self.getCustomEForBlock()
                block_dict[masterLst[i]] = (tn_block,lata_name,custom_e)
                self.closeTnDashboardMenu()
                time.sleep(2)
                
            #print(block_dict)
            return block_dict
            
    def selectblockInventoryStatus(self,text):
        self.isElementDisplayed(locator=self._selectStatusDropDownField, locatorType="xpath")
        self.isElementPresent(locator=self._selectStatusDropDownField, locatorType="xpath")
        self.elementClick(locator=self._selectStatusDropDownField, locatorType="xpath")
        self.sendKeysOnElement(text,locator=self._selectStatusDropDownField, locatorType="xpath")
        self.sendKeysOnElement(text, locator=self._type_select_status, locatorType="xpath")
        dropdown_options = self.getElementList(locator=self._select_status, locatorType="xpath")
        for i, optionval in enumerate(dropdown_options, start=1):
            print(f"{i}. {optionval.text.strip()}")
            
        for optionval in dropdown_options:
            if optionval.text.strip() == text:   # replace with the option you want
                optionval.click()
                return True
                
        # If not found
        print(f"Option '{text}' not found in dropdown")
        return False


    def selectblockInventorySource(self,text):
        self.isElementDisplayed(locator=self._selectSourceDropDownField, locatorType="xpath")
        self.isElementPresent(locator=self._selectSourceDropDownField, locatorType="xpath")
        self.elementClick(locator=self._selectSourceDropDownField, locatorType="xpath")
        self.sendKeysOnElement(text,locator=self._selectSourceDropDownField, locatorType="xpath")
        self.sendKeysOnElement(text, locator=self._type_source_status, locatorType="xpath")
        dropdown_options = self.getElementList(locator=self._select_source, locatorType="xpath")
        for i, optionval in enumerate(dropdown_options, start=1):
            print(f"{i}. {optionval.text.strip()}")
            
        for optionval in dropdown_options:
            if optionval.text.strip() == text:   # replace with the option you want
                optionval.click()
                return True
                
        # If not found
        print(f"Option '{text}' not found in dropdown")
        return False
        
    def selectRequesterContainsField(self):
        dropdown = self.getElement(self._reqester_drop_down)

        # Scroll into view
        self.driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        #time.sleep(10)
        self.selectElementFromDropDownMenuByValue("contains", locator=self._reqester_drop_down, locatorType="xpath")
        time.sleep(1)

    def blockLstForEffectiveDate(self,effectiveDate): 
        try:
            #print('get_links_by_date')
            values = self.get_links_by_date(effectiveDate)
            return values
        except Exception as e:
            print(e)
            return None
            
    def getAllBlockListForDate(self,date_str):
        master_dict = {}
        masterLst = []
        for currentItem in ['Available','Pending','Guarded']:
            self.navigateToblockDashboardMenu()
            time.sleep(2)
            self.searchOpen()
            time.sleep(2)

            self.selectblockInventoryStatus(currentItem)

            self.selectblockInventorySource('Primary')

            self.clickOnSearchButton()
            time.sleep(5)

            self.clickOnEffectiveFieldCoulum()
            time.sleep(5)
            available_blockLst = self.blockLstForEffectiveDate(date_str)
            master_dict[currentItem] = available_blockLst
            #print(available_blockLst)
            masterLst.extend(available_blockLst)
            self.closeblockDashboardMenu()
            time.sleep(4)
         
        #print(master_dict)
        #print(masterLst)
        return master_dict, masterLst
        
    def dict_to_html_table(self,data, title="Summary Table for Number Range Testing"):
        """Convert dict to HTML table string."""
        if not data:
            return "<p>No data</p>"

        # derive headers dynamically from first tuple
        first_key = next(iter(data))
        remaining_headers = list(data[first_key])
        headers = ['Block Number', 'TN ', 'LataName', 'CustomE']

        html = [
            "<!doctype html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            f"<title>{title}</title>",
            "<style>",
            "  body { font-family: Arial, sans-serif; margin: 20px; }",
            "  table { border-collapse: collapse; width: 80%; }",
            "  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "  th { background-color: #f2f2f2; font-weight: bold; }",
            "  tr:nth-child(even) { background-color: #f9f9f9; }",
            "</style>",
            "</head><body>",
            f"<h3>{title}</h3>",
            "<table>",
            "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"
        ]

        for key, values in data.items():
            html.append("<tr>")
            html.append(f"<td>{key}</td>")
            for v in values:
                html.append(f"<td>{v}</td>")
            html.append("</tr>")

        html.append("</table></body></html>")
        return "\n".join(html)