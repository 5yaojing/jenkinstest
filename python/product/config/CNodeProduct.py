import os
from framework.utils import UBase
from framework.utils import UTracking
from framework.config.CNode import *
from product.base.BDefineProduct import *
#为CNode对象构造初始值
#这个文件项目里随意定制，格式任意，形式任意，该赋值的都赋值即可
class CNodeProduct(CNode):
    def __init__(self):
        self.name = 'Default'

        if BConstSystemPlatform == BPlatformEnum.OSX:
            self.jenkins = '/var/jenkins/work/'
            self.root = '/var/jenkins/Node/'
        elif BConstSystemPlatform == BPlatformEnum.Windows:
            self.jenkins = 'C:/jenkins/work/'
            self.root = 'C:/jenkins/Node/'
        else:
            UTracking.RaiseException('CNodeProduct->__init__', 'Unsupported system platform: ' + BConstSystemPlatform)
             
        self.projectRoot = os.path.join(self.root, 'Projects/')
        #每个平台的每个group配置5个工程，这是个预估量，实际上用不到几个
        self.projects = {
            BPlatformEnum.DontCare : {
                BGameEnum.CuteStars.value :[
                    self.__CreateProject(BPlatformEnum.DontCare, BGameEnum.CuteStars, 0),
                    self.__CreateProject(BPlatformEnum.DontCare, BGameEnum.CuteStars, 1),
                    self.__CreateProject(BPlatformEnum.DontCare, BGameEnum.CuteStars, 2),
                    self.__CreateProject(BPlatformEnum.DontCare, BGameEnum.CuteStars, 3),
                    self.__CreateProject(BPlatformEnum.DontCare, BGameEnum.CuteStars, 4)
                ]
            },
            BPlatformEnum.MiniGame : {
                BGameEnum.CuteStars.value :[
                    self.__CreateProject(BPlatformEnum.MiniGame, BGameEnum.CuteStars, 0),
                    self.__CreateProject(BPlatformEnum.MiniGame, BGameEnum.CuteStars, 1),
                    self.__CreateProject(BPlatformEnum.MiniGame, BGameEnum.CuteStars, 2),
                    self.__CreateProject(BPlatformEnum.MiniGame, BGameEnum.CuteStars, 3),
                    self.__CreateProject(BPlatformEnum.MiniGame, BGameEnum.CuteStars, 4)
                ]
            }
        }
    ################################################################
    def __CreateProject(self, platform : BPlatformEnum, game : BGameEnum, index : int):
        name = f'{platform.value}_{game.value}{index}'
        project = CProject()
        project.name = name
        project.root = os.path.join(self.projectRoot, f'{name}/')
        project.busyMark = os.path.join(self.projectRoot, f'{name}.busy')
        #
        if game == BGameEnum.CuteStars:
            project.gitRepositorys = {
                'Client' : {
                    'url':'https://tygit.tuyoo.com/unicorn/minigame.git', 
                    'location':'Client/'
                },
                'Data' : {
                    'url':'https://tygit.tuyoo.com/unicorn/minigamedata.git', 
                    'location':'Data/'
                }
            }
        else:
            UTracking.RaiseException('CNodeProduct->__CreateProject', f'Unsupported game: {game.vale}')
        #
        project.untiyRoot = 'Unity/'
        project.unityExportPathApple = 'Apple/UnityExport/'
        project.unityExportPathAndroid = 'Android/UnityExport/'
        project.unityExportPathWindows = 'Windows/UnityExport/'
        project.unityExportPathLinux = 'Linux/UnityExport/'
        #
        project.appleRoot = 'Apple/'
        project.xcodeProjectPath = 'UnityExport/'
        project.xcodeWorkspace = False
        project.xcodeProjectFile = 'Unity-iPhone.xcodeproj'
        #
        project.androidRoot = 'Android/'
        project.androidStudioProjectPath = 'UnityExport/'
        project.androidStudioOutputAPKPath = 'OutputAPK/'
        project.androidStudioOutputAABPath = 'OutputAAB/'
        project.androidAggregateSDKOutputAPKPath = 'OutputAPKWithSDK/'
        project.androidAggregateSDKOutputAABPath = 'OutputAABWithSDK/'
        #
        project.windowsRoot = 'Windows/'
        #
        project.linuxRoot = 'Linux/'
        #
        project.minigameRoot = 'Client/'
        project.minigameOutputPath = 'Output/'
        #
        project.tempLocation = 'Temp/'
        #
        project.archiveLocation = os.path.join(self.jenkins, 'workspace/{jobName}/Archives/{buildNumber}/')
        return project
    ################################################################

class CNodeSelector:
    #
    __defaultNode = CNodeProduct()
    __nodes = {}
    #
    def Do(self, name : str = '') -> CNode:
        node = None
        
        if UBase.IsStringNoneOrEmpty(name):
            node = self.__defaultNode
        else:
            node = self.__nodes.get(name)

        return node