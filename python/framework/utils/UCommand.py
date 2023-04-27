import os
import subprocess
import threading
import time
from framework.basic.BConstant import *

def RunPython(v : str):
    print('UCommand->RunPython, cmd: ' + v)
    code = 0
    try:
        code = subprocess.call(v, shell=True)
    except Exception as e:
        print('UCommand->RunPython, exception: ' + str(e))
        code = -1234567890
    finally:
        pass

    return code

def RunCmd(v : str):
    # return os.system(v)
    print('UCommand->RunCmd, cmd: ' + v)
    code = 0
    try:
        # pp = subprocess.Popen(v, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')#'gb2312'
        # (stdout,_) = pp.communicate()
        # print(stdout)
        pp = subprocess.Popen(v, shell=True, encoding='utf-8')#'gb2312'
        pp.wait()
        code = pp.returncode
    except Exception as e:
        print('UCommand->RunCmd, exception: ' + str(e))
        code = -1234567890
    finally:
        pass

    return code

class IncrementalContent2Console:
    __thread = None
    __filePath = ''
    __interval = 1.0
    __Position = 0
    __Running = False
    def __init__(self, filePath : str, interval : float = 1.0):
        self.__filePath = filePath
        self.__interval = interval

    def __ThreadFunc(self):
        while (self.__Running):
            if not os.path.exists(self.__filePath): continue
            if not os.path.isfile(self.__filePath): continue
            
            lines = None
            f = None
            try:
                if BConstSystemPlatform == BPlatformEnum.Windows:
                    f = open(self.__filePath, 'r', encoding='utf-8')
                else:
                    f = open(self.__filePath, 'r')
                    
                if not f is None:
                    f.seek(self.__Position)
                    lines = f.readlines()
                    self.__Position = f.tell()                   
            finally:
                if not f is None:
                    f.close()

            if not lines is None:
                for line in lines:
                    print(line, end='')

            time.sleep(self.__interval)

    def Start(self):
        if not self.__thread is None: return
        self.__Running = True
        self.__thread = threading.Thread(target=self.__ThreadFunc, name='IncrementalContentOutputThread')
        self.__thread.start()

    def Finish(self):
        if self.__thread is None: return
        self.__Running = False
        self.__thread.join(30)
        self.__thread = None