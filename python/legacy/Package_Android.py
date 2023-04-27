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

def MakeBundleVersion(bundleVersion : str, buildNumber : int) -> str:
    ss = bundleVersion.split(".")
    if len(ss) < 3: return ""
    return f"{ss[0]}.{ss[1]}.{ss[2]}.{buildNumber}"

def MakeBundleVersionCode(bundleVersionCode : int, buildNumber : int) -> int:    
    return bundleVersionCode if bundleVersionCode > 0 else 1000000 + buildNumber

def VerifyValues(bundleVersion : str, bundleVersionCode : int) -> bool:
    UTracking.LogInfo('Package_Android->VerifyValues', f'bundleVersion: {bundleVersion}, bundleVersionCode: {bundleVersionCode}')
    if UBase.IsStringNoneOrEmpty(bundleVersion): return False
    if bundleVersionCode <= 0: return False
    return True

def ModifyVersionFile(unityLocation : str, server : str, cdn : str, cdn2 : str, appStoreURL : str):
    fileName = MVersionFile.Name()

    path = os.path.join(unityLocation, f'Assets/StreamingAssets/Config/Version/{BPlatformEnum.Android.value}/{fileName}')
    # if not UOS.IsFileExist(path): return False, path

    versionFile = MVersionFile()
    if not versionFile.CreateFrom(path): 
        UTracking.LogError('Package_Android->ModifyVersionFile', f'create version file failed, path: {path}')
        return False, path
    #
    ss = server.split('|')
    if len(ss) != 3:
        UTracking.LogError('Package_Android->ModifyVersionFile', f'parse server string failed, server string: {server}')
        return False, path

    domain = ss[0]
    ip = ss[1]
    port = ss[2]
    #
    versionFile.MakePackageAndroid(domain, ip, port, cdn, cdn2, appStoreURL)
    return versionFile.Save(), path

def GetAssetManifestContent(tempPath : str, platform : BPlatformEnum, branch : str):
    constFileName = 'Assets.bytes'

    nfs = MNFS(CNFSProduct())
    if not nfs.CopyFileFromNFS(tempPath, constFileName, CNFSResourceEnum.AssetBundleCache.value, platform=platform.value, branch=branch):        
        return None

    path = os.path.join(tempPath, constFileName)
    if not UOS.IsFileExist(path):
        UTracking.LogError('Package_Android->GetAssetManifestContent', f'not found {constFileName} path: {path}')
        return None

    src = UOS.LoadByteFile(path)
    oriLen = (src[0] << 24) | (src[1] << 16) | (src[2] << 8) | src[3]
    dest = UCompress.LZ4Decompress(src[4:], oriLen)
    json = dest.decode(encoding='utf-8')
    return UJson.FromJson(json)

def PickResources(tempPath : str, unityPath : str, packageResourceEmbed : BPackageResourceEmbedEnum, platform : BPlatformEnum, branch : str) -> bool:
    UTracking.LogInfo('Package_Android->PickResources', f'begin, package resource embed: {packageResourceEmbed.value}')
    #
    useAssetBundle = False
    fullAssetBundle = False
    if packageResourceEmbed == BPackageResourceEmbedEnum.ReleaseFull:
        useAssetBundle = True
        fullAssetBundle = True
    elif packageResourceEmbed == BPackageResourceEmbedEnum.Mini:
        useAssetBundle = True

    if not useAssetBundle:
        UTracking.LogInfo('Package_Android->PickResources', f'done, nothing to do')
        return True
    #
    srcRoot = os.path.join(unityPath, "Assets/BundleResources/Resources/")
    destRoot = os.path.join(unityPath, "Assets/BundleResources/Resources_1/")
    if UOS.IsDirectoryExist(destRoot):
        UOS.DeleteDirectory(destRoot)
    result = UOS.RenameDirectory(srcRoot, destRoot, True)
    if result:
        UTracking.LogInfo('Package_Android->PickResources', f'exclude resources folder, from: {srcRoot} to: {destRoot}')
    else:
        UTracking.LogError('Package_Android->PickResources', f'exclude resources folder failed, from: {srcRoot} to: {destRoot}')

    if not result: return False
    #
    branchNormalized = UBase.ReplaceStrings(branch, ['.', ':', '-', '/', '\\'], '_')
    nfs = MNFS(CNFSProduct())
    streamingAssetsPath = os.path.join(unityPath, 'Assets/StreamingAssets/')

    if fullAssetBundle:    
        result = nfs.CopyFilesFromNFS(streamingAssetsPath, CNFSResourceEnum.AssetBundleCache.value, platform=platform.value, branch=branchNormalized)
        if result:            
            UOS.DeleteFile(os.path.join(streamingAssetsPath, 'AssetBundle'))
            UOS.DeleteFile(os.path.join(streamingAssetsPath, 'AssetBundle.manifest'))
    else:
        content = GetAssetManifestContent(tempPath, platform, branchNormalized)
        if UBase.IsContainerNoneOrEmpty(content):
            result = False
            UTracking.LogError('Package_Android->PickResources', f'load asset manifest failed')
        else:            
            nodes = content.get('nodes')
            if UBase.IsContainerNoneOrEmpty(nodes):
                result = False
                UTracking.LogError('Package_Android->PickResources', f'asset manifest nodes is empty')
            else:
                fileNames = []
                for node in nodes:
                    extractFromPackage = node.get('extractFromPackage')
                    if extractFromPackage is None: continue
                    if not extractFromPackage: continue
                    id = node.get('id')
                    if UBase.IsStringNoneOrEmpty(id): continue
                    fileNames.append(id)                    
                
                if (len(fileNames) <= 0):
                    UTracking.LogInfo('Package_Android->PickResources', f'done, no asset bundle to pick')
                else:
                    for fn in fileNames:        
                        result = nfs.CopyFileFromNFS(streamingAssetsPath, fn, CNFSResourceEnum.AssetBundleCache.value, platform=platform.value, branch=branchNormalized)
                        if not result: break

    UTracking.LogInfo('Package_Android->PickResources', f'end')
    #
    return result

