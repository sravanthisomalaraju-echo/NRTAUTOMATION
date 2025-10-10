import os
import hashlib
import re
import shutil
import time


class GenericFileUtils(object):

#file handling specific methods
    def getCurrentWorkingDir(self):
        print('Current Working Directory = ' + os.getcwd())
        return os.getcwd()

    def changeWorkingDir(self,path):
        cwd = os.getcwd()
        #print(cwd)
        pwd = os.chdir(path)
        return pwd


    def getAbsolutePath(self, path):
        val = os.path.exists(path)
        if val == True:
            print('AbsoultePath = ' + os.path.abspath(path))
            return os.path.abspath(path)
        else:
            return None


    def getRelativePath(self, source, relativeTo):
        # return os.path.relpath(C:\\Windows', 'C:\\ankesh\\project')
        # '..\\..\\Windows'
        val = os.path.exists(relativeTo)
        val1 = os.path.exists(source)
        if (val and val1) == True:
            return os.path.relpath(source, relativeTo)
        else:
            return None


    def getBasename(self, path):
        # path = 'C:\\Windows\\System32\\Notepad.exe'
        # return 'Notepad.exe'
        val = os.path.exists(path)
        if val == True:
            return os.path.basename(path)
        else:
            return None


    def getDirectoryName(self, path):
        val = os.path.exists(path)
        if val == True:
            return os.path.dirname(path)
        else:
            return None


    def getDirNameAndFileName(self, path):
        val = os.path.exists(path)
        if val == True:
            return os.path.split(path)
        else:
            return None


    def listDirectories(self, path):
        val = os.path.exists(path)
        if val == True:
            dirs = os.listdir(path)
            print(str(dirs))
            return dirs
        else:
            return None


    def getFileSize(self, path):
        val = os.path.exists(path)
        if val == True:
            print('file :: ' + path + ' :: size = ' + os.path.getsize(path))
            return os.path.getsize(path)
        else:
            return None


    def readFileContentAsString(self, fileName):
        with open(fileName) as file:
            content = file.read()
            # print(content)
            return content


    def readFileContentAsList(self, fileName):
        with open(fileName) as file:
            contentList = file.readlines()
            # print(str(contentList))
            return contentList


    def findHashCodeOfFile(self, fileName):
        """"This function returns the SHA-1 hash of the file passed into it"""
        # make a hash object
        h = hashlib.sha1()

        # open file for reading in binary mode
        with open(fileName, 'rb') as file:
            # loop till the end of the file
            chunk = 0
            while chunk != b'':
                # read only 1024 bytes at a time
                chunk = file.read(1024)
                h.update(chunk)

        # return the hex representation of digest  #print(str(h.hexdigest()))
        return h.hexdigest()


    def copyFile(self, sourceFile, destinationPath):
        try:
            val = os.path.exists(sourceFile)
            val1 = os.path.exists(destinationPath)
            if (val and val1) == True:
                shutil.copy(sourceFile, destinationPath)
            else:
                print('Kindly check source file and destination path')
        except:
            print('########### Exception Occured ########## Copy File opertation did not work')


 

    # regex specifc Methods
    def findMatchingStringUsingRegex(self, actualString, pattern):
        try:
            regex = re.compile(pattern)
            matchObj = regex.search(actualString)
            print('Match found ################## ' + matchObj.group() + '#################')
        except:
            print(' ????? Match not found ?????  ')


    def findMatchingGroupsUsingRegex(self, actualString, pattern):
        try:
            regex = re.compile(pattern)
            matchObj = regex.search(actualString)
            print('Matches found ################## ' + str(matchObj.groups()))
            return matchObj.groups()
        except:
            print(' ????? Match not found ?????  ')


    def findAllMatchingStringsUsingRegex(self, actualString, pattern):
        try:
            regex = re.compile(pattern)
            matchObj = regex.findall(actualString)
            print('Matched tuple count :: ' + str(len(matchObj)))
            print('Match Strings list found ################## ' + str(matchObj) + '#################')
        except:
            print(' ????? Match not found ?????  ')


    def substituteMatchedString(self, subString, actualStirng, pattern):
        try:
            regex = re.compile(pattern)
            substituteString = regex.sub(subString, actualStirng)
            print('Original String = ' + actualStirng + ' changed to /substitute to ' + substituteString)
            return substituteString
        except:
            print('Substitution of string did not work')

