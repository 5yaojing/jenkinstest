from framework.utils import UJson
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

    versionFile.MakeHotfix(str(versionNumber))
    
    if not versionFile.Save(): return False
    #
    UTracking.LogInfo('Hotfix->MakeVersionFile', f'file: {savedFile}, version number: {versionNumber}')
    return True

def CopyVersionFiles(path : str, unityLocation : str, platform : BPlatformEnum):
    fileName = MVersionFile.Name()
    unityVersionDirectory = os.path.join(unityLocation, f'Assets/StreamingAssets/Config/Version/')
    #
    src = os.path.join(path, fileName)
    dest = os.path.join(unityVersionDirectory, f'{platform.value}/')
    if not UOS.CopyFile2D(src, dest, True): return False,unityVersionDirectory

    UTracking.LogInfo('Hotfix->CopyVersionFiles', f'from: {src}, to: {dest}')
    return True,unityVersionDirectory

def UploadCDNHotfix(hotfixPath : str, versionNumber : int, environment : CCDNEnvironmentEnum, server : str, platform : BPlatformEnum) -> bool:
    hotfixs = []
    allSize = 0
    for dir, dns, fns in os.walk(hotfixPath):        
        for fn in fns:
            fp = os.path.join(dir, fn)
            rfp = os.path.relpath(fp, hotfixPath)
            s = os.path.getsize(fp)
            allSize += s
            hotfixs.append(fp)
    #
    if UBase.IsContainerNoneOrEmpty(hotfixs): 
        UTracking.LogError('Hotfix->UploadCDNHotfix', f'hotfixs is empty')    
        return False
    #
    cdn = MCDN(CCDNProduct())
    if not cdn.UploadFiles(hotfixs, False, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Hotfix.value, version=versionNumber, environment=environment.value, server=server, platform=platform.value):
        return False
    
    UTracking.LogInfo('Hotfix->UploadCDNHotfix', f'hotfix count: {len(hotfixs)} size: {allSize}')    
    return True

def UploadCDNVersion(path : str, environment : CCDNEnvironmentEnum, server : str, platform : BPlatformEnum) -> bool:
    fileName = MVersionFile.Name()
    #
    cdn = MCDN(CCDNProduct())    
    localPath = os.path.join(path, fileName)
    return cdn.UploadFile(localPath, False, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Version.value, environment=environment.value, server=server, platform=platform.value)

def CacheNFSHotfix(path : str, platform : BPlatformEnum, branch : str) -> bool:
    branchNormalized = UBase.ReplaceStrings(branch, ['.', ':', '-', '/', '\\'], '_')
    nfs = MNFS(CNFSProduct())
    if not nfs.DeleteDirectoryFromNFS(CNFSResourceEnum.HotfixCache.value, platform=platform.value, branch=branchNormalized): return False
    return nfs.CopyFilesToNFS(path, CNFSResourceEnum.HotfixCache.value, platform=platform.value, branch=branchNormalized)

def DoAction(configKey : str, platform : BPlatformEnum, args : dict):
    UTracking.LogInfo('Hotfix->DoAction', UTracking.BeautifyLog(args))

    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('Hotfix->DoAction', 'node not existed, key: ' + configKey)
    #
    node = MNode(config)
    project = node.GetIdleProject(platform, MProject.GetBusyMarkTag(args))
    if project is None:
        UTracking.RaiseException('Hotfix->DoAction', 'no idle project existed, platform: ' + platform.value)
    #
    project.Begin()
    try:
        branch = args['branch']
        environment = CCDNEnvironmentEnum.FromS(args['environment'])
        server = UBase.ReplaceStrings(args['server'], ['.', ':', '-', '/', '\\'], '_')
        includeAotDll = args['include_aot_dll']
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
        hotfixPath = os.path.join(unityParams.exportPath, 'Hotfix/')
        ps = {
            'includeAotDll':includeAotDll,
            'exportPath':hotfixPath,
            'defineSymbols':CSharpDefineSymbols
        }
        unityParams.executeMethodParams = UJson.ToJson(ps)
        
        unityParams.executeMethod = 'EDCTools.PrepareCompileDllCommandLine'
        unityParams.logFile = 'Hotfix_Prepare.txt'
        project.Check(unity.Exec(unityParams), 'Unity prepare', args)

        unityParams.executeMethod = 'EDCTools.CompileDllCommandLine'
        unityParams.logFile = 'Hotfix_Build.txt'
        project.Check(unity.Exec(unityParams), 'Unity build', args)
        #
        project.Check(MakeVersionFile(versionPath, versionNumber, environment, server, platform), 'Make version file', args)
        #
        if syncUnity:
            CFResult, versionDirectory = CopyVersionFiles(versionPath, unityLocation, platform)
            project.Check(CFResult, 'Copy version files', args)
            project.Check(git.CommitAndPush(gitParamsUnity, 'Jenkins commit hotfix', [versionDirectory]), 'Git unity commit', args)        
        #
        project.Check(UploadCDNHotfix(hotfixPath, versionNumber, environment, server, platform), 'Upload CDN hotfix', args)
        project.Check(UploadCDNVersion(versionPath, environment, server, platform), 'Upload CDN version', args)
        # project.Check(CacheNFSHotfix(hotfixPath, platform, branch), 'Cache NFS hotfix', args)
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
        ('__IncludeAotDll'      , 'include_aot_dll'         , bool  , False                     ),
        ('__SyncUnity'          , 'sync_unity'              , bool  , False                     ),
        ('BUILD_TIMESTAMP'      , 'time_stamp'              , str   , '2011-11-11 11:11:11 CST' ),
        ('__CSharpDefineSymbols', 'csharp_define_symbols'   , str   , ''                        )
    ])
    
    configKey = ''
    platform = BPlatformEnum.FromS(args['platform'])
    DoAction(configKey, platform, args)

if __name__ == '__main__':
    main()