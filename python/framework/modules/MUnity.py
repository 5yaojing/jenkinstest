import os
from ..basic.BDefines import *
from ..basic.BConstant import *
from ..utils import UBase
from ..utils import UOS
from ..utils import UTracking
from ..utils import UEncrypt
from ..utils import UCommand
from ..config.CUnity import *

class MUnityPlatformEnum(Enum):
    Android = 'Android'
    IOS     = 'iOS'
    Windows = 'Win64'
    OSX     = 'OSXUniversal'
    Linux   = 'Linux64'
    
    @staticmethod
    def From(platform : BPlatformEnum):
        p = MUnityPlatformEnum.Android
        
        if platform == BPlatformEnum.Android:
            p = MUnityPlatformEnum.Android
        elif platform == BPlatformEnum.IOS:
            p = MUnityPlatformEnum.IOS
        elif platform == BPlatformEnum.Windows:
            p = MUnityPlatformEnum.Windows
        elif platform == BPlatformEnum.OSX:
            p = MUnityPlatformEnum.OSX
        elif platform == BPlatformEnum.Linux:
            p = MUnityPlatformEnum.Linux
        else:
            UTracking.RaiseException('MUnityPlatformEnum->From', 'platform: ' + platform)
        
        return p
    
class MUnityParams:
    buildTarget = MUnityPlatformEnum.Android    
    projectPath = ''
    exportPath = ''

    logFile = 'BuildLog.txt'
    clearScriptAssemblies = False
    publish = False    
    batchMode = True
    noGraphics = True
    quit = True    
    customParams = ''
    executeMethod = ''
    executeMethodParams = ''
    
class MUnity:
    __config : CUnity = None
    ################################################################ 
    def __init__(self, config : CUnity):
        if config is None:
            UTracking.RaiseException('MUnity->__init__', 'config is none')
        self.__config = config
    ################################################################
    def GetEngineSymbolTablePath(self, releaseMode : bool, il2cpp : bool, platform : BPlatformEnum, architecture : BArchitectureEnum) -> str:
        path = self.__config.playbackEnginesPath
        if platform == BPlatformEnum.Android:
            path += 'AndroidPlayer/Variations/'
            path += 'il2cpp/' if il2cpp else 'mono/'
            path += 'Release/' if releaseMode else 'Development/'
            path += 'Symbols/'
            path += f'{architecture.value}/'
        # elif platform == BPlatformEnum.IOS:
        #     path += 'IOSSupport/'#暂时还不确定这个目录，到时候改
        else:
            UTracking.RaiseException('MUnity->GetEngineSymbolTablePath', 'Unsupported system platform: ' + platform.value)
            
        return path

    def Exec(self, params : MUnityParams) -> bool:
        UTracking.LogInfo('MUnity->Exec', f'begin params: {UTracking.BeautifyLog(params.__dict__)}')

        if not UOS.IsDirectoryExist(params.projectPath): 
            UTracking.LogError('MUnity->Exec', 'project path not existed: \'' + params.projectPath + '\'')
            return False

        if params.clearScriptAssemblies:
            scriptAssembliesPath = os.path.join(params.projectPath, 'Library/ScriptAssemblies/')
            if UOS.IsDirectoryExist(scriptAssembliesPath):
                UOS.DeleteDirectory(scriptAssembliesPath)
                UTracking.LogInfo('MUnity->Exec', f'clear script assemblies, path: {scriptAssembliesPath}')


        unityOutputPath = params.exportPath
        unityOutputPathOther = UOS.ChangeDirectoryName(params.exportPath, '_BurstDebugInformation_DoNotShip')
        if UOS.IsDirectoryExist(unityOutputPath):
            UOS.DeleteDirectory(unityOutputPath)
        if UOS.IsDirectoryExist(unityOutputPathOther):
            UOS.DeleteDirectory(unityOutputPathOther)

        
        
        cmd = self.__config.appPath

        # account = ''
        # password = ''
        # serial = ''
        # if params.publish:
        #     if BConstSystemPlatform == BPlatformEnum.Windows:
        #         account = self.__config.account_Publish
        #         password = self.__config.password_Publish                
        #     else:
        #         account = f'\'{self.__config.account_Publish}\''
        #         password = f'\'{self.__config.password_Publish}\''
        #     serial = self.__config.serial_Publish
        # else:
        #     if BConstSystemPlatform == BPlatformEnum.Windows:
        #         account = self.__config.account_Develop
        #         password = self.__config.password_Develop                
        #     else:
        #         account = f'\'{self.__config.account_Develop}\''
        #         password = f'\'{self.__config.password_Develop}\''
        #     serial = self.__config.serial_Develop
        
        # cmd += ' -username ' + account
        # cmd += ' -password ' + password
        # if not UBase.IsStringNoneOrEmpty(serial):
        #     cmd += ' -serial ' + serial

        if params.quit:
            cmd += ' -quit'
            
        if params.batchMode:
            if params.noGraphics:
                cmd += ' -batchmode -nographics'
            else:
                cmd += ' -batchmode'
        
        withLogFile = not UBase.IsStringNoneOrEmpty(params.logFile)
        logFile = os.path.join(params.projectPath, params.logFile) if withLogFile else ''

        cmd += ' -logFile ' + logFile if withLogFile else '-'
        cmd += ' -buildTarget ' + params.buildTarget.value
        cmd += ' -projectPath ' + params.projectPath

        if not UBase.IsStringNoneOrEmpty(params.customParams):
            cmd += ' ' + params.customParams

        if not UBase.IsStringNoneOrEmpty(params.executeMethod):
            cmd += ' -executeMethod ' + params.executeMethod
            if not UBase.IsStringNoneOrEmpty(params.executeMethodParams):
                cmd += ' ' + UEncrypt.StringToBase64(params.executeMethodParams)        

        log2Console = None
        if withLogFile:
            if UOS.IsFileExist(logFile):
                UOS.DeleteFile(logFile)
            log2Console = UCommand.IncrementalContent2Console(logFile)
            log2Console.Start()
        
        result = UCommand.RunCmd(cmd)

        if withLogFile:
            log2Console.Finish()

        UTracking.LogInfo('MUnity->Exec', 'end')
        return result == 0