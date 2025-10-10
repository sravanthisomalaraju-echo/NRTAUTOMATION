import utilities.custom_logger as cl
import logging
from base.selenium_driver import SeleniumDriver
from traceback import print_stack

class TsStatus(SeleniumDriver):

    log = cl.customLoggerMethod(logging.INFO)


    def __init__(self, driver):
        super(TsStatus, self).__init__(driver)
        self.resultList = []

    def setResult(self, result, resultMessage):
        try:
            if result is not None:
                if result == True:
                    self.resultList.append("PASS")
                    self.log.info(resultMessage + " \n\t  :: ### VERIFICATION SUCCESSFUL ###  ")
                else:
                    self.resultList.append("FAIL")
                    self.log.error(resultMessage + "\n\t :: ### VERIFICATION FAILED ### \t\n ")
                    self.screenShot(resultMessage)

            else:
                self.resultList.append("FAIL")
                self.log.error(resultMessage + "\n\t :: ### VERIFICATION FAILED ### \t\n")
                self.screenShot(resultMessage)

        except:
                self.resultList.append("FAIL")
                self.log.error(resultMessage + " :: ### Exception Occurred !!! ")
                self.screenShot(resultMessage)
                print_stack()

    def mark(self, result, resultMessage):
        """
        Mark the result of the verification point in a test case
        """
        self.setResult(result, resultMessage)

    def markFinal(self, testName, result, resultMessage):
        """
        Mark the final result of the verification point in a test case
        This needs to be called at least once in a test case
        This should be final test status of the test case
        """
        self.setResult(result, resultMessage)

        if "FAIL" in self.resultList:
            self.log.error("\n\t ### :: "+ testName + " :: ### TEST FAILED ###\t\n")
            #self.resultList.clear()
            self.resultList[:] = []
            assert True == False
        else:
            self.log.info("\n\t ### :: "+ testName + " ::  ### TEST SUCCESSFUL ###\t\n ")
            #self.resultList.clear()
            self.resultList[:] = []
            assert True == True