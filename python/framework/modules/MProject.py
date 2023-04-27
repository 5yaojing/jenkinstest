import os
from ..basic.BDefines import *
from ..utils import UBase
from ..utils import UOS
from ..utils import UDateTime
from ..config.CProject import *
from .MGit import *
from .MUnity import *
from .MAndroidStudio import *
from .MAndroidAggregateSDK import *
from .MXCode import *

class MProject:
    __config : CProject = None
    __busyMarkTag = ''
    __startTime = 0
    __preTime = 0
    ################################################################ 
    def __init__(self, config : CProject, busyMarkTag : str):
        if config is None:
            UTracking.RaiseException('MProject->__init__', 'config is none')

        if UBase.IsStringNoneOrEmpty(busyMarkTag):
            UTracking.RaiseException('MProject->__init__', 'busy mark tag is bad')

        self.__config = config
        self.__busyMarkTag = busyMarkTag
    ################################################################  
    def __CreateBusyMark(self):
        #busy mark file
        bmPath = self.__config.busyMark
        UOS.CreateFileEmpty(bmPath, True)
        #busy mark tag file
        directory = UOS.DirectoryOfPath(bmPath)
        tagPath = os.path.join(directory, f'{self.__busyMarkTag}.tag')
        UOS.SaveStringFile(tagPath, bmPath)

    def __DeleteBusyMark(self):
        #busy mark file
        bmPath = self.__config.busyMark
        UOS.DeleteFile(bmPath)
        #busy mark tag file
        directory = UOS.DirectoryOfPath(bmPath)
        tagPath = os.path.join(directory, f'{self.__busyMarkTag}.tag')
        UOS.DeleteFile(tagPath)
    
    @staticmethod
    def GetBusyMarkTag(args : dict) -> str:
        if args is None:
            UTracking.RaiseException('MProject->GetBusyMarkTag', 'args is none')
        tag = args.get('bmt975310')
        if tag is None:
            UTracking.RaiseException('MProject->GetBusyMarkTag', 'busy mark tag is none')
        tag = tag.replace(' ', '').replace('.', '_').replace('\\', '_').replace('/', '_') 
        if tag == '':
            UTracking.RaiseException('MProject->GetBusyMarkTag', 'busy mark tag is empty')
        return tag
        
    @staticmethod
    def CleanBusyMarkResidual(projectRoot : str, busyMarkTag : str) -> bool:
        tagPath = os.path.join(projectRoot, f'{busyMarkTag}.tag')
        if not UOS.IsFileExist(tagPath): return False

        result = False
        bmPath = UOS.LoadStringFile(tagPath)
        if not UBase.IsStringNoneOrEmpty(bmPath):
            if UOS.IsFileExist(bmPath):
                UOS.DeleteFile(bmPath)
                result = True
                
        UOS.DeleteFile(tagPath)
        return result

    ################################################################
    def SetupGitParams(self, repositoryKey : str, params : MGitParams):
        value = self.__config.gitRepositorys.get(repositoryKey)
        if value is None:
            UTracking.RaiseException('MProject->SetupGitParams', 'not found repository key: ' + repositoryKey)
        else:
            params.url = value['url']
            params.location =  os.path.join(self.__config.root, value['location']) 

    def SetupUnityParams(self, params : MUnityParams, platform : MUnityPlatformEnum):
        params.buildTarget = platform
        params.projectPath = os.path.join(self.__config.root, self.__config.untiyRoot)
        if platform == MUnityPlatformEnum.IOS or platform == MUnityPlatformEnum.OSX:
            params.exportPath = os.path.join(self.__config.root, self.__config.unityExportPathApple)
        elif platform == MUnityPlatformEnum.Android:
            params.exportPath = os.path.join(self.__config.root, self.__config.unityExportPathAndroid)
        elif platform == MUnityPlatformEnum.Windows:
            params.exportPath = os.path.join(self.__config.root, self.__config.unityExportPathWindows)
        elif platform == MUnityPlatformEnum.Linux:
            params.exportPath = os.path.join(self.__config.root, self.__config.unityExportPathLinux)
        else:
            UTracking.RaiseException('MProject->SetupUnityParams', 'platform: ' + platform)        

    def SetupXCodeParams(self, params : MXCodeParams):
        params.workspace = self.__config.xcodeWorkspace
        params.projectPath = os.path.join(self.__config.root, self.__config.appleRoot, self.__config.xcodeProjectPath, self.__config.xcodeProjectFile)

    def SetupAndroidStudioParams(self, params : MAndroidStudioParams):
        params.projectPath = os.path.join(self.__config.root, self.__config.androidRoot, self.__config.androidStudioProjectPath)
        params.outputAPKPath = os.path.join(self.__config.root, self.__config.androidRoot, self.__config.androidStudioOutputAPKPath)
        params.outputAABPath = os.path.join(self.__config.root, self.__config.androidRoot, self.__config.androidStudioOutputAABPath)
        params.mainProjectPath = os.path.join(self.__config.root, self.__config.untiyRoot)

    def SetupAndroidAggregateSDKParams(self, params : MAndroidAggregateSDKParams):
        params.outputAPKPath = os.path.join(self.__config.root, self.__config.androidRoot, self.__config.androidAggregateSDKOutputAPKPath)
        params.outputAABPath = os.path.join(self.__config.root, self.__config.androidRoot, self.__config.androidAggregateSDKOutputAABPath)
        params.mainProjectPath = os.path.join(self.__config.root, self.__config.untiyRoot)

    def GetTempLocation(self):
        return os.path.join(self.__config.root, self.__config.tempLocation)

    def MakeArchiveLocation(self, **kwargs):
        return self.__config.archiveLocation.format(**kwargs)

    def Begin(self):
        UTracking.LogInfo('MProject->Begin', 'root: ' + self.__config.root)
        self.__startTime = UDateTime.CurTimeSecond()
        self.__preTime = self.__startTime
        self.__CreateBusyMark()

    def End(self):
        self.__DeleteBusyMark()
        curTime =  UDateTime.CurTimeSecond()        
        dtp = curTime - self.__preTime
        dtf = curTime - self.__startTime
        self.__preTime = curTime
        UTracking.LogInfo('MProject->End', f'time elapsed: {dtp}/{dtf}s')

    def Check(self, result : bool, step : str, args : dict = None):
        curTime =  UDateTime.CurTimeSecond()        
        dtp = curTime - self.__preTime
        dtf = curTime - self.__startTime
        self.__preTime = curTime
        if result:
            UTracking.LogInfo('MProject->Check', f'time elapsed: {dtp}/{dtf}s, result: {step} done')
        else:
            UTracking.RaiseException('MProject->Check', f'time elapsed: {dtp}/{dtf}s, result: {step} error\nconfig: {UTracking.BeautifyLog(self.__config.__dict__)}\nargs: {UTracking.BeautifyLog(args)}')          