def PickHotfix(unityPath : str, packageResourceEmbed : BPackageResourceEmbedEnum, platform : BPlatformEnum, branch : str) -> bool:
    UTracking.LogInfo('Package_Android->PickHotfix', f'begin, package resource embed: {packageResourceEmbed.value}')
    #
    useHotfix = False
    if packageResourceEmbed == BPackageResourceEmbedEnum.ReleaseFull:
        useHotfix = True
    elif packageResourceEmbed == BPackageResourceEmbedEnum.Mini:
        useHotfix = True

    if not useHotfix:
        UTracking.LogInfo('Package_Android->PickHotfix', f'done, nothing to do')
        return True
    #
    branchNormalized = UBase.ReplaceStrings(branch, ['.', ':', '-', '/', '\\'], '_')
    nfs = MNFS(CNFSProduct())
    targetPath = os.path.join(unityPath, f'Assets/StreamingAssets/Hotfix/{platform.value}')

    result = nfs.CopyFilesFromNFS(targetPath, CNFSResourceEnum.HotfixCache.value, platform=platform.value, branch=branchNormalized)
    UTracking.LogInfo('Package_Android->PickHotfix', f'end')
    #
    return result

def RenamePackages(packageDirectory : str, branch : str, buildNumber : int, bundleVersionCode : int, bundleVersion : str):
    branch = UBase.ReplaceStrings(branch, [':', '/', '\\'], '_')

    count = 0
    for dir, dns, fns in os.walk(packageDirectory):
        for fn in fns:
            fp = os.path.join(dir, fn)
            
            same = UOS.IsSameExt(fp, 'apk') or UOS.IsSameExt(fp, 'aab')
            if not same: continue

            nfp = UOS.ChangeFileName(fp, f'__{branch}_{buildNumber}_{bundleVersion}_{bundleVersionCode}')
            if UOS.IsFileExist(nfp):
                UOS.DeleteFile(nfp)
            if UOS.RenameFile(fp, nfp, True):
                UTracking.LogInfo('Package_Android->RenamePackages', f'from: {fp}, to: {nfp}')                
            else:
                UTracking.LogWarning('Package_Android->RenamePackages', f'failed, keep old: {fp}')

            count += 1

    if count <= 0:
        UTracking.LogWarning('Package_Android->RenamePackages', f'no files need to be renamed')

def KeepArchive(packageDirectory : str, cleanDest : bool, jobName : str, buildNumber : int) -> bool:
    nfs = MNFS(CNFSProduct())
    if cleanDest:
        if not nfs.DeleteDirectoryFromNFS(CNFSResourceEnum.Archive.value, jobName=jobName, buildNumber=buildNumber): return False
    return nfs.CopyFilesToNFS(packageDirectory, CNFSResourceEnum.Archive.value, jobName=jobName, buildNumber=buildNumber)

