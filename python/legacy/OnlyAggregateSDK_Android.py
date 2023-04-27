from framework.utils import UJson
from framework.utils import UJenkinsArgs
from framework.utils import UCompress

from framework.modules.MNode import *
from framework.modules.MProject import *
from framework.modules.MGit import *
from framework.modules.MUnity import *
from framework.modules.MAndroidStudio import *
from framework.modules.MAndroidAggregateSDK import *
from framework.modules.MNFS import *

from product.config.CNodeProduct import *
from product.config.CGitProduct import *
from product.config.CUnityProduct import *
from product.config.CAndroidStudioProduct import *
from product.config.CAndroidAggregateSDKProduct import *
from product.config.CNFSProduct import *

from product.modules.MVersionFile import *

def PickPackage(packageJobName : str, packageBuildNumber : int, packageName : str, localDirectory : str):
    nfs = MNFS(CNFSProduct())
    if not nfs.CopyFileFromNFS(localDirectory, packageName, CNFSResourceEnum.Archive.value, jobName=packageJobName, buildNumber=packageBuildNumber): return False, '', False
    #
    isAPK = UOS.IsSameExt(packageName, 'apk')
    isAAB = UOS.IsSameExt(packageName, 'aab')
    if not isAPK and not isAAB: return False, '', False

    packagePath = os.path.join(localDirectory, packageName)
    return True, packagePath, isAPK

def KeepArchive(packageDirectory : str, packageJobName : str, packageBuildNumber : int) -> bool:
    nfs = MNFS(CNFSProduct())
    return nfs.CopyFilesToNFS(packageDirectory, CNFSResourceEnum.Archive.value, jobName=packageJobName, buildNumber=packageBuildNumber)

def DoAction(configKey : str, platform : BPlatformEnum, args : dict):
    UTracking.LogInfo('OnlyAggregateSDK_Android->DoAction', UTracking.BeautifyLog(args))

    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('OnlyAggregateSDK_Android->DoAction', 'node not existed, key: ' + configKey)
    #
    node = MNode(config)
    project = node.GetIdleProject(platform, MProject.GetBusyMarkTag(args))
    if project is None:
        UTracking.RaiseException('OnlyAggregateSDK_Android->DoAction', 'no idle project existed, platform: ' + platform.value)
    #
    project.Begin()
    try:
        packageJobName = args['package_job_name']
        packageBuildNumber = args['package_build_number']
        packageName = args['package_name']
        aggregateSDKBranch = args['aggregate_sdk_branch']
        #
        git = MGit(CGitProduct())        

        gitParamsASDK = MGitParams()
        project.SetupGitParams('AggregateSDK', gitParamsASDK)
        gitParamsASDK.branch = aggregateSDKBranch
        project.Check(git.CloneOrPull(gitParamsASDK), 'Git aggregate sdk', args)
        aggregateSDKLocation = gitParamsASDK.location

        gitParamsASDKBuild = MGitParams()
        project.SetupGitParams('AggregateSDKBuild', gitParamsASDKBuild)
        gitParamsASDKBuild.branch = aggregateSDKBranch
        project.Check(git.CloneOrPull(gitParamsASDKBuild), 'Git aggregate sdk build', args)
        aggregateSDKBuildLocation = gitParamsASDKBuild.location
        #
        tempPath = os.path.join(project.GetTempLocation(), 'OnlyAggregateSDK_Android/')
        if UOS.IsDirectoryExist(tempPath):
            UOS.DeleteDirectory(tempPath)
        UOS.CreateDirectory(tempPath)

        result, packagePath, APKOrAAB = PickPackage(packageJobName, packageBuildNumber, packageName, tempPath)
        project.Check(result, 'Pick package', args)
        #
        androidAggregateSDKParams = MAndroidAggregateSDKParams()
        project.SetupAndroidAggregateSDKParams(androidAggregateSDKParams)
        androidAggregateSDKParams.inputPath = packagePath
        androidAggregateSDKParams.APKOrAAB = APKOrAAB
        androidAggregateSDKParams.projectPath = aggregateSDKLocation
        androidAggregateSDKParams.projectBuildPath = aggregateSDKBuildLocation

        androidAggregateSDK = MAndroidAggregateSDK(CAndroidAggregateSDKProduct())
        project.Check(androidAggregateSDK.MakeBuildParams(androidAggregateSDKParams), 'AndroidAggregateSDK make build params', args)
        project.Check(androidAggregateSDK.Exec(androidAggregateSDKParams), 'AndroidAggregateSDK build', args)
        sdkPackageDirectory = MAndroidAggregateSDK.GetOutputPackageDirectory(androidAggregateSDKParams)
        #
        project.Check(KeepArchive(sdkPackageDirectory, packageJobName, packageBuildNumber), 'Keep archives with sdk', args)
        #
    finally:
        project.End()

def main():
    # consoleTextPath = os.path.join(UOS.DirectoryOfPath(__file__), 'ConsoleText.txt')
    # UJenkinsArgs.Test_FillTestEnvironmentByConsoleTextFile(consoleTextPath)

    args = UJenkinsArgs.FromEnvironment([
        ('__PackageJobName'         , 'package_job_name'        , str   , ''        ),
        ('__PackageBuildNumber'     , 'package_build_number'    , int   , 0         ),
        ('__PackageName'            , 'package_name'            , str   , ''        ),
        ('__AggregateSDKBranch'     , 'aggregate_sdk_branch'    , str   , 'master'  )
    ])

    configKey = ''
    platform = BPlatformEnum.Android
    DoAction(configKey, platform, args)

if __name__ == '__main__':
    main()