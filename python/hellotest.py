from framework.basic.BConstant import *
from framework.utils import UJenkinsArgs
from framework.modules.MNode import *
from framework.modules.MProject import *
from framework.modules.MGit import *

#from product.config.CNodeProduct import *
from product.config.CNodeHelloProduct import *
from product.config.CGitProduct import *

#传入的参数为前面克隆或者拉下来的git仓库的路径，我要进入这个路径然后在里面新建一个python脚本，内容为打印hello world，返回是否成功
def ChangeFolderContent(filePath : str)->bool:
    python_script='print("hello world")'
    filt_path=os.path.join(filePath,'aaaanotherhello.py')
    try:
        with open(filt_path,'w') as f:
            f.write(python_script)
    except Exception as e:
        print(e)
        return False
    return True


def DoAction(configKey : str, platform : BPlatformEnum, game : BGameEnum, args : dict):
    UTracking.LogInfo('Meta->DoAction', UTracking.BeautifyLog(args))

    config = CNodeHelloSelector().Do(configKey)
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
        # branchData = args['branch_data']
        # branchClient = args['branch_client']
        # #
        # git = MGit(CGitProduct())
        # #
        # gitParamsData = MGitParams()
        # project.SetupGitParams('Data', gitParamsData)
        # gitParamsData.branch = branchData
        # project.Check(git.CloneOrPull(gitParamsData), 'Git data', args)
        # dataLocation = gitParamsData.location
        # #
        # gitParamsClient = MGitParams()
        # project.SetupGitParams('Client', gitParamsClient)
        # gitParamsClient.branch = branchClient
        # project.Check(git.CloneOrPull(gitParamsClient), 'Git client', args)
        # clientLocation = gitParamsClient.location
        # #
        # metaResult, resultDirectory = RunInternalScripts(dataLocation, clientLocation)
        # project.Check(metaResult, 'Run internal scripts', args)
        # project.Check(git.CommitAndPush(gitParamsClient, 'Jenkins commit meta', [resultDirectory]), 'Git client commit', args)
        print("Hello World77777777777777777777")
        #把一个仓库的拉下来然后做一些修改然后传上去，在框架里做这件事和在Jenkins里面做这件事
        git=MGit(CGitProduct())
        gitParamsHello=MGitParams()
        project.SetupGitParams('HelloTest',gitParamsHello)
        #加参数
        gitParamsHello.branch='main'
        project.Check(git.CloneOrPull(gitParamsHello),'Git HelloTest',args)
        helloLocation=gitParamsHello.location
        #修改文件
        changeresult=ChangeFolderContent(helloLocation)
        project.Check(changeresult,'ChangeFolderContent',args)
        #提交
        project.Check(git.CommitAndPush(gitParamsHello,'Jenkins commit meta',[helloLocation]),'Git HelloTest commit',args)
    finally:
        project.End()

def main():
    #consoleTextPath = os.path.join(UOS.DirectoryOfPath(__file__), 'ConsoleText.txt')
    #UJenkinsArgs.Test_FillTestEnvironmentByConsoleTextFile(consoleTextPath)   

    args = UJenkinsArgs.FromEnvironment([
        ('__Game'                   , 'game'                        , str   , 'error'       )
    ])
    
    configKey = ''
    platform = BPlatformEnum.DontCare
    game = BGameEnum.FromS(args['game'])
    DoAction(configKey, platform, game, args)

if __name__ == '__main__':
    main()