from framework.basic.BConstant import *
from framework.utils import UJson
from framework.utils import UDateTime
from framework.utils import UJenkinsArgs
from framework.modules.MNode import *
from framework.modules.MProject import *
from framework.modules.MGit import *
from framework.modules.MUnity import *
from framework.modules.MCDN import *

from product.config.CNodeProduct import *
from product.config.CGitProduct import *
from product.config.CUnityProduct import *
from product.config.CCDNProduct import *

from product.modules.MVersionFile import *

def RunInternalScripts(processMeta : bool, processLocale : bool, metadataLocation : str) -> bool:
    scriptExport = ''
    if BConstSystemPlatform == BPlatformEnum.OSX:
        scriptExport = './export.sh'
    elif BConstSystemPlatform == BPlatformEnum.Windows:
        scriptExport = 'export.bat'
    else:
        UTracking.RaiseException('MetaAndLocale->RunInternalScripts', 'Unsupported system platform: ' + BConstSystemPlatform)
    #
    os.chdir(metadataLocation)
    os.chdir('./Tools')

    arg1 = '1' if processMeta else '0'
    arg2 = '1' if processLocale else '0'

    result = 0
    if BConstSystemPlatform == BPlatformEnum.OSX:
        result = UCommand.RunCmd(f'chmod +x {scriptExport}')
    if result == 0:
        result = UCommand.RunCmd(f'{scriptExport} {arg1} {arg2}')
    return result == 0


def MakeVersionFile(processMeta : bool, processLocale : bool, path : str, versionNumber : int, languages : str) -> bool:
    versionFile = MVersionFile()
    if not versionFile.CreateFrom(path): return False

    if processMeta:
        versionFile.MakeMeta(str(versionNumber))

    if processLocale:
        versionFile.MakeLocale(str(versionNumber))
        versionFile.MakeLanguages(languages)
    
    return versionFile.Save()

def MakeVersionFiles(processMeta : bool, processLocale : bool, metadataLocation : str, versionNumber : int, environment : CCDNEnvironmentEnum, server : str, languages : str) -> bool:
    fileName = MVersionFile.Name()
    #
    cdn = MCDN(CCDNProduct())
    saveDirectory0 = os.path.join(metadataLocation, f'Tools/configM/{BPlatformEnum.Standalone.value}/')
    if not cdn.DownloadFile(fileName, saveDirectory0, True, CCDNResourceEnum.Version.value, environment=environment.value, server=server, platform=BPlatformEnum.Standalone.value): return False

    saveDirectory1 = os.path.join(metadataLocation, f'Tools/configM/{BPlatformEnum.Android.value}/')
    if not cdn.DownloadFile(fileName, saveDirectory1, True, CCDNResourceEnum.Version.value, environment=environment.value, server=server, platform=BPlatformEnum.Android.value): return False

    saveDirectory2 = os.path.join(metadataLocation, f'Tools/configM/{BPlatformEnum.IOS.value}/')
    if not cdn.DownloadFile(fileName, saveDirectory2, True, CCDNResourceEnum.Version.value, environment=environment.value, server=server, platform=BPlatformEnum.IOS.value): return False
    #    
    savedFile = os.path.join(saveDirectory0, fileName)
    if not MakeVersionFile(processMeta, processLocale, savedFile, versionNumber, languages): return False

    savedFile = os.path.join(saveDirectory1, fileName)
    if not MakeVersionFile(processMeta, processLocale, savedFile, versionNumber, languages): return False

    savedFile = os.path.join(saveDirectory2, fileName)
    if not MakeVersionFile(processMeta, processLocale, savedFile, versionNumber, languages): return False
    #
    return True

