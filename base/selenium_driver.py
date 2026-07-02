from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from traceback import print_stack
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.support.select import Select
import utilities.custom_logger as cl
import logging
import os
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.file_detector import LocalFileDetector

class SeleniumDriver():
    log = cl.customLoggerMethod(logging.DEBUG)
    # to resolve TypeError: super() argument 1 must be type, not classobj inpython 2.7 ##add the below line of code
    __metaclass__ = type

    def __init__(self, driver):
        self.driver = driver

    def getByType(self,locatorType):
        locatorType = locatorType.lower()
        if locatorType == 'id':
            return By.ID
        elif locatorType == 'name':
            return By.NAME
        elif locatorType == 'xpath':
            return By.XPATH
        elif locatorType == 'classname':
            return By.CLASS_NAME
        elif locatorType == 'cssselector':
            return By.CSS_SELECTOR
        elif locatorType == 'linktext':
            return By.LINK_TEXT
        elif locatorType == 'partiallinktext':
            return By.PARTIAL_LINK_TEXT
        elif locatorType == 'tagname':
            return By.TAG_NAME
        else:
            #print("locatortype --> "+ locatorType + "not correct/ supported")
            self.log.info("locatortype --> "+ locatorType + "not correct/ supported")
        return False

    def getElement(self,locator,locatorType="xpath"):
        element = None
        try:
            locatorType = locatorType.lower()
            byType = self.getByType(locatorType)
            element = self.driver.find_element(byType,locator)
            self.log.info("Element found with locator : "+ locator + "and locatortype : "+byType)
        except:
            self.log.error("Element not found with locator : " + locator + "and locatortype : " + byType)
        return  element

    def elementClick(self, locator="", locatorType="xpath", element=None):
        """
        Click on an element -> MODIFIED
        Either provide element or a combination of locator and locatorType
        """
        try:
            if locator:  # This means if locator is not empty
                element = self.waitForElement(locator, locatorType)
                displayStatus = self.isElementDisplayed(element=element)
                enableStatus = self.isElementEnabled(locator, locatorType)
                element = self.getElement(locator, locatorType)
            element.click()
            self.log.info("Clicked on element with locator: " + locator +
                          " locatorType: " + locatorType)
        except:
            self.log.error("Cannot click on the element with locator: " + locator +
                          " locatorType: " + locatorType)
            #print_stack()

    def sendKeysOnElement(self, data, locator="", locatorType="id", element=None):
        """
        Either provide element or a combination of locator and locatorType
        """
        try:
            if locator:  # This means if locator is not empty
                status = self.waitForElement(locator,locatorType)
                element = self.getElement(locator, locatorType)
            element.clear()
            time.sleep(1)
            element.send_keys(data)
            self.log.info("Sent data on element with locator: " + locator +
                          " locatorType: " + locatorType)
        except:
            self.log.info("Cannot send data on the element with locator: " + locator +
                          " locatorType: " + locatorType)
            #print_stack()

    def selectElementFromDropDownMenuByValue(self, value, locator="", locatorType="id", element=None):
        try:
            if locator:  # This means if locator is not empty
                status = self.waitForElement(locator, locatorType)
                element = self.getElement(locator, locatorType)
            sel = Select(element)
            sel.select_by_value(value)
            self.log.info("element is selected : " + locator +
                          " value: " + value)
        except:
            self.log.error("Could not select the element " + locator +
                          "value: " + value)
            #print_stack()

    def selectElementFromDropDownMenuByVisibleText(self,text, locator="", locatorType="id", element=None):
        try:
            if locator:  # This means if locator is not empty
                status = self.waitForElement(locator, locatorType)
                element = self.getElement(locator, locatorType)
            sel = Select(element)
            sel.select_by_visible_text(text)
            self.log.info("element is selected : " + locator +
                          " text: " + text)
        except:
            self.log.error("Could not select the element " + locator +
                          "text: " + text)
            print_stack()

    def selectElementFromDropDownMenuByIndex(self,index, locator="", locatorType="id", element=None):
        try:
            if locator:  # This means if locator is not empty
                status = self.waitForElement(locator, locatorType)
                element = self.getElement(locator, locatorType)
            sel = Select(element)
            sel.select_by_index(index)
            self.log.info("element is selected : " + locator +
                          " index: " + index)
        except:
            self.log.error("Could not select the element " + locator +
                          "index: " + index)
            #print_stack()

    def isElementPresent(self, locator="", locatorType="xpath", element=None):
        """
        Check if element is present
        Either provide element or a combination of locator and locatorType
        """
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
            if element is not None:
                self.log.info("Element is present with locator: " + locator +
                              " locatorType: " + locatorType)
                return True
            else:
                self.log.error("Element is not present with locator: " + locator +
                              " locatorType: " + locatorType)
                return False
        except:
            self.log.error("Exception occured :Element is not  present with locator : " + locator)
            return False

    def elementPresenceCheck(self,locator,locatorType):
        try:
            locatorType = locatorType.lower()
            elementList = self.driver.find_elements(locatorType,locator)
            if(len(elementList) > 0 ):
                self.log.info("Elements found with locator "+ locator)
                return True
            else:
                self.log.info("Elements not found with locator" + locator)
                return False
        except:
            self.log.info("Elements not found with locator:"+ locator)
            #print_stack()
            return  False

    # pass list of elements
    def checkElementsPresenceOnPage(self,itemlist):
        PageElementsStatus = []
        for currentElement in itemlist:
            result = self.isElementPresent(currentElement, locatorType="xpath")
            if result is not None:
                if result == True:
                    self.log.info(currentElement + ' *** present on page *** ')
                    PageElementsStatus.append("p")
                else:
                    self.log.error(currentElement + ' ??? Not present page ??? ')
                    PageElementsStatus.append("Np")
            else:
                self.log.error(currentElement + 'Element not found on page')
                PageElementsStatus.append("Np")

        if "Np" in PageElementsStatus:
            return False
        else:
            return True

    def screenShot(self, resultMessage):
        timestr = time.strftime("%Y%m%d-%H-%M-%S")

        fileName = resultMessage + "." + timestr + ".png" # "-"+str(round(time.time())) +
        screenshotDirectory = "..\\screenshots\\"
        relativeFileName = screenshotDirectory + fileName
        currentDirectory = os.path.dirname(__file__)
        destinationFile = os.path.join(currentDirectory, relativeFileName)
        destinationDirectory = os.path.join(currentDirectory, screenshotDirectory)

        try:
            if not os.path.exists(destinationDirectory):
                os.makedirs(destinationDirectory)
            self.driver.save_screenshot(destinationFile)
            self.log.info("Screenshot save to directory: " + destinationFile)
        except:
            self.log.error("### Exception Occurred when taking screenshot")
            #print_stack()

    def waitForElement(self,locator,locatorType="xpath",maxtimeout=10,pollFrequency=2):
        element = None
        try:
            locatorType = locatorType.lower()
            byType = self.getByType(locatorType)
            self.log.info("waiting for max :: " + str(maxtimeout) + ":: second for the element")
            wait = WebDriverWait(self.driver,timeout=maxtimeout,poll_frequency=pollFrequency,ignored_exceptions=[NoSuchElementException,ElementNotSelectableException,ElementNotVisibleException,TimeoutException])
            element = wait.until(EC.element_to_be_clickable((byType,locator)))

            self.log.info("Element appeared on the webpage :"+ locator + "at attempt/poll frequency : "+pollFrequency)
        except:
            self.log.info("Element did not appeard on the webpage :" + locator)
        return element

    def waitForStateChangeElement(self,text,locator,locatorType="xpath", maxtimeout=60,pollFrequency=10):
        element = None
        try:
            locatorType = locatorType.lower()
            byType = self.getByType(locatorType)
            self.log.info("waiting for max :: " + str(maxtimeout) + ":: second for the element")
            wait = WebDriverWait(self.driver, timeout=maxtimeout, poll_frequency=pollFrequency,
                                 ignored_exceptions=[NoSuchElementException, ElementNotSelectableException,
                                                     ElementNotVisibleException, TimeoutException])
            element = wait.until(EC.text_to_be_present_in_element((byType,locator),text))
            self.log.info(
                "Element :" + locator + " with text = " + text)
        except:
            self.log.info("Element did not found :" + locator + "with text = " + text)
        return element

    def excecuteJsReturnElement(self,locator):
        element = self.driver.execute_script("return document.getElementsByClassName(locator);")
        return element

    def executeJsForFileUpload(self,fileName,dirName=None):
        input = self.getElement(locatorType="cssselector", locator="input[type='file']")
        self.driver.execute_script('arguments[0].style = ""; arguments[0].style.display = "block"; arguments[0].style.visibility = "visible";',input)
        self.driver.file_detector = LocalFileDetector()
        time.sleep(2)
        input.send_keys(fileName)

    def getPageSource(self):
        try:
            source = self.driver.page_source
            sourceCode = source.encode('utf-8')
            return sourceCode
        except:
            self.log.info('page source code not found')
            return None

    def isElementEnabled(self,locator,locatorType="xpath"):
        try:
            locatorType = locatorType.lower()
            element = self.getElement(locator, locatorType)
            if element is not None:
                self.log.info("Element exists on the page with locator : " + locator)
                result = element.is_enabled()
                return result
            else:
                self.log.error("Element did not found on the page with locator : " + locator)
                return False
        except:
            self.log.info("Element did not found on the page with locator : " + locator)
            return False

    def getPageTitle(self):
        try:
            pagetitle = self.driver.title
            self.log.info("page tile = " + pagetitle)
            return pagetitle
        except:
            self.log.error("page title not found")
            return None

    '''def getElementsFromTable(self):
        elementlist = []
        try:
            tableresult = self.elementPresenceCheck("//table[@class='table table-bordered customTable']",locatorType="xpath")
            self.log.info("table element exists??? ==" + str(tableresult))

            table = self.driver.find_elements_by_xpath("//table[@class='table table-bordered customTable']")
            self.log.info("number of table:"+ str(table))

            tableRowresult = self.elementPresenceCheck("//tr[@class='customTableRow']",
                                                    locatorType="xpath")
            self.log.info("tableRowresult exists??? ==" + str(tableRowresult))

            tablecolresult = self.elementPresenceCheck("//td[@class='customTableCol",
                                                       locatorType="xpath")
            self.log.info("tablecolresult exists??? ==" + str(tablecolresult))

            for row in table.find_elements_by_xpath("//tr[@class='customTableRow']",locatorType="xpath"):
                for td in row.find_elements_by_xpath("//td[@class='customTableCol']",locatorType="xpath"):
                    self.log.info([td.text])
                    elementlist.append([td.text])
        except:
                print('None')'''

    def getElementList(self, locator, locatorType="xpath"):
        """
        Get list of elements
        """
        element = None
        try:
            locatorType = locatorType.lower()
            byType = self.getByType(locatorType)
            element = self.driver.find_elements(byType, locator)
            self.log.info("Element list found with locator: " + locator +
                          " and locatorType: " + locatorType)
        except:
            self.log.info("Element list not found with locator: " + locator +
                          " and locatorType: " + locatorType)
        return element

    def getText(self, locator="", locatorType="id", element=None, info=""):
        """
        Get 'Text' on an element
        Either provide element or a combination of locator and locatorType
        """
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
            text = element.text
            if len(text) == 0:
                #text = element.get_attribute("innerText")
                text =''
            if len(text) != 0:
                self.log.info("Getting text on element :: " + info)
                self.log.info("The text is :: '" + text + "'")
                text = text.strip()
            
        except:
            #self.log.error("Failed to get text on element " + info)
            #print_stack()
            text = ''
        return text

    def isElementDisplayed(self, locator="", locatorType="xpath", element=None):
        """
        Check if element is displayed
        Either provide element or a combination of locator and locatorType
        """
        isDisplayed = False
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
            if element is not None:
                isDisplayed = element.is_displayed()
                self.log.info("Element is displayed" + element)
            else:
                self.log.error("Element is not displayed" + element)
            return isDisplayed
        except:
            self.log.error("Element is not displayed")
            return False

    

    def scrollMultipleTimeToSeeHiddenElement(self):
        container_selector = "#grid_TnInventory-Table_records"  # your table container
        scroll_step = 100  # pixels per scroll
        scroll_times = 3   # number of scrolls
        
        
        for i in range(scroll_times):
            self.driver.execute_script('''
                var container = document.querySelector(arguments[0]);
                container.scrollLeft += arguments[1];
                console.log("Scroll attempt:", arguments[2], "New scrollLeft:", container.scrollLeft);
            ''', container_selector, scroll_step, i + 1)
        
    def webScroll(self, direction="up"):

        if direction == "up":
            # Scroll Up
            self.driver.execute_script("window.scrollBy(0, -2000);")

        if direction == "down":
            # Scroll Down
            self.driver.execute_script("window.scrollBy(0, 2000);")

        if direction == "bottom":
            # Scroll Down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        if direction == "horizontal":
            self.driver.execute_script("window.scrollTo(document.body.scrollWidth,document.body.scrollHeight);")

        if direction == "right":
            # Scroll Down
            self.driver.execute_script("window.scrollBy(1500, 0);")

        if direction == "left":
            # Scroll Down
            self.driver.execute_script("window.scrollBy(-1000, 0);")

    def webScrollIntoView(self, locator,locatorType):
        element = None
        try:
            if locator:  # This means if locator is not empty
                element = self.getElement(locator, locatorType)
                self.log.info('scrolling to the element : ' + element )
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                return element
        except:
            self.log.error('unable to scroll into view for the element = '+locator)
            return None



   
        
    def webScrollIntoViewAndClickElement(self, locator,locatorType):
        try:
            if locator:  # This means if locator is not empty
                '''
                element = self.getElement(locator, locatorType)
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                element.click() '''
                #element = self.webScrollIntoView(locator,locatorType)
                #element.click()
                wait = WebDriverWait(self.driver, 10)
                element = wait.until(EC.element_to_be_clickable((locatorType, locator)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                element.click()
                print(f"Clicked element: {locator}")
        except Exception as e:
            print(f"Normal click failed: {e}")
            try:
                # Fallback to JS click
                self.driver.execute_script("arguments[0].click();", element)
                print(f"Clicked element with JS: {locator}")
            except Exception as ex:
                print(f"JS click failed: {ex}")
                self.log.error('unable to click on = '+locator)
                
    def executeJsToClickSearch(self):
        js_click = """
                    Array.from(document.querySelectorAll("button"))
                         .filter(btn => btn.textContent.trim() === "Search")[0]
                         .click();
                    """
        self.driver.execute_script(js_click)
        
    def executeJsToFillRequester(self, requester_name, locator, locatorType="xpath"):
        element = self.getElement(locator, locatorType)
        self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", element, requester_name)

    def get_links_by_date(self, date_str):
        try:
            js_code = """
            var date_str = arguments[0];
            var rows = document.querySelectorAll("#grid_BlkInventory-Table_records tr");
            var results = [];

            rows.forEach(row => {
                var tds = row.querySelectorAll("td");
                var matched = false;

                tds.forEach(td => {
                    if(td.innerText.includes(date_str)) {
                        matched = true;
                    }
                });

                if(matched) {
                    var links = row.querySelectorAll("td a");
                    links.forEach(a => results.push(a.innerText.trim()));
                }
            });

            return results;
            """
            #print(js_code)
            # Pass the Python variable as an argument to JS
            block_list = self.driver.execute_script(js_code, date_str)
            #print(block_list)
            return block_list
        except Exception as e:
            print(e)
            return []

        
    def webJSexcuteClickonlogoutElement(self):
        try:
            element = self.driver.execute_script("return document.getElementsByClassName('toast-close-button');")
            element[0].click()
        except:
            self.log.error('unable to click on element')

    def mouseHoverOnElement(self,locator="", locatorType="xpath", element=None):
        try:
            self.mouse = ActionChains(self.driver)
            status = self.waitForElement(locator, locatorType)
            element = self.getElement(locator, locatorType)
            self.mouse.move_to_element(element).perform()
        except:
            self.log.error('unable to click even after  mouse hover')

    def mouseHoverAndElementClick(self,locator="", locatorType="xpath", element=None):
        try:
            self.mouse = ActionChains(self.driver)
            status = self.waitForElement(locator, locatorType)
            element = self.getElement(locator, locatorType)
            self.mouse.move_to_element(element).click().perform()
        except:
            self.log.error('unable to click even after  mouse hover')

    def JSExecuteAttachedFile(self,filename):
        try:
            self.driver.execute_script("document.getElementById('attachFile').value='" + filename + "';")
        except:
            self.log.error('unable to attach the file ' + filename )


    def JsExecuteZoomInZoomOut(self,value):
        try:
            self.driver.execute_script("document.body.style.zoom='"+str(value)+"%'")
            #document.body.style.transform = 'scale(0.9)'
        except:
            self.log.error('unable to zoom out')

    def injectJsForFileUpload(self,input,fileName):
        self.driver.execute_script(
            'arguments[0].style = ""; arguments[0].style.display = "block"; arguments[0].style.visibility = "visible";',
            input)
        print(self.driver.title)
        self.driver.file_detector = LocalFileDetector()
        time.sleep(2)
        input.send_keys(fileName)
        time.sleep(2)

#### windows handling wrappers####

    def getParentWindowHandle(self):
        parentHandle = None
        try:
            parentHandle = self.driver.current_window_handle()
            self.log.info('Current/Parent Window handle '+parentHandle + ' With Window Title :: ' + self.getWindowTitle())
        except:
            self.log.error('Unable to get the current/parent window handle')

        return parentHandle


    def getWindowHandles(self):
        handles = []
        try:
            handles = self.driver.window_handles
            #print(handles)
            self.log.info("Total visible windows ::" + str(len(handles)) +  " windows ids are:: " + str(handles))
        except:
            self.log.error('Unable to get the Window handles')
        return handles

    def getWindowTitle(self):
        return self.driver.title

    def switchToOtherWindow(self):
            handles = self.getWindowHandles()
            #print(len(handles))
            self.driver.switch_to.window(handles[1])
            print('Switching to Window :: ' + handles[1] + ' With Window Title :: ' + self.getWindowTitle())
            self.log.info('Switching to Window  :: ' + handles[1] + ' With Window Title :: ' + self.getWindowTitle())
            self.maximize_window()

    def switchToMainWindow(self):
            handles = self.getWindowHandles()
            #print(len(handles))
            self.driver.switch_to.window(handles[0])
            print('Switching to Main Window :: ' + handles[0] + ' With Window Title :: ' + self.getWindowTitle())


    def switchToWindowHandle(self,handle):
        self.driver.switch_to.window(handle)

    def maximize_window(self):
        self.driver.maximize_window()

    def close(self):
        self.driver.close()

    def quit(self):
        self.driver.quit()

