from dingtalkchatbot.chatbot import DingtalkChatbot
from ..utils import UTracking
from ..config.CDingDing import *

class MDingDing:
    __config : CDingDing = None
    ################################################################ 
    def __init__(self, config : CDingDing):
        if config is None:
            UTracking.RaiseException('MDingDing->__init__', 'config is none')
        self.__config = config
    ################################################################
    ################################################################
    def SendMessage(self, group : str, message : str) -> bool:
        result = False
        
        values = self.__config.groups.get(group)
        if values is None:
            UTracking.LogError('MDingDing->SendMessage', 'not found group: ' + group)
        else:
            webhook = values['webhook']
            secret = values['secret']
            dingding = DingtalkChatbot(webhook=webhook, secret=secret)
            rs = dingding.send_text(message)
            result = rs['errcode'] == 0

        return result
    