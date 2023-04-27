import os
from ..basic.BDefines import *
from ..basic.BConstant import *
from ..utils import UBase
from ..utils import UOS
from ..utils import UTracking
from ..utils import UCommand
from ..config.CAndroidAggregateSDK import *
 
class MAndroidAggregateSDKParams:    
    outputAPKPath = ''
    outputAABPath = ''
    mainProjectPath = ''

    inputPath = ''
    APKOrAAB = True
    projectPath = ''
    projectBuildPath = ''

class MAndroidAggregateSDK:
    __config : CAndroidAggregateSDK = None
    ################################################################ 
    def __init__(self, config : CAndroidAggregateSDK):
        if config is None:
            UTracking.RaiseException('MAndroidAggregateSDK->__init__', 'config is none')
        self.__config = config
    ################################################################
    @staticmethod
    def __GetBuildParamsPath(params : MAndroidAggregateSDKParams):
        return os.path.join(params.projectBuildPath, 'build-params.txt')

    ################################################################
    @staticmethod
    def GetOutputPackageDirectory(params : MAndroidAggregateSDKParams):
        return params.outputAPKPath if params.APKOrAAB else params.outputAABPath
        
    ################################################################
    def MakeBuildParams(self, params : MAndroidAggregateSDKParams) -> bool:
        path = self.__GetBuildParamsPath(params)
        UTracking.LogInfo('MAndroidAggregateSDK->MakeBuildParams', f'begin file: \'{path}\'')

        lines = []

        lines.append(f'-i {params.inputPath}')
        outputPath = self.GetOutputPackageDirectory(params)
        lines.append(f'-o {outputPath}')

        lines.append(f'--androidGradleBuildVersion {self.__config.gradle.toolsBuildGradleVersion}')
        lines.append(f'--compileSdkVersion {self.__config.gradle.compileSdkVersion}')
        lines.append(f'--buildToolsVersion {self.__config.gradle.buildToolsVersion}')
        lines.append(f'--minSdkVersion {self.__config.gradle.minSdkVersion}')
        lines.append(f'--targetSdkVersion {self.__config.gradle.targetSdkVersion}')
        
        keystorePath = os.path.join(params.mainProjectPath, self.__config.gradle.keystoreName) if self.__config.gradle.keystoreFromMainProject else self.__config.gradle.keystoreName
        lines.append(f'--storeFile {keystorePath}')
        lines.append(f'--storePassword {self.__config.gradle.keystorePass}')
        lines.append(f'--keyAlias {self.__config.gradle.keyaliasName}')
        lines.append(f'--keyPassword {self.__config.gradle.keyPassword}')
        lines.append(f'--v1SigningEnabled true')
        lines.append(f'--v2SigningEnabled true')

        lines.append(f'--aggregateDir {params.projectPath}')
        tuyooSdkPath = f'{params.projectPath}tools/tuyoosdk/' if UBase.IsStringNoneOrEmpty(self.__config.tuyooSdkDir) else self.__config.tuyooSdkDir
        lines.append(f'--tuyooSdkDir {tuyooSdkPath}')
        lines.append(f'--disableBuildTuyooAar false')
        lines.append(f'--cacheEnable false')

        lines.append(f'--gradlePath {self.__config.gradle.gradlePath}')
        lines.append(f'--sdkPath {self.__config.gradle.sdkPath}')
        lines.append(f'--ndkPath {self.__config.gradle.ndkPath}')
        lines.append(f'--jdkPath {self.__config.gradle.jdkPath}')
        lines.append(f'--antPath {self.__config.antPath}')

        lines.append(f'--python2Path {self.__config.python2Path}')

        for line in lines:
            UTracking.LogInfo('MAndroidAggregateSDK->MakeBuildParams', f'add line: {line}')

        result = UOS.SaveTextFile(path, lines)

        UTracking.LogInfo('MAndroidAggregateSDK->MakeBuildParams', 'end')
        return result

    def Exec(self, params : MAndroidAggregateSDKParams) -> bool:
        UTracking.LogInfo('MAndroidAggregateSDK->Exec', f'begin params: {UTracking.BeautifyLog(params.__dict__)}')

        if not UOS.IsFileExist(params.inputPath): 
            UTracking.LogError('MAndroidAggregateSDK->Exec', 'input path not existed: \'' + params.inputPath + '\'')
            return False

        buildParamsPath = self.__GetBuildParamsPath(params)
        if not UOS.IsFileExist(buildParamsPath): 
            UTracking.LogError('MAndroidAggregateSDK->Exec', 'build params path not existed: \'' + buildParamsPath + '\'')
            return False

        outputPath = self.GetOutputPackageDirectory(params)
        UOS.DeleteDirectory(outputPath)
        UOS.CreateDirectory(outputPath)
        
        packageType = 'apk' if params.APKOrAAB else 'aab'
        scriptPath = os.path.join(params.projectBuildPath, 'build.py')
        
        result = 0
        if BConstSystemPlatform == BPlatformEnum.OSX:
            result = UCommand.RunCmd(f'chmod +x {scriptPath}')
        else:
            UTracking.LogError('MAndroidAggregateSDK->Exec', 'Windows is not supported')
            result = 1

        if result == 0: 
            result = UCommand.RunPython(f'{scriptPath} {packageType} @{buildParamsPath}')

        UTracking.LogInfo('MAndroidAggregateSDK->Exec', 'end')
        return result == 0