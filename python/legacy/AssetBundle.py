from framework.utils import UJson
from framework.utils import UCompress
from framework.utils import UJenkinsArgs

from framework.modules.MNode import *
from framework.modules.MProject import *
from framework.modules.MGit import *
from framework.modules.MUnity import *
from framework.modules.MCDN import *
from framework.modules.MNFS import *

from product.config.CNodeProduct import *
from product.config.CGitProduct import *
from product.config.CUnityProduct import *
from product.config.CCDNProduct import *
from product.config.CNFSProduct import *

from product.modules.MVersionFile import *

def VerifyAssetBundles(abPath : str) -> bool:
    result = True
    
    for dir, dns, fns in os.walk(abPath):
        for dn in dns:
            if dn.find(' ') < 0: continue
            UTracking.LogError('AssetBundle->VerifyAssetBundles', f'Contains spaces, directory name: {dn}')
            result = False

        for fn in fns:
            if fn.find(' ') < 0: continue
            UTracking.LogError('AssetBundle->VerifyAssetBundles', f'Contains spaces, file name: {fn}')
            result = False

    return result

def MakeVersionFile(path : str, versionNumber : int, environment : CCDNEnvironmentEnum, server : str, platform : BPlatformEnum) -> bool:
    fileName = MVersionFile.Name()
    #
    cdn = MCDN(CCDNProduct())
    saveDirectory = path
    if not cdn.DownloadFile(fileName, saveDirectory, True, CCDNResourceEnum.Version.value, environment=environment.value, server=server, platform=platform.value): return False
    #    
    savedFile = os.path.join(saveDirectory, fileName)
    #
    versionFile = MVersionFile()
    if not versionFile.CreateFrom(savedFile): return False

    versionFile.MakeAssetBundle(str(versionNumber))
    
    if not versionFile.Save(): return False
    #
    UTracking.LogInfo('AssetBundle->MakeVersionFile', f'file: {savedFile}, version number: {versionNumber}')
    return True

def CopyVersionFiles(path : str, unityLocation : str, platform : BPlatformEnum):
    fileName = MVersionFile.Name()
    unityVersionDirectory = os.path.join(unityLocation, f'Assets/StreamingAssets/Config/Version/')
    #
    src = os.path.join(path, fileName)
    dest = os.path.join(unityVersionDirectory, f'{platform.value}/')
    if not UOS.CopyFile2D(src, dest, True): return False,unityVersionDirectory

    UTracking.LogInfo('AssetBundle->CopyVersionFiles', f'from: {src}, to: {dest}')
    return True,unityVersionDirectory