def DoAction(configKey : str, platform : BPlatformEnum, args : dict):
    UTracking.LogInfo('Package_Android->DoAction', UTracking.BeautifyLog(args))

    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('Package_Android->DoAction', 'node not existed, key: ' + configKey)
    #
    node = MNode(config)
    project = node.GetIdleProject(platform, MProject.GetBusyMarkTag(args))
    if project is None:
        UTracking.RaiseException('Package_Android->DoAction', 'no idle project existed, platform: ' + platform.value)
    #
    project.Begin()
    try:
        branch = args['branch']
        packageType = BPackageTypeEnum.FromS(args['package_type'])
        packagePurpose = BPackagePurposeEnum.FromS(args['package_purpose'])
        jobName = args['job_name']
        buildNumber = args['build_number']
        bundleVersion = MakeBundleVersion(args['bundle_version'], buildNumber)
        bundleVersionCode = MakeBundleVersionCode(args['bundle_version_code'], buildNumber)
        packageResourceEmbed = BPackageResourceEmbedEnum.FromS(args['resource_embed'])
        server = args['server']
        cdn = args['cdn']
        cdn2 = args['cdn2']        
        generateSymbolTable = args['generate_symbol_table']
        appStoreURL = args['app_store_url']
        showLoginUI = args['show_login_ui']
        developmentBuild = args['development_build']
        il2cpp = args['il2cpp']
        CSharpDefineSymbols = UBase.SplitString(args['csharp_define_symbols'], ',')
        version2git = args['version2git']
        aggregateSDK = args['aggregate_sdk']
        aggregateSDKBranch = args['aggregate_sdk_branch'] 

        APKOrAAB = True if packageType == BPackageTypeEnum.APK else False
        releaseMode = True if packagePurpose == BPackagePurposeEnum.Publish else False
        #
        git = MGit(CGitProduct())
        
        gitParamsUnity = MGitParams()
        project.SetupGitParams('Unity', gitParamsUnity)
        gitParamsUnity.branch = branch
        project.Check(git.CloneOrPull(gitParamsUnity), 'Git unity', args)
        unityLocation = gitParamsUnity.location

        aggregateSDKLocation = ''
        aggregateSDKBuildLocation = ''
        if aggregateSDK:
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
        project.Check(VerifyValues(bundleVersion, bundleVersionCode), 'Verify values', args)
        MVFResult, MVFPath = ModifyVersionFile(unityLocation, server, cdn, cdn2, appStoreURL)
        project.Check(MVFResult, 'Modify version file', args)
        if version2git:
            project.Check(git.CommitAndPush(gitParamsUnity, 'Jenkins commit package android', [MVFPath]), 'Git unity commit', args)
        #
        # tempPath = os.path.join(project.GetTempLocation(), 'PackageAndroid/')
        # if UOS.IsDirectoryExist(tempPath):
        #     UOS.DeleteDirectory(tempPath)
        # UOS.CreateDirectory(tempPath)
        # project.Check(PickResources(tempPath, unityLocation, packageResourceEmbed, platform, branch), 'Pick resources', args)
        # project.Check(PickHotfix(unityLocation, packageResourceEmbed, platform, branch), 'Pick hotfix', args)
        #        
        unity = MUnity(CUnityProduct())
        unityParams = MUnityParams()
        project.SetupUnityParams(unityParams, MUnityPlatformEnum.From(platform))        
        ps = {
            'apk_aab':APKOrAAB,
            'bundleVersion':bundleVersion,
            'bundleVersionCode':bundleVersionCode,
            'releaseMode':releaseMode,            
            'resourceEmbed':packageResourceEmbed.value,
            'showLoginUI':showLoginUI,
            'developmentBuild':developmentBuild,
            'il2cpp':il2cpp,
            'exportProject':True,
            'outputPath':unityParams.exportPath,
            'defineSymbols':CSharpDefineSymbols
        }
        unityParams.executeMethodParams = UJson.ToJson(ps)
        
        unityParams.executeMethod = 'AutoBuilder.PrepareBuildAndroidCommandLine'
        unityParams.logFile = 'BuildLog_Prepare.txt'
        unityParams.clearScriptAssemblies = True
        project.Check(unity.Exec(unityParams), 'Unity prepare', args)

        unityParams.executeMethod = 'AutoBuilder.BuildAndroidCommandLine'
        unityParams.logFile = 'BuildLog_Build.txt'
        unityParams.clearScriptAssemblies = False
        project.Check(unity.Exec(unityParams), 'Unity build', args)
        #
        androidStudioParams = MAndroidStudioParams()
        project.SetupAndroidStudioParams(androidStudioParams)
        androidStudioParams.APKOrAAB = APKOrAAB
        androidStudioParams.bundleVersion = bundleVersion
        androidStudioParams.bundleVersionCode = bundleVersionCode
        androidStudioParams.releaseMode = True #releaseMode
        androidStudioParams.generateSymbolTable = generateSymbolTable        

        androidStudio = MAndroidStudio(CAndroidStudioProduct())
        project.Check(androidStudio.ModifyMainGradle(androidStudioParams), 'AndroidStudio modify main gradle', args)        
        project.Check(androidStudio.ModifyLauncherGradle(androidStudioParams), 'AndroidStudio modify launcher gradle', args)
        project.Check(androidStudio.ModifyUnityLibraryGradle(androidStudioParams), 'AndroidStudio modify unity library gradle', args)        
        project.Check(androidStudio.ModifyLocalProperties(androidStudioParams), 'AndroidStudio modify localProperties', args)
        project.Check(androidStudio.Exec(androidStudioParams), 'AndroidStudio build', args)
        #
        rawPackageDirectory = MAndroidStudio.GetOutputPackageDirectory(androidStudioParams)
        sdkPackageDirectory = ""
        #
        if aggregateSDK:
            project.Check(KeepArchive(rawPackageDirectory, True, jobName, buildNumber), 'Keep archives raw', args)
        #
        if aggregateSDK:
            androidAggregateSDKParams = MAndroidAggregateSDKParams()
            project.SetupAndroidAggregateSDKParams(androidAggregateSDKParams)
            androidAggregateSDKParams.inputPath = MAndroidStudio.GetOutputPackagePath(androidStudioParams)
            androidAggregateSDKParams.APKOrAAB = APKOrAAB
            androidAggregateSDKParams.projectPath = aggregateSDKLocation
            androidAggregateSDKParams.projectBuildPath = aggregateSDKBuildLocation

            androidAggregateSDK = MAndroidAggregateSDK(CAndroidAggregateSDKProduct())
            project.Check(androidAggregateSDK.MakeBuildParams(androidAggregateSDKParams), 'AndroidAggregateSDK make build params', args)
            project.Check(androidAggregateSDK.Exec(androidAggregateSDKParams), 'AndroidAggregateSDK build', args)
            sdkPackageDirectory = MAndroidAggregateSDK.GetOutputPackageDirectory(androidAggregateSDKParams)
        #
        if aggregateSDK:
            RenamePackages(sdkPackageDirectory, branch, buildNumber, bundleVersionCode, bundleVersion)#not do check, cuo le jiu cuo le
            project.Check(KeepArchive(sdkPackageDirectory, False, jobName, buildNumber), 'Keep archives with sdk', args)
        else:
            RenamePackages(rawPackageDirectory, branch, buildNumber, bundleVersionCode, bundleVersion)#not do check, cuo le jiu cuo le
            project.Check(KeepArchive(rawPackageDirectory, True, jobName, buildNumber), 'Keep archives raw', args)           
        #
    finally:
        project.End()

