from ConfigParser import ConfigParser
import os

class ConfigReader(object):

    def __init__(self, fileName="testenvironment.ini"):
        self.parser = ConfigParser()
        scriptDirectory = os.path.dirname(__file__)
        print(scriptDirectory)
        os.chdir('../configfiles')
        scriptDirectory = os.getcwd()

        absFilePath = os.path.join(scriptDirectory,fileName)
        val = os.path.dirname(absFilePath)
        print(val)
        #relativePath = "../configfiles/" + fileName
        #print(relativePath)
        #absFilePath = os.path.join(scriptDirectory, relativePath)
        print(absFilePath)
        self.file = absFilePath

    def configRead (self):
        self.parser.read(self.file)

    def configSectionMap(self, section):
        config = {}
        options = self.parser.options(section)
        for option in options:
            try:
                config[option] = self.parser.get(section, option)
                if config[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                config[option] = None
        return config

    def getConfiguration(self, section, option):
        config_map = self.configSectionMap(section)
        option_value = config_map[option]
        return option_value


