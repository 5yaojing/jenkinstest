from framework.utils import UJenkinsArgs

from framework.modules.MNode import *
from framework.modules.MProject import *
from framework.modules.MGit import *
from framework.modules.MCDN import *

from product.base.BDefineProduct import *
from product.config.CNodeProduct import *
from product.config.CGitProduct import *
from product.config.CCDNProduct import *

from product.modules.MManifestFile import *

def CheckBundleVersion(v : str) -> bool:
    ss = v.split(".")
    if len(ss) != 3: return False

    if not UBase.IsIntRange(ss[0], 0, 99): return False
    if not UBase.IsIntRange(ss[1], 0, 99): return False
    if not UBase.IsIntRange(ss[2], 0, 99): return False

    return True

def CleanBuild(clientLocation: str) -> bool:
    buildDirectory = os.path.join(clientLocation, 'miniGame/build/')
    libraryDirectory = os.path.join(clientLocation, 'miniGame/library/')
    tempDirectory = os.path.join(clientLocation, 'miniGame/temp/')
    #
    if UOS.IsDirectoryExist(buildDirectory):
        UOS.DeleteDirectory(buildDirectory)
        UTracking.LogInfo('Package->CleanBuild', f'remove build folder: {buildDirectory}')

    if UOS.IsDirectoryExist(libraryDirectory):
        UOS.DeleteDirectory(libraryDirectory)
        UTracking.LogInfo('Package->CleanBuild', f'remove library folder: {libraryDirectory}')

    if UOS.IsDirectoryExist(tempDirectory):
        UOS.DeleteDirectory(tempDirectory)
        UTracking.LogInfo('Package->CleanBuild', f'remove temp folder: {tempDirectory}')
    return True

def BuildPackage(gamePlatform : BGamePlatformEnum, clientLocation: str, buildVersion : str, release : bool, cdn : str) -> bool:
    scriptPath = os.path.join(clientLocation, 'miniGame/buildDepend/build_wechatgame.sh')

    result = 0
    if BConstSystemPlatform == BPlatformEnum.OSX:
        result = UCommand.RunCmd(f'chmod +x {scriptPath}')

    if result == 0:
        releaseStr = 'true' if release else 'false'
        #下面这个命令，在VSCode中运行时失败的，可能是和NodeJS冲突导致的，错误是“bad option: --project”。
        #不过实际环境中，是正常的。目前没有去寻找解决办法，有时间再说，谁能解决也可
        result = UCommand.RunCmd(f'{scriptPath} {buildVersion} {releaseStr} {cdn}')
    
    ok = False
    checkFile0Path = os.path.join(clientLocation, f'miniGame/build/{gamePlatform.value}/game.json')
    checkFile1Path = os.path.join(clientLocation, f'miniGame/build/{gamePlatform.value}/project.config.json')
    if result == 0:
        ok = UOS.IsFileExist(checkFile0Path) and UOS.IsFileExist(checkFile1Path)

    if ok:
        UTracking.LogInfo('Package->BuildPackage', f'Package successed')
    else:
        files = [checkFile0Path, checkFile1Path]
        UTracking.LogError('Package->BuildPackage', f'Package failed, files used for verification not existed: {UTracking.BeautifyLog(files)}')

    return ok

def CheckAssetBundle(clientLocation: str, gamePlatform : BGamePlatformEnum):
    assetBundleDirectory = os.path.join(clientLocation, f'miniGame/build/{gamePlatform.value}/remote/')
    #
    result = True
    if not UOS.IsDirectoryExist(assetBundleDirectory):
        result = False
        UTracking.LogError('Package->CheckAssetBundle', f'asset bundle directory not exit: {assetBundleDirectory}')
    #
    return result

def MakeManifest(clientLocation: str, game : BGameEnum, gamePlatform : BGamePlatformEnum, buildVersion : int, bundleVersion : int, cdn : str) -> bool:
    assetBundleDirectory = os.path.join(clientLocation, f'miniGame/build/{gamePlatform.value}/remote/')
    manifestDirectory = os.path.join(clientLocation, f'miniGame/build/{gamePlatform.value}_temp/')
    manifestPath = os.path.join(manifestDirectory, MManifestFile.Name())
    #
    if UOS.IsDirectoryExist(manifestDirectory):
        if UOS.IsFileExist(manifestPath):
            UOS.DeleteFile(manifestPath)
    else:
        UOS.CreateDirectory(manifestDirectory)
        
    manifestFile = MManifestFile()
    if not manifestFile.CreateFrom(manifestPath): return False
    #
    manifestFile.MakeDesc('远程文件版本对比')
    #
    mcdn = MCDN(CCDNProduct())
    manifestDirectoryCDN = mcdn.MakePath(CCDNResourceEnum.Manifest.value, game=game.value, buildVersion=buildVersion)
    manifestDirectoryCDNParent = UOS.DirectoryOfPath(manifestDirectoryCDN)
    packageURL = os.path.join(cdn, manifestDirectoryCDNParent)
    manifestFile.MakePackageURL(packageURL)
    #
    paths = os.listdir(assetBundleDirectory)
    for path in paths:
        fp = os.path.join(assetBundleDirectory, path)
        if not os.path.isdir(fp): continue
        manifestFile.AddFolder(path, bundleVersion)

    if not manifestFile.Save(): return False
    #
    UTracking.LogInfo('Package->MakeManifest', f'file: {manifestPath}, build version: {buildVersion}, bundle version: {bundleVersion}')
    return True

