from framework.basic.BConstant import *
from framework.utils import UJenkinsArgs
from framework.modules.MNode import *
from framework.modules.MProject import *
from framework.modules.MGit import *

from product.config.CNodeProduct import *
from product.config.CGitProduct import *

def RunInternalScripts(dataLocation : str, clientLocation: str):
    scriptPath = os.path.join(clientLocation, 'miniGame/buildDepend/excel2csv.py')

    result = 0
    if BConstSystemPlatform == BPlatformEnum.OSX:
        result = UCommand.RunCmd(f'chmod +x {scriptPath}')

    dataDirectory = os.path.join(dataLocation, 'DataTables/')
    targetDirectory = os.path.join(clientLocation, 'miniGame/assets/games/configs/csv/')

    if result == 0:
        result = UCommand.RunPython(f'{scriptPath} -s 0 {dataDirectory} {targetDirectory}')
    
    return result == 0, targetDirectory

def DoAction(configKey : str, platform : BPlatformEnum, game : BGameEnum, args : dict):
    UTracking.LogInfo('Meta->DoAction', UTracking.BeautifyLog(args))

    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('Meta->DoAction', 'node not existed, key: ' + configKey)
    #
    node = MNode(config)
    project = node.GetIdleProject(platform, game.value, MProject.GetBusyMarkTag(args))
    if project is None:
        UTracking.RaiseException('Meta->DoAction', 'no idle project existed, platform: ' + platform.value)
    #
    project.Begin()
    try:
        branchData = args['branch_data']
        branchClient = args['branch_client']
        #
        git = MGit(CGitProduct())
        #
        gitParamsData = MGitParams()
        project.SetupGitParams('Data', gitParamsData)
        gitParamsData.branch = branchData
        project.Check(git.CloneOrPull(gitParamsData), 'Git data', args)
        dataLocation = gitParamsData.location
        #
        gitParamsClient = MGitParams()
        project.SetupGitParams('Client', gitParamsClient)
        gitParamsClient.branch = branchClient
        project.Check(git.CloneOrPull(gitParamsClient), 'Git client', args)
        clientLocation = gitParamsClient.location
        #
        metaResult, resultDirectory = RunInternalScripts(dataLocation, clientLocation)
        project.Check(metaResult, 'Run internal scripts', args)
        project.Check(git.CommitAndPush(gitParamsClient, 'Jenkins commit meta', [resultDirectory]), 'Git client commit', args)
    finally:
        project.End()

def main():
    # consoleTextPath = os.path.join(UOS.DirectoryOfPath(__file__), 'ConsoleText.txt')
    # UJenkinsArgs.Test_FillTestEnvironmentByConsoleTextFile(consoleTextPath)   

    args = UJenkinsArgs.FromEnvironment([
        ('__Game'                   , 'game'                        , str   , 'error'       ),
        ('__BranchData'             , 'branch_data'                 , str   , 'error'       ),
        ('__BranchClient'           , 'branch_client'               , str   , 'error'       )
    ])
    
    configKey = ''
    platform = BPlatformEnum.DontCare
    game = BGameEnum.FromS(args['game'])
    DoAction(configKey, platform, game, args)

if __name__ == '__main__':
    main()