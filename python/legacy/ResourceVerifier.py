from framework.utils import UJson
from framework.utils import UJenkinsArgs

from framework.modules.MNode import *
from framework.modules.MProject import *
from framework.modules.MGit import *
from framework.modules.MUnity import *

from product.config.CNodeProduct import *
from product.config.CGitProduct import *
from product.config.CUnityProduct import *

from product.modules.MVersionFile import *

def DoAction(configKey : str, platform : BPlatformEnum, args : dict):
    UTracking.LogInfo('ResourceVerifier->DoAction', UTracking.BeautifyLog(args))

    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('ResourceVerifier->DoAction', 'node not existed, key: ' + configKey)
    #
    node = MNode(config)
    project = node.GetIdleProject(platform, MProject.GetBusyMarkTag(args))
    if project is None:
        UTracking.RaiseException('ResourceVerifier->DoAction', 'no idle project existed, platform: ' + platform.value)
    #
    project.Begin()
    try:
        branch = args['branch']
        #
        git = MGit(CGitProduct())        
        gitParamsUnity = MGitParams()
        project.SetupGitParams('Unity', gitParamsUnity)
        gitParamsUnity.branch = branch
        project.Check(git.CloneOrPull(gitParamsUnity), 'Git unity', args)
        #        
        unity = MUnity(CUnityProduct())
        unityParams = MUnityParams()
        project.SetupUnityParams(unityParams, MUnityPlatformEnum.From(platform))
        ps = {
            'type':'unknown'#暂时还不知道参数是啥，随便写了一个
        }
        unityParams.executeMethodParams = UJson.ToJson(ps)
        unityParams.executeMethod = 'Class.Method'
        project.Check(unity.Exec(unityParams), 'Unity', args)
        #
    finally:
        project.End()

def main():
    # consoleTextPath = os.path.join(UOS.DirectoryOfPath(__file__), 'ConsoleText.txt')
    # UJenkinsArgs.Test_FillTestEnvironmentByConsoleTextFile(consoleTextPath)

    args = UJenkinsArgs.FromEnvironment([
        ('__Platform'           , 'platform'                , str   , 'error'                   ),
        ('__Branch'             , 'branch'                  , str   , 'error'                   )
    ])
    
    configKey = ''
    platform = BPlatformEnum.FromS(args['platform'])
    DoAction(configKey, platform, args)

if __name__ == '__main__':
    main()