def ZipAssetBundle(abPath : str, zipPath : str) -> list:
    UTracking.LogInfo('AssetBundle->ZipAssetBundle', f'begin, from: {abPath}, to: {zipPath}')
    #
    constZipSizeLimit = 1024*1024*100
    constZipName = UOS.NameOfPath(abPath)
    allSize = 0
    allCount = 0
    allZipSize = 0
    zipFiles = []  
    zipSize = 0
    zipIndex = 0
    fileNames = []
    for dir, dns, fns in os.walk(abPath):
        for fn in fns:
            allCount += 1
            fp = os.path.join(dir, fn)
            rfp = os.path.relpath(fp, abPath)
            s = os.path.getsize(fp)
            allSize += s
            zipSize += s
            fileNames.append(rfp)
            if zipSize >= constZipSizeLimit:
                zipName = f'{constZipName}{zipIndex}.zip'
                zipFile = os.path.join(zipPath, zipName)
                if not UCompress.ZipFiles(True, abPath, fileNames, zipFile, False, True): 
                    UTracking.LogError('AssetBundle->ZipAssetBundle', f'Zip error, index: {zipIndex} count: {len(fileNames)} size: {zipSize} zip file: {zipFile} source: {UTracking.BeautifyLog(fileNames)}')
                    return None
                UTracking.LogInfo('AssetBundle->ZipAssetBundle', f'Zip once, index: {zipIndex} count: {len(fileNames)} size: {zipSize} zip file: {zipFile} source: {UTracking.BeautifyLog(fileNames)}')
                allZipSize += os.path.getsize(zipFile)
                zipFiles.append(zipName)
                zipSize = 0
                zipIndex += 1
                fileNames.clear()

    if len(fileNames) > 0:
        zipName = f'{constZipName}{zipIndex}.zip'
        zipFile = os.path.join(zipPath, zipName)
        if not UCompress.ZipFiles(True, abPath, fileNames, zipFile, False, True): 
            UTracking.LogError('AssetBundle->ZipAssetBundle', f'Zip error, index: {zipIndex} count: {len(fileNames)} size: {zipSize} zip file: {zipFile} source: {UTracking.BeautifyLog(fileNames)}')
            return None
        UTracking.LogInfo('AssetBundle->ZipAssetBundle', f'Zip once, index: {zipIndex} count: {len(fileNames)} size: {zipSize} zip file: {zipFile} source: {UTracking.BeautifyLog(fileNames)}')
        allZipSize += os.path.getsize(zipFile)
        zipFiles.append(zipName)
        zipSize = 0
        zipIndex += 1
        fileNames.clear()
        
    UTracking.LogInfo('AssetBundle->ZipAssetBundle', f'end, source count: {allCount} size: {allSize}, zip file count: {len(zipFiles)} size: {allZipSize}')
    return zipFiles

def UploadCDNAssetBundle(abPath : str, zipPath : str, versionNumber : int, environment : CCDNEnvironmentEnum, server : str, platform : BPlatformEnum) -> bool:
    zips = ZipAssetBundle(abPath, zipPath)
    if UBase.IsContainerNoneOrEmpty(zips): 
        UTracking.LogError('AssetBundle->UploadCDNAssetBundle', f'zips is empty')    
        return False
    #
    cdn = MCDN(CCDNProduct())
    if not cdn.UploadFilesInDirectory(zipPath, zips, True, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.AssetBundle.value, version=versionNumber, environment=environment.value, server=server, platform=platform.value):
        return False
    
    UTracking.LogInfo('AssetBundle->UploadCDNAssetBundle', f'zip count: {len(zips)}')    
    return True

def UploadCDNVersion(path : str, environment : CCDNEnvironmentEnum, server : str, platform : BPlatformEnum) -> bool:
    fileName = MVersionFile.Name()
    #
    cdn = MCDN(CCDNProduct())
    localPath = os.path.join(path, fileName)
    return cdn.UploadFile(localPath, False, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Version.value, environment=environment.value, server=server, platform=platform.value)

def CacheNFSAssetBundle(abPath : str, platform : BPlatformEnum, branch : str) -> bool:
    branchNormalized = UBase.ReplaceStrings(branch, ['.', ':', '-', '/', '\\'], '_')
    nfs = MNFS(CNFSProduct())
    if not nfs.DeleteDirectoryFromNFS(CNFSResourceEnum.AssetBundleCache.value, platform=platform.value, branch=branchNormalized): return False
    return nfs.CopyFilesToNFS(abPath, CNFSResourceEnum.AssetBundleCache.value, platform=platform.value, branch=branchNormalized)

