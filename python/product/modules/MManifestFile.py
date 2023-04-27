from framework.utils import UOS
from framework.utils import UBase
from framework.utils import UJson
from framework.utils import UTracking

class MManifestFile:
    __path = ''
    __datas = {}
    ######
    @staticmethod
    def Name():
        return 'meta.nocache'
    ######
    def CreateFrom(self, path : str) -> bool:
        self.__path = path
        self.__datas = {}
        if UOS.IsFileExist(path):
            UTracking.LogError('MManifestFile->CreateFrom', f'file: {path}')
            return False
        #
        return True

    def SaveTo(self, path : str) -> bool:
        UJson.ToJsonFile(self.__datas, path)
        UTracking.LogInfo('MManifestFile->SaveTo', f'file: {path}')
        return True

    def Save(self) -> bool:
        return self.SaveTo(self.__path)
    ######
    def __MakeData(self, key : str, value : str):
        if UBase.IsStringNoneOrEmpty(value):
            self.__datas.pop(key, None)
        else:
            self.__datas[key] = value
    
    def __AddDict(self, key : str, value : dict):
        if UBase.IsContainerNoneOrEmpty(value):
            self.__datas.pop(key, None)
        else:
            self.__datas[key] = value

    def MakeDesc(self, v : str):
        self.__MakeData('desc', v)

    def MakePackageURL(self, v : str):
        self.__MakeData('packageUrl', v)

    def AddFolder(self, folder : str, bundleVersion : int):
        dict = { 'name':folder, 'version':f'{bundleVersion}' }
        self.__AddDict(folder, dict)