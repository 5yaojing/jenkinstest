from framework.utils import UJson
from framework.utils import UJenkinsArgs

from framework.modules.MNode import *
from framework.modules.MProject import *
from framework.modules.MCDN import *

from product.config.CNodeProduct import *
from product.config.CCDNProduct import *

from product.modules.MVersionFile import *

def MakeVersionFile(path : str, args : dict) -> bool:
    versionFile = MVersionFile()
    if not versionFile.CreateFrom(path): return False

    versionFile.MakePublishTool(args)
    
    return versionFile.Save()

def UploadCDNVersion(path : str, environment : CCDNEnvironmentEnum, server : str, platform : BPlatformEnum) -> bool:
    cdn = MCDN(CCDNProduct())
    return cdn.UploadFile(path, False, False, CCDNProjectEnum.XProject.value, CCDNResourceEnum.Version.value, environment=environment.value, server=server, platform=platform.value)

def DoAction(configKey : str, platform : BPlatformEnum, args : dict):
    UTracking.LogInfo('PublishTool->DoAction', UTracking.BeautifyLog(args))

    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('PublishTool->DoAction', 'node not existed, key: ' + configKey)
    #
    node = MNode(config)
    project = node.GetIdleProject(platform, MProject.GetBusyMarkTag(args))
    if project is None:
        UTracking.RaiseException('PublishTool->DoAction', 'no idle project existed, platform: ' + platform.value)
    #
    project.Begin()
    try:        
        environment = CCDNEnvironmentEnum.FromS(args['environment'])
        server = UBase.ReplaceStrings(args['server'], ['.', ':', '-', '/', '\\'], '_')
        platformV = BPlatformEnum.FromS(args['platform'])
        #
        tempPath = os.path.join(project.GetTempLocation(), 'PublishTool/')
        if UOS.IsDirectoryExist(tempPath):
            UOS.DeleteDirectory(tempPath)
        UOS.CreateDirectory(tempPath)
        #
        versionPath = os.path.join(tempPath, MVersionFile.Name())
        project.Check(MakeVersionFile(versionPath, args), 'Make version file', args)
        #
        project.Check(UploadCDNVersion(versionPath, environment, server, platformV), 'Upload CDN version', args)
    finally:
        project.End()

def main():
    # consoleTextPath = os.path.join(UOS.DirectoryOfPath(__file__), 'ConsoleText.txt')
    # UJenkinsArgs.Test_FillTestEnvironmentByConsoleTextFile(consoleTextPath)

    args = UJenkinsArgs.FromEnvironment([        
        ('__Environment'            , 'environment'             , str   , 'error'   ),
        ('__Server'                 , 'server'                  , str   , 'error'   ),
        ('__Platform'               , 'platform'                , str   , 'error'   ),
        ('__minimum_version'        , 'minimum_version'         , str   , ''        ),
        ('__maximum_version'        , 'maximum_version'         , str   , ''        ),
        ('__meta_version'           , 'meta_version'            , str   , ''        ),
        ('__locale_version'         , 'locale_version'          , str   , ''        ),
        ('__asset_version'          , 'asset_version'           , str   , ''        ),
        ('__hotfix_version'         , 'hotfix_version'          , str   , ''        ),        
        ('__cdn'                    , 'cdn'                     , str   , ''        ),
        ('__cdn2'                   , 'cdn2'                    , str   , ''        ),
        ('__gateway_domain'         , 'gateway_domain'          , str   , ''        ),
        ('__gateway_ip'             , 'gateway_ip'              , str   , ''        ),
        ('__gateway_port'           , 'gateway_port'            , str   , ''        ),       
        ('__review_gateway_domain'  , 'review_gateway_domain'   , str   , ''        ),
        ('__review_gateway_ip'      , 'review_gateway_ip'       , str   , ''        ),
        ('__review_gateway_port'    , 'review_gateway_port'     , str   , ''        ),        
        ('__app_store'              , 'app_store'               , str   , ''        ),
        ('__languages'              , 'languages'               , str   , ''        )
    ])
    
    configKey = ''
    platform = BPlatformEnum.DontCare
    DoAction(configKey, platform, args)

if __name__ == '__main__':
    main()