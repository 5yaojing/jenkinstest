from enum import Enum
from ..utils import UOS
from ..utils import UCommand
from ..utils import UTracking
from ..config.CXCode import *

class MXCodeConfigurationEnum(Enum):
    Debug               = 'Debug'
    Release             = 'Release'
    ReleaseForProfiling = 'ReleaseForProfiling'
    ReleaseForRunning   = 'ReleaseForRunning'

class MXCodeSDKEnum(Enum):
    IOS11_0             = 'iphoneos11.0'

class MXCodeUploadTypeEnum(Enum):
    MacOS               = 'macos'
    IOS                 = 'ios'
    AppleTVOS           = 'appletvos'

class MXCodeParams:
    workspace = False
    projectPath = 'Unity-iPhone.xcodeproj or xxx.workspace'
    #
    scheme = 'Unity-iPhone'
    configuration = MXCodeConfigurationEnum.Debug
    sdk = MXCodeSDKEnum.IOS11_0
    archivePath = 'xxx/yyy.xcarchive'
    exportPath = 'xxx/yyy/build/'
    exportOptionsPlist = 'xxx/yyy/info.plist'
    #
    publish = False
    publishUploadType = MXCodeUploadTypeEnum.IOS
    publishWithAPIKeyOrAccount = False
    
class MXCode:
    __config : CXCode = None
    ################################################################ 
    def __init__(self, config : CXCode):
        if config is None:
            UTracking.RaiseException('MXCode->__init__', 'config is none')
        self.__config = config
    ################################################################
    def __ShowSDK(self) -> bool:
        cmd = 'xcodebuild -showsdks'
        result = UCommand.RunCmd(cmd)
        return result == 0

    def __Clean(self, params : MXCodeParams) -> bool:
        cmd = 'xcodebuild clean'
        
        if params.workspace:
            cmd = ' -workspace ' + params.projectPath
        else:
            cmd = ' -project ' + params.projectPath
        
        cmd += ' -scheme ' + params.scheme
        cmd += ' -configuration ' + params.configuration.name
        cmd += ' -sdk ' + params.sdk.name

        result = UCommand.RunCmd(cmd)
        return result == 0

    def __Build(self, params : MXCodeParams) -> bool:
        cmd = 'xcodebuild build'
        
        if params.workspace:
            cmd = ' -workspace ' + params.projectPath
        else:
            cmd = ' -project ' + params.projectPath
        
        cmd += ' -scheme ' + params.scheme
        cmd += ' -configuration ' + params.configuration.name
        cmd += ' -sdk ' + params.sdk.name

        result = UCommand.RunCmd(cmd)
        return result == 0

    def __Archive(self, params : MXCodeParams) -> bool:
        cmd = 'xcodebuild archive'
        
        if params.workspace:
            cmd = ' -workspace ' + params.projectPath
        else:
            cmd = ' -project ' + params.projectPath
        
        cmd += ' -scheme ' + params.scheme
        cmd += ' -configuration ' + params.configuration.name
        cmd += ' -sdk ' + params.sdk.name
        cmd += ' -archivePath ' + params.archivePath

        result = UCommand.RunCmd(cmd)
        return result == 0

    def __ExportIPA(self, params : MXCodeParams) -> bool:
        cmd = 'xcodebuild -exportArchive'
        cmd += ' -archivePath ' + params.archivePath
        cmd += ' -exportPath ' + params.exportPath
        cmd += ' -exportOptionsPlist ' + params.exportOptionsPlist

        result = UCommand.RunCmd(cmd)
        return result == 0

    def __Validate(self, params : MXCodeParams) -> bool:
        cmd = 'xcrun altool --validate-app'
        cmd += ' -f ' + params.exportPath
        cmd += ' -t ' + params.publishUploadType

        if params.publishWithAPIKeyOrAccount:
            cmd += ' --apiKey ' + self.__config.apiKey
            cmd += ' --apiIssuer ' + self.__config.apiIssuer
        else:
            cmd += ' -u ' + self.__config.account_Publish
            cmd += ' -p ' + self.__config.password_Publish

    def __UploadApp(self, params : MXCodeParams) -> bool:
        cmd = 'xcrun altool --upload-app'
        cmd += ' -f ' + params.exportPath
        cmd += ' -t ' + params.publishUploadType

        if params.publishWithAPIKeyOrAccount:
            cmd += ' --apiKey ' + self.__config.apiKey
            cmd += ' --apiIssuer ' + self.__config.apiIssuer
        else:
            cmd += ' -u ' + self.__config.account_Publish
            cmd += ' -p ' + self.__config.password_Publish

    def __UploadPackage(self, params : MXCodeParams) -> bool:
        cmd = 'xcrun altool --upload-package'
        cmd += ' -f ' + params.exportPath
        cmd += ' -t ' + params.publishUploadType

        cmd += ' --asc-public-id ' + 'id'
        cmd += ' --apple-id ' + 'id'
        cmd += ' --bundle-version ' + 'version'
        cmd += ' --bundle-short-version-string ' + 'string'
        cmd += ' --bundle-id ' + 'id'

        if params.publishWithAPIKeyOrAccount:
            cmd += ' --apiKey ' + self.__config.apiKey
            cmd += ' --apiIssuer ' + self.__config.apiIssuer
        else:
            cmd += ' -u ' + self.__config.account_Publish
            cmd += ' -p ' + self.__config.password_Publish

    ################################################################
    def Exec(self, params : MXCodeParams) -> bool:
        #http://t.zoukankan.com/liuluoxing-p-8622108.html
        #PROVISIONING_PROFILE=<profileuuid>
        UTracking.LogInfo('MXCode->Exec', f'begin params: {UTracking.BeautifyLog(params.__dict__)}')

        if not UOS.IsFileExist(params.projectPath): 
            UTracking.LogError('MXCode->Exec', 'project path not existed')
            return False

        # if not UOS.IsDirectoryExist(params.outputPath):
        #     UOS.CreateDirectory(sparams.outputPath)
        #     UTracking.LogInfo('MUnity->Exec', 'create output diretory: ' + params.outputPath)
        
        if not self.__ShowSDK():
            UTracking.LogError('MXCode->Exec', 'show sdk failed')
            return False

        if not self.__Clean(params): 
            UTracking.LogError('MXCode->Exec', 'clean failed')
            return False

        if not self.__Build(params): 
            UTracking.LogError('MXCode->Exec', 'build failed')
            return False

        if not self.__Archive(params): 
            UTracking.LogError('MXCode->Exec', 'archive failed')
            return False

        if not self.__ExportIPA(params): 
            UTracking.LogError('MXCode->Exec', 'export IPA failed')
            return False

        if params.publish:            
            if not self.__Validate(params): 
                UTracking.LogError('MXCode->Exec', 'validate failed')
                return False

            if not self.__UploadApp(params): 
                UTracking.LogError('MXCode->Exec', 'upload  failed')
                return False
        
        UTracking.LogInfo('MXCode->Exec', 'end')
        return True