import time
from framework.utils import UJson
from framework.utils import UEncrypt
from framework.utils import UJenkinsArgs

from framework.modules.MNode import *
from framework.modules.MProject import *
from framework.modules.MGit import *
from framework.modules.MUnity import *
from framework.modules.MAndroidStudio import *
from framework.modules.MXCode import *
from framework.modules.MCDN import *
from framework.modules.MDingDing import *

from product.config.CNodeProduct import *
from product.config.CGitProduct import *
from product.config.CUnityProduct import *
from product.config.CXCodeProduct import *
from product.config.CAndroidStudioProduct import *
from product.config.CDingDingProduct import *
from product.config.CCDNProduct import *
from product.config.CAppStoreProduct import *

def DoAction(configKey : str, platform : BPlatformEnum, args : dict):
    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('Test->DoAction', 'node not existed, key: ' + configKey)
    #
    node = MNode(config)
    project = node.GetIdleProject(platform, MProject.GetBusyMarkTag(args))
    if project is None:
        UTracking.RaiseException('Test->DoAction', 'no idle project existed, platform: ' + platform.value)
    #
    project.Begin()    
    try:
        branch = args['branch']
        UTracking.LogInfo('Test->DoAction1', 'start sleep你好么')
        # time.sleep(30)
        UTracking.LogInfo('Test->DoAction2', 'end sleep你好么')
        # #
        # gitParams = MGitParams()
        # project.SetupGitParams('Unity', gitParams)
        # gitParams.branch = branch
        # git = MGit(CGitProduct())
        # project.Check(git.CloneOrPull(gitParams), 'Git')
        #
        # androidStudioParams = MAndroidStudioParams()
        # project.SetupAndroidStudioParams(androidStudioParams)
        # androidStudioParams.APKOrAAB = False
        # androidStudioParams.releaseMode = False
        # #
        # outputPath = androidStudioParams.projectPath  
        # #
        # unityParams = MUnityParams()
        # project.SetupUnityParams(unityParams)        
        # unityParams.buildTarget = MUnityPlatformEnum.From(platform)
        # unityParams.executeMethod = 'Builder.BuildAndroid'
        # unityParams.executeMethodParams = UJson.ToJson({'apk_aab':androidStudioParams.APKOrAAB, 'release':androidStudioParams.releaseMode, 'il2cpp':True, 'exportProject':True, 'outputPath':outputPath})
        # #
        # if UOS.IsDirectoryExist(outputPath):
        #     UOS.DeleteDirectory(outputPath)
        #     UTracking.LogInfo('Test->DoAction', 'delete output directory: ' + outputPath)
        # #
        # unity = MUnity(CUnityProduct())
        # project.Check(unity.Exec(unityParams), 'Unity')
        # #        
        # androidStudio = MAndroidStudio(CAndroidStudioProduct())
        # project.Check(androidStudio.Exec(androidStudioParams), 'AndroidStudio')
        # #
        # xcodeParams = MXCodeParams()
        # project.SetupXCodeParams(xcodeParams)
        # xcode = MXCode(CXCodeProduct())
        # project.Check(xcode.Exec(xcodeParams), 'XCode')
        # #
        # cdn = MCDN(CCDNProduct())
        # cdn.UploadFile('D:/Node/Projects/1234567.txt', False, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Meta.value, server='Test' platform=CCDNPlatformEnum.Android.value)
        # cdn.UploadFile('D:/Node/Projects/abc.zip', True, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Meta.value, server='Test', platform=CCDNPlatformEnum.Android.value)
        # cdn.UploadDirectory('D:/Node/Projects/abcdefg/', CCDNProjectEnum.XProject.value, CCDNResourceEnum.Meta.value, server='Test', platform=CCDNPlatformEnum.Android.value)
        # cdn.UploadFiles(['D:/Node/Projects/defg/d.txt', 'D:/Node/Projects/defg/ef/e.txt', 'D:/Node/Projects/defg/ef/f.txt', 'D:/Node/Projects/defg/g/g.txt'], CCDNProjectEnum.XProject.value, CCDNResourceEnum.Meta.value, server='Test', platform=CCDNPlatformEnum.Android.value)
        # #
        # dingding = MDingDing(CDingDingProduct())
        # dingding.SendMessage('All', '这是Python主动调通知的钉钉, 不是Job执行的结果!')
    finally:
        project.End()

def main():

    invokeByJenkins = False
    manualOrConsoleText = True
    if not invokeByJenkins:
        if manualOrConsoleText:
            UJenkinsArgs.Test_FillEnvironmentByManual({
                '__Branch':'BranchName'
            })
        else:
            consoleTextPath = os.path.join(UOS.DirectoryOfPath(__file__), 'ConsoleText.txt')
            UJenkinsArgs.Test_FillTestEnvironmentByConsoleTextFile(consoleTextPath)   

    args = UJenkinsArgs.FromEnvironment([
        ('__Branch', 'branch', str, 'error')
    ])

    configKey = ''
    platform = BPlatformEnum.Android 
    DoAction(configKey, platform, args)

if __name__ == '__main__':
    main()