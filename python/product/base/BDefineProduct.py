from enum import Enum

class BGameEnum(Enum):
    CuteStars = 'CuteStars'

    @staticmethod
    def FromS(v : str):
        lv = v.lower()

        if lv == BGameEnum.CuteStars.value.lower():
            r = BGameEnum.CuteStars
        else:
            raise ValueError(f'BGameEnum->FromS exception, value: {v}')
        return r
    
    def AppID(self) -> str:
        if self == BGameEnum.CuteStars:
            r = 'wx6ac3f5090a6b99c5'
        else:
            raise ValueError(f'BGameEnum->AppID exception, value: {self}')
        return r
    
class BGamePlatformEnum(Enum):
    wechatgame = 'wechatgame'