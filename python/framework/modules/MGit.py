import os
from ..utils import UBase
from ..utils import UOS
from ..utils import UCommand
from ..utils import UTracking
from ..config.CGit import *

class MGitParams:
    url = ''
    location = ''
    branch = 'branch'
    
class MGit:
    __config : CGit = None
    ################################################################ 
    def __init__(self, config : CGit):
        if config is None:
            UTracking.RaiseException('MGit->__init__', 'config is none')
        self.__config = config
    ################################################################
    def __GitCommand(self, cmd : str):
        return self.__config.appPath + ' ' + cmd

    def __IsRepositoryExisted(self, location : str) -> bool:
        if not UOS.IsDirectoryExist(location): return False
        
        os.chdir(location)
        result = UCommand.RunCmd(self.__GitCommand('status'))
        return result == 0
    
    def __ConvertGitURL(self, url : str):
        return url
        # #https://tygit.tuyoo.com/unicorn/nozdormu.git
        # #ssh://git@tygit.tuyoo.com:2222/unicorn/nozdormu.git
        # account = 'xxx'
        # password = 'yyy'
        # protocol = 'https://'
        # result = url
        # if url.startswith(protocol):
        #     other = url[len(protocol):]
        #     result = protocol + account + ':' + password + '@' + other
        # return result

    ################################################################
    def CloneOrPull(self, params : MGitParams) -> bool:
        UTracking.LogInfo('MGit->CloneOrPull', f'begin params: {UTracking.BeautifyLog(params.__dict__)}')

        result = 0
        
        if self.__IsRepositoryExisted(params.location):
            os.chdir(params.location)
            cmd = self.__GitCommand('reset --hard')
            result = UCommand.RunCmd(cmd)
            if result == 0:
                cmd = self.__GitCommand('clean -df')
                result = UCommand.RunCmd(cmd)
                if result == 0:
                    cmd = self.__GitCommand('fetch --prune --all')
                    result = UCommand.RunCmd(cmd)
                    if result == 0:
                        #cmd = self.__GitCommand('checkout -f -b ' + params.branch)
                        cmd = self.__GitCommand('checkout -f ' + params.branch)
                        result = UCommand.RunCmd(cmd)
                        if result == 0:                            
                            cmd = self.__GitCommand('pull --no-rebase')                            
                            result = UCommand.RunCmd(cmd)
        else:
            if UOS.IsDirectoryExist(params.location):
                UOS.DeleteDirectory(params.location)
            UOS.CreateDirectory(params.location)
            os.chdir(params.location)
            url = self.__ConvertGitURL(params.url)
            cmd = self.__GitCommand('clone -b ' + params.branch + ' ' + url + ' ' + params.location)
            result = UCommand.RunCmd(cmd)
            
        UTracking.LogInfo('MGit->CloneOrPull', 'end')
        return result == 0
    
    def CommitAndPush(self, params : MGitParams, message : str, paths : list = []) -> bool:
        UTracking.LogInfo('MGit->CommitAndPush', f'begin params: {UTracking.BeautifyLog(params.__dict__)}')

        if not self.__IsRepositoryExisted(params.location): return False        
        
        os.chdir(params.location)
        
        result = 0
        
        if UBase.IsContainerNoneOrEmpty(paths):
            cmd = self.__GitCommand('add -A')
            result = UCommand.RunCmd(cmd)
        else:
            for f in paths:
                cmd = self.__GitCommand('add ' + f)
                result = UCommand.RunCmd(cmd)
                if result != 0: break

        if result == 0:
            cmd = self.__GitCommand('commit -m "' + message + '"')
            result = UCommand.RunCmd(cmd)
            if result == 0:
                # cmd = self.__GitCommand('pull -X theirs')
                cmd = self.__GitCommand('pull --no-rebase')
                result = UCommand.RunCmd(cmd)
                if result == 0:
                    cmd = self.__GitCommand('push')
                    result = UCommand.RunCmd(cmd)
            elif result == 1:
                #如果没有staged的文件，commit返回值是1，这个很恶心，所以默认commit成功
                result = 0
                UTracking.LogInfo('MGit->CommitAndPush', 'nothing to commit')
            
        UTracking.LogInfo('MGit->CommitAndPush', 'end')
        return result == 0