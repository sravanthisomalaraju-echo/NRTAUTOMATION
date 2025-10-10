import logging
import inspect
import time
import os
from traceback import print_stack
from configfiles.common_variable import *
import sys

def customLoggerMethod(loglevel=logging.DEBUG):
    platform = sys.platform
    logDir = ''
    
    logDirtimestr = time.strftime("%Y-%m-%d")
    logDirName =  os.path.join(logDir,"Automation-"+logDirtimestr)

    if not os.path.exists(logDirName):
        os.makedirs(logDirName, 0o755)
    else :
        print('Directory already exists: '+ logDirName)

    #get the name of method/class from which the method is called.
    loggername = inspect.stack()[1][3]
    logger = logging.getLogger(loggername)
    logger.setLevel(logging.DEBUG)

    timestr = time.strftime("%H-%M-%S")
    automationLogFile = "Automation" + "-" + timestr + ".log"

    fileHandler = logging.FileHandler(logDirName + os.path.sep +automationLogFile,mode='a')
    fileHandler.setLevel(loglevel)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s',datefmt='%d/%m/%Y %I:%M:%S %p')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    return logger

