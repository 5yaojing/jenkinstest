from ..basic.BDefines import *
from ..config.CNode import *
from .MProject import *

class MNode:
    __config : CNode = None
    ################################################################ 
    def __init__(self, config : CNode):
        if config is None:
            UTracking.RaiseException('MNode->__init__', 'config is none')
        self.__config = config
    ################################################################
    def __IsBusy(self, project : CProject) -> bool:
        if project is None: return True
        if UOS.IsFileExist(project.busyMark): return True
        return False
    ################################################################
    def GetIdleProject(self, platform : BPlatformEnum, groupKey : str, busyMarkTag : str) -> MProject:
        groups = self.__config.projects.get(platform)        
        if groups is None: return None        
        
        if UBase.IsStringNoneOrEmpty(str):
            projects = groups
        else:
            projects = groups.get(groupKey)
            if projects is None: return None

        project = None
        for p in projects:
            if self.__IsBusy(p): continue
            project = p
            break
        if project is None: return None
        return MProject(project, busyMarkTag)