def UploadCDNAssetBundle(clientLocation: str, game : BGameEnum, gamePlatform : BGamePlatformEnum, buildVersion : int, bundleVersion : int) -> bool:
    assetBundleDirectory = os.path.join(clientLocation, f'miniGame/build/{gamePlatform.value}/remote/')
    manifestPath = os.path.join(clientLocation, f'miniGame/build/{gamePlatform.value}_temp/{MManifestFile.Name()}')

    cdn = MCDN(CCDNProduct())
    if not cdn.UploadDirectory(assetBundleDirectory, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.AssetBundle.value, game=game.value, buildVersion=buildVersion, bundleVersion=bundleVersion):
        return False

    if not cdn.UploadFile(manifestPath, False, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Manifest.value, game=game.value, buildVersion=buildVersion):
        return False
    
    return True

def PublishGame(gamePlatform : BGamePlatformEnum, clientLocation: str) -> bool:
    return False

def DoAction(configKey : str, platform : BPlatformEnum, game : BGameEnum, args : dict):
    UTracking.LogInfo('Package->DoAction', UTracking.BeautifyLog(args))

    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('Package->DoAction', 'node not existed, key: ' + configKey)
    #
    node = MNode(config)
    project = node.GetIdleProject(platform, game.value, MProject.GetBusyMarkTag(args))
    if project is None:
        UTracking.RaiseException('Package->DoAction', f'no idle project existed, platform: {platform.value}, game: {game.value}')
    #
    project.Begin()
    try:
        gamePlatform = BGamePlatformEnum.wechatgame
        branch = args['branch']
        buildVersion = args['build_version']
        cdn = args['cdn']
        cdn2 = args['cdn2']
        uploadAssetbunde = args['upload_assetbundle']
        publish = args['publish']
        release = args['release']
        buildNumber = args['build_number']

        # appID = game.AppID()#暂时不用
        project.Check(CheckBundleVersion(buildVersion), 'Check bundle version', args)
        #
        git = MGit(CGitProduct())
        
        gitParamsClient = MGitParams()
        project.SetupGitParams('Client', gitParamsClient)
        gitParamsClient.branch = branch
        project.Check(git.CloneOrPull(gitParamsClient), 'Git client', args)
        clientLocation = gitParamsClient.location
        #
        project.Check(CleanBuild(clientLocation), 'Clean build', args)
        project.Check(BuildPackage(gamePlatform, clientLocation, buildVersion, release, cdn), 'Build package', args)
        #
        if uploadAssetbunde:
            project.Check(CheckAssetBundle(clientLocation, gamePlatform), 'Check asset bundle', args)
            project.Check(MakeManifest(clientLocation, game, gamePlatform, buildVersion, buildNumber, cdn), 'Make manifest', args)
            project.Check(UploadCDNAssetBundle(clientLocation, game, gamePlatform, buildVersion, buildNumber), 'Upload asset bundle', args)
        #
        if publish:
            project.Check(PublishGame(gamePlatform, clientLocation), 'Publish game', args)
        #
    finally:
        project.End()

def main():
    # consoleTextPath = os.path.join(UOS.DirectoryOfPath(__file__), 'ConsoleText.txt')
    # UJenkinsArgs.Test_FillTestEnvironmentByConsoleTextFile(consoleTextPath)

    args = UJenkinsArgs.FromEnvironment([
        ('__Game'                   , 'game'                    , str   , 'error'       ),
        ('__Branch'                 , 'branch'                  , str   , 'error'       ),
        ('__BuildVersion'           , 'build_version'           , str   , '1.0.0'       ),
        ('__CDN'                    , 'cdn'                     , str   , 'error'       ),
        ('__CDN2'                   , 'cdn2'                    , str   , 'error'       ),
        ('__UploadAssetbundle'      , 'upload_assetbundle'      , bool  , False         ),
        ('__Publish'                , 'publish'                 , bool  , False         ),
        ('__Release'                , 'release'                 , bool  , False         ),
        ('BUILD_NUMBER'             , 'build_number'            , int   , 0             )
    ])

    configKey = ''
    platform = BPlatformEnum.MiniGame
    game = BGameEnum.FromS(args['game'])
    DoAction(configKey, platform, game, args)

if __name__ == '__main__':
    main()