def DoAction(configKey : str, platform : BPlatformEnum, args : dict):
    UTracking.LogInfo('AssetBundle->DoAction', UTracking.BeautifyLog(args))

    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('AssetBundle->DoAction', 'node not existed, key: ' + configKey)
    #
    node = MNode(config)
    project = node.GetIdleProject(platform, MProject.GetBusyMarkTag(args))
    if project is None:
        UTracking.RaiseException('AssetBundle->DoAction', 'no idle project existed, platform: ' + platform.value)
    #
    project.Begin()
    try:
        branch = args['branch']
        environment = CCDNEnvironmentEnum.FromS(args['environment'])
        server = UBase.ReplaceStrings(args['server'], ['.', ':', '-', '/', '\\'], '_')
        syncUnity = args['sync_unity']
        versionNumber = UDateTime.ToDateTimeSecond(args['time_stamp'])
        CSharpDefineSymbols = UBase.SplitString(args['csharp_define_symbols'], ',')
        #
        git = MGit(CGitProduct())        
        gitParamsUnity = MGitParams()
        project.SetupGitParams('Unity', gitParamsUnity)
        gitParamsUnity.branch = branch
        project.Check(git.CloneOrPull(gitParamsUnity), 'Git unity', args)
        unityLocation = gitParamsUnity.location
        #        
        unity = MUnity(CUnityProduct())
        unityParams = MUnityParams()
        project.SetupUnityParams(unityParams, MUnityPlatformEnum.From(platform))
        versionPath = os.path.join(unityParams.exportPath, 'Version/')
        zipPath = os.path.join(unityParams.exportPath, 'Zips/')
        assetBundlePath = os.path.join(unityParams.exportPath, 'AssetBundle/')
        ps = {
            'exportPath':assetBundlePath,
            'defineSymbols':CSharpDefineSymbols
        }
        unityParams.executeMethodParams = UJson.ToJson(ps)
        
        unityParams.executeMethod = 'EDCAssetBundleBuildToolWindow.PrepareBuildAssetBundleCommandLine'
        unityParams.logFile = 'AssetBundleLog_Prepare.txt'
        project.Check(unity.Exec(unityParams), 'Unity prepare', args)

        unityParams.executeMethod = 'EDCAssetBundleBuildToolWindow.BuildAssetBundleCommandLine'
        unityParams.logFile = 'AssetBundleLog_Build.txt'
        project.Check(unity.Exec(unityParams), 'Unity build', args)
        #
        project.Check(VerifyAssetBundles(assetBundlePath), 'Verify asset bundles', args)
        #
        project.Check(MakeVersionFile(versionPath, versionNumber, environment, server, platform), 'Make version file', args)
        #
        if syncUnity:
            CFResult, versionDirectory = CopyVersionFiles(versionPath, unityLocation, platform)
            project.Check(CFResult, 'Copy version files', args)
            project.Check(git.CommitAndPush(gitParamsUnity, 'Jenkins commit asset bundle', [versionDirectory]), 'Git unity commit', args)        
        #
        project.Check(UploadCDNAssetBundle(assetBundlePath, zipPath, versionNumber, environment, server, platform), 'Upload CDN asset bundle', args)
        project.Check(UploadCDNVersion(versionPath, environment, server, platform), 'Upload CDN version', args)
        # project.Check(CacheNFSAssetBundle(assetBundlePath, platform, branch), 'Cache NFS asset bundle', args)
    finally:
        project.End()

def main():
    # consoleTextPath = os.path.join(UOS.DirectoryOfPath(__file__), 'ConsoleText.txt')
    # UJenkinsArgs.Test_FillTestEnvironmentByConsoleTextFile(consoleTextPath)

    args = UJenkinsArgs.FromEnvironment([
        ('__Platform'           , 'platform'                , str   , 'error'                   ),
        ('__Branch'             , 'branch'                  , str   , 'error'                   ),
        ('__Environment'        , 'environment'             , str   , 'error'                   ),
        ('__Server'             , 'server'                  , str   , 'error'                   ),
        ('__SyncUnity'          , 'sync_unity'              , bool  , False                     ),
        ('BUILD_TIMESTAMP'      , 'time_stamp'              , str   , '2011-11-11 11:11:11 CST' ),
        ('__CSharpDefineSymbols', 'csharp_define_symbols'   , str   , ''                        )
    ])
    
    configKey = ''
    platform = BPlatformEnum.FromS(args['platform'])
    DoAction(configKey, platform, args)

if __name__ == '__main__':
    main()