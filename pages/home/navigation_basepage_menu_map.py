import utilities.custom_logger as cl
import logging
from base.basepage import BasePage
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NavigationBasePageMenuMap(BasePage):

    log = cl.customLoggerMethod(logging.DEBUG)

    def __init__(self, driver):
        super(NavigationBasePageMenuMap, self).__init__(driver)
        self.driver = driver

    # Locators
    # Nov 2026 portal change: Inventory (click dropdown) -> NANP (hover submenu) -> Block / TN Dashboard
    _inventory_menu = '//a[@id="inventory"]'
    # <a class="dropdown-item submenu"><span class="triangle-right">◂</span>NANP<span class="triangle-left">‣</span></a>
    _nanp_submenu = "//a[contains(@class,'dropdown-item') and contains(@class,'submenu')][contains(normalize-space(.),'NANP')]"
    _nanp_submenu_fallback = "//span[contains(@class,'triangle-right')]/parent::a[contains(normalize-space(.),'NANP')]"
    _blockDashboard = '//a[@id="main-nav-dashboard-block"]'
    _blockDashboardMaximize = '//button[@id="BlockDashboard-maximize"]'
    _blockDashboardClose = '//button[@id="BlockDashboard-close"]/i'
    _tnDashnoard = '//a[@id="main-nav-dashboard-tn"]'
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
    
    _getBlockList = "//div[@id='grid_BlkInventory-Table_records']//tr[td[@col='10']/div[@title='{0}']]/td//a"
    _block_number_tn_field = "//tr[1]/td/input[@rel='search']"
    _requester_name_tn_field = "//td[contains(text(),'Requester')]/following-sibling::td/input[@rel='search']"
    _tn_value = "//tr[@id='grid_TnInventory-Table_rec_1']/td[2]/div"
    _lata_name = "//tr[@id='grid_TnInventory-Table_rec_1']/td[9]/div"
    _custome_val = "//td[@id='grid_TnInventory-Table_data_0_17']/div/div"
    _reqester_drop_down = "//td[contains(text(),'Requester')]/following-sibling::td/select"
    
    def navigateToInventoryMenu(self):
        """Opens the Inventory dropdown (Bootstrap click toggle)."""
        wait = WebDriverWait(self.driver, 20)
        inv = wait.until(EC.element_to_be_clickable((By.XPATH, self._inventory_menu)))
        if inv.get_attribute("aria-expanded") != "true":
            inv.click()
        time.sleep(1)

    def hoverOnNanpMenu(self):
        """Hovers over the NANP submenu so Block/TN Dashboard links become visible."""
        wait = WebDriverWait(self.driver, 10)
        nanp = None
        for xp in (self._nanp_submenu, self._nanp_submenu_fallback):
            try:
                nanp = wait.until(EC.visibility_of_element_located((By.XPATH, xp)))
                break
            except Exception:
                continue
        if nanp is None:
            self.log.warning("NANP submenu not found - will try direct click on dashboard link")
            return False
        ActionChains(self.driver).move_to_element(nanp).pause(1).perform()
        return True

    def _openDashboardViaNanp(self, link_xpath, name):
        """Inventory -> hover NANP -> click dashboard link.
        Falls back to a JavaScript click if the hover menu doesn't open
        (common in headless Chrome on GitHub Actions)."""
        self.navigateToInventoryMenu()
        self.hoverOnNanpMenu()
        try:
            link = WebDriverWait(self.driver, 8).until(
                EC.visibility_of_element_located((By.XPATH, link_xpath)))
            ActionChains(self.driver).move_to_element(link).pause(0.5).click(link).perform()
            self.log.info(f"Opened {name} via Inventory > NANP menu")
        except Exception:
            self.log.warning(f"{name} link not visible after hover - using JavaScript click")
            link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, link_xpath)))
            self.driver.execute_script("arguments[0].click();", link)
        time.sleep(2)

    def clickOnSearchButton(self):
        #self.webScroll("down")
        #self.webScrollIntoViewAndClickElement(self._search_button, "xpath")
        self.executeJsToClickSearch()
        
    def clickOnEffectiveFieldCoulum(self):
        for i in range(3):
            time.sleep(2)
            self.elementClick(locator=self._effective_field_coloum, locatorType="xpath")
        
    def navigateToblockDashboardMenu(self):
        self._openDashboardViaNanp(self._blockDashboard, "Block Dashboard")

    def navigateToTnDashboardMenu(self):
        self._openDashboardViaNanp(self._tnDashnoard, "TN Dashboard")

    def maximizeblockDashboardMenu(self):
        self.elementClick(locator=self._blockDashboardMaximize, locatorType="xpath")
        
    def _closeIfOpen(self, close_xpath, name):
        """Clicks a dashboard close button only if it is on screen.
        Temporarily disables the driver's 30s implicit wait so an
        already-closed dashboard is skipped instantly instead of
        waiting ~90s per close attempt."""
        self.driver.implicitly_wait(0)
        try:
            buttons = [b for b in self.driver.find_elements(By.XPATH, close_xpath) if b.is_displayed()]
            if not buttons:
                self.log.info(f"{name} already closed - skipping close")
                return False
            buttons[0].click()
            self.log.info(f"Closed {name}")
            return True
        finally:
            self.driver.implicitly_wait(30)

    def closeblockDashboardMenu(self):
        return self._closeIfOpen(self._blockDashboardClose, "Block Dashboard")
      
    def closeTnDashboardMenu(self):
        return self._closeIfOpen(self._tnDashboardClose, "TN Dashboard")
          

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
        self.executeJsToFillRequester(requester_name, self._requester_name_tn_field)
        
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
            self.maximizeblockDashboardMenu()
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