def main():
    # consoleTextPath = os.path.join(UOS.DirectoryOfPath(__file__), 'ConsoleText.txt')
    # UJenkinsArgs.Test_FillTestEnvironmentByConsoleTextFile(consoleTextPath)

    args = UJenkinsArgs.FromEnvironment([
        ('__Branch'                 , 'branch'                  , str   , 'error'       ),
        ('__PackageType'            , 'package_type'            , str   , 'error'       ),
        ('__PackagePurpose'         , 'package_purpose'         , str   , 'error'       ),
        ('__BundleVersion'          , 'bundle_version'          , str   , '1.0.0.0'     ),
        ('__BundleVersionCode'      , 'bundle_version_code'     , int   , 0             ),
        ('__ResourceEmbed'          , 'resource_embed'          , str   , 'error'       ),
        ('__Server'                 , 'server'                  , str   , 'error'       ),
        ('__CDN'                    , 'cdn'                     , str   , 'error'       ),
        ('__CDN2'                   , 'cdn2'                    , str   , 'error'       ),
        ('__GenerateSymbolTable'    , 'generate_symbol_table'   , bool  , False         ),
        ('__AppStoreURL'            , 'app_store_url'           , str   , 'error'       ),
        ('__ShowLoginUI'            , 'show_login_ui'           , bool  , False         ),
        ('__DevelopmentBuild'       , 'development_build'       , bool  , False         ),
        ('__IL2CPP'                 , 'il2cpp'                  , bool  , True          ),
        ('__CSharpDefineSymbols'    , 'csharp_define_symbols'   , str   , ''            ),
        ('__Version2Git'            , 'version2git'             , bool  , False         ),
        ('__AggregateSDK'           , 'aggregate_sdk'           , bool  , False         ),
        ('__AggregateSDKBranch'     , 'aggregate_sdk_branch'    , str   , 'master'      ),
        ('BUILD_NUMBER'             , 'build_number'            , int   , 0             ),
        ('JOB_NAME'                 , 'job_name'                , str   , 'error'       ),
    ])

    configKey = ''
    platform = BPlatformEnum.Android
    DoAction(configKey, platform, args)

if __name__ == '__main__':
    main()