def CopyFiles(processMeta : bool, processLocale : bool, metadataLocation : str, serverLocation : str, syncAutoChessServer : bool, autoChessServerLocation : str, syncUnity : bool, unityLocation : str):
    unityCommonDirectory = os.path.join(unityLocation, 'Assets/StreamingAssets/Config/Common/')
    unityVersionDirectory = os.path.join(unityLocation, f'Assets/StreamingAssets/Config/Version/')
    serverDirectory = os.path.join(serverLocation, 'meta/')
    autoChessServerDirectory = os.path.join(autoChessServerLocation, 'AutoChessServer/Resource/Common/')
    result = (unityCommonDirectory, unityVersionDirectory, serverDirectory, autoChessServerDirectory)

    if syncUnity:
        if processMeta:
            srcUnityM = os.path.join(metadataLocation, 'Tools/configM/Meta.bytes') 
            if not UOS.CopyFile2D(srcUnityM, unityCommonDirectory, True): return False,result
            UTracking.LogInfo('CopyFiles->CopyFile2D', f'from: {srcUnityM}, to: {unityCommonDirectory}')

        if processLocale:
            srcUnityL = os.path.join(metadataLocation, 'Tools/configL/') 
            if not UOS.CopyFiles(srcUnityL, unityCommonDirectory, True): return False,result
            UTracking.LogInfo('CopyFiles->CopyFiles', f'from: {srcUnityL}, to: {unityCommonDirectory}')
        #
        fileName = MVersionFile.Name()

        srcUnityV = os.path.join(metadataLocation, f'Tools/configM/{BPlatformEnum.Standalone.value}/', fileName)
        destUnityV = os.path.join(unityVersionDirectory, f'{BPlatformEnum.Standalone.value}/')    
        if not UOS.CopyFile2D(srcUnityV, destUnityV, True): return False,result
        UTracking.LogInfo('CopyFiles->CopyFile2D', f'from: {srcUnityV}, to: {destUnityV}')

        srcUnityV = os.path.join(metadataLocation, f'Tools/configM/{BPlatformEnum.Android.value}/', fileName)
        destUnityV = os.path.join(unityVersionDirectory, f'{BPlatformEnum.Android.value}/')    
        if not UOS.CopyFile2D(srcUnityV, destUnityV, True): return False,result
        UTracking.LogInfo('CopyFiles->CopyFile2D', f'from: {srcUnityV}, to: {destUnityV}')

        srcUnityV = os.path.join(metadataLocation, f'Tools/configM/{BPlatformEnum.IOS.value}/', fileName)
        destUnityV = os.path.join(unityVersionDirectory, f'{BPlatformEnum.IOS.value}/')    
        if not UOS.CopyFile2D(srcUnityV, destUnityV, True): return False,result
        UTracking.LogInfo('CopyFiles->CopyFile2D', f'from: {srcUnityV}, to: {destUnityV}')

    srcServer = os.path.join(metadataLocation, 'Tools/server/')
    if not UOS.CopyFiles(srcServer, serverDirectory, True): return False,result
    UTracking.LogInfo('CopyFiles->CopyFiles', f'from: {srcServer}, to: {serverDirectory}')

    if syncAutoChessServer:
        if processMeta:        
            srcAutoChessServer = os.path.join(metadataLocation, 'Tools/configM/Meta.bytes') 
            if not UOS.CopyFile2D(srcAutoChessServer, autoChessServerDirectory, True): return False,result
            UTracking.LogInfo('CopyFiles->CopyFile2D', f'from: {srcAutoChessServer}, to: {autoChessServerDirectory}')

    return True,result

def UploadCDN(processMeta : bool, processLocale : bool, metadataLocation : str, versionNumber : int, environment : CCDNEnvironmentEnum, server : str) -> bool:
    cdn = MCDN(CCDNProduct())
    #
    if processMeta:
        localPath = os.path.join(metadataLocation, 'Tools/configM/Meta.bytes')
        if not cdn.UploadFile(localPath, False, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Meta.value, version=versionNumber, environment=environment.value, server=server): return False
    
    if processLocale:
        localPath = os.path.join(metadataLocation, 'Tools/configL/')
        if not cdn.UploadDirectory(localPath, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Locale.value, version=versionNumber, environment=environment.value, server=server): return False
    #
    fileName = MVersionFile.Name()

    localPath = os.path.join(metadataLocation, f'Tools/configM/{BPlatformEnum.Standalone.value}/', fileName)
    if not cdn.UploadFile(localPath, False, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Version.value, environment=environment.value, server=server, platform=BPlatformEnum.Standalone.value): return False

    localPath = os.path.join(metadataLocation, f'Tools/configM/{BPlatformEnum.Android.value}/', fileName)
    if not cdn.UploadFile(localPath, False, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Version.value, environment=environment.value, server=server, platform=BPlatformEnum.Android.value): return False

    localPath = os.path.join(metadataLocation, f'Tools/configM/{BPlatformEnum.IOS.value}/', fileName)
    if not cdn.UploadFile(localPath, False, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Version.value, environment=environment.value, server=server, platform=BPlatformEnum.IOS.value): return False
    #
    return True
    

def DoAction(configKey : str, platform : BPlatformEnum, args : dict):
    UTracking.LogInfo('MetaAndLocale->DoAction', UTracking.BeautifyLog(args))

    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('MetaAndLocale->DoAction', 'node not existed, key: ' + configKey)
    #
    node = MNode(config)
    project = node.GetIdleProject(platform, MProject.GetBusyMarkTag(args))
    if project is None:
        UTracking.RaiseException('MetaAndLocale->DoAction', 'no idle project existed, platform: ' + platform.value)
    #
    project.Begin()
    try:        
        purpose = args['purpose']
        branchMetadata = args['branch_metadata']
        branchServer = args['branch_server']
        branchUnity = args['branch_unity']        
        environment = CCDNEnvironmentEnum.FromS(args['environment'])
        server = UBase.ReplaceStrings(args['server'], ['.', ':', '-', '/', '\\'], '_')
        languages = args['languages']
        syncUnity = args['sync_unity']
        syncAutoChessServer = args['sync_auto_chess_server']
        branchAutoChessServer = args['branch_auto_chess_server']
        versionNumber = UDateTime.ToDateTimeSecond(args['time_stamp'])        
        #
        pl = purpose.lower()
        if pl == 'meta_locale':
            processMeta = True
            processLocale = True
        elif pl == 'meta':
            processMeta = True
            processLocale = False
        elif pl == 'locale':
            processMeta = False
            processLocale = True
        else:
            processMeta = True
            processLocale = True

        metadataLocation = ''
        serverLocation = ''
        unityLocation = ''
        autoChessServerLocation = ''
        #
        git = MGit(CGitProduct())
        #
        gitParamsMeta = MGitParams()
        project.SetupGitParams('Metadata', gitParamsMeta)
        gitParamsMeta.branch = branchMetadata
        project.Check(git.CloneOrPull(gitParamsMeta), 'Git metadata', args)
        metadataLocation = gitParamsMeta.location
        #
        gitParamsServer = MGitParams()
        project.SetupGitParams('Server', gitParamsServer)
        gitParamsServer.branch = branchServer
        project.Check(git.CloneOrPull(gitParamsServer), 'Git server', args)
        serverLocation = gitParamsServer.location
        #
        if syncAutoChessServer:
            gitParamsAutoChessServer = MGitParams()
            project.SetupGitParams('AutoChessServer', gitParamsAutoChessServer)
            gitParamsAutoChessServer.branch = branchAutoChessServer
            project.Check(git.CloneOrPull(gitParamsAutoChessServer), 'Git auto chess server', args)
            autoChessServerLocation = gitParamsAutoChessServer.location
        #
        if syncUnity:
            gitParamsUnity = MGitParams()
            project.SetupGitParams('Unity', gitParamsUnity)
            gitParamsUnity.branch = branchUnity
            project.Check(git.CloneOrPull(gitParamsUnity), 'Git unity', args)
            unityLocation = gitParamsUnity.location
        #
        project.Check(RunInternalScripts(processMeta, processLocale, metadataLocation), 'Run internal scripts', args)
        #
        project.Check(MakeVersionFiles(processMeta, processLocale, metadataLocation, versionNumber, environment, server, languages), 'Make version file', args)
        #
        CFResult, (unityCommonDirectory, unityVersionDirectory, serverDirectory, autoChessServerDirectory) = CopyFiles(processMeta, processLocale, metadataLocation, serverLocation, syncAutoChessServer, autoChessServerLocation, syncUnity, unityLocation)
        project.Check(CFResult, 'Copy files', args)
        
        if syncUnity:
            project.Check(git.CommitAndPush(gitParamsUnity, 'Jenkins commit meta and locale', [unityCommonDirectory, unityVersionDirectory]), 'Git unity commit', args)

        project.Check(git.CommitAndPush(gitParamsServer, 'Jenkins commit meta and locale', [serverDirectory]), 'Git server commit', args)

        if syncAutoChessServer:
            project.Check(git.CommitAndPush(gitParamsAutoChessServer, 'Jenkins commit meta and locale', [autoChessServerDirectory]), 'Git auto chess server commit', args)
        #
        project.Check(UploadCDN(processMeta, processLocale, metadataLocation, versionNumber, environment, server), 'Upload CDN', args)
    finally:
        project.End()

def main():
    # consoleTextPath = os.path.join(UOS.DirectoryOfPath(__file__), 'ConsoleText.txt')
    # UJenkinsArgs.Test_FillTestEnvironmentByConsoleTextFile(consoleTextPath)   

    args = UJenkinsArgs.FromEnvironment([
        ('__Purpose'                , 'purpose'                     , str   , 'error'                       ),
        ('__BranchMetadata'         , 'branch_metadata'             , str   , 'error'                       ),
        ('__BranchServer'           , 'branch_server'               , str   , 'error'                       ),
        ('__BranchUnity'            , 'branch_unity'                , str   , 'error'                       ),
        ('__Environment'            , 'environment'                 , str   , 'error'                       ),
        ('__Server'                 , 'server'                      , str   , 'error'                       ),
        ('__Languages'              , 'languages'                   , str   , 'error'                       ),
        ('__SyncUnity'              , 'sync_unity'                  , bool  , False                         ),
        ('__SyncAutoChessServer'    , 'sync_auto_chess_server'      , bool  , False                         ),
        ('__BranchAutoChessServer'  , 'branch_auto_chess_server'    , str   , 'error'                       ),
        ('BUILD_TIMESTAMP'          , 'time_stamp'                  , str   , '2011-11-11 11:11:11 CST'     )
    ])
    
    configKey = ''
    platform = BPlatformEnum.DontCare
    DoAction(configKey, platform, args)

if __name__ == '__main__':
    main()