from framework.basic.BConstant import *
from framework.utils import UTracking
from framework.config.CUnity import *
from product.base.BConstantProduct import *

class CUnityProduct(CUnity):
    version = '2021.3.14f1'

    if BConstSystemPlatform == BPlatformEnum.OSX:
        appPath = '/Applications/Unity/Hub/Editor/2021.3.14f1/Unity.app/Contents/MacOS/Unity'
        playbackEnginesPath = '/Applications/Unity/Hub/Editor/2021.3.14f1/PlaybackEngines/'
    elif BConstSystemPlatform == BPlatformEnum.Windows:
        appPath = 'c:/Progra~1/Unity/Hub/Editor/2021.3.14f1/Editor/Unity.exe'
        playbackEnginesPath = 'c:/Progra~1/Unity/Hub/Editor/2021.3.14f1/Editor/Data/PlaybackEngines/'
    else:
        UTracking.RaiseException('CUnityProduct->__init__', 'Unsupported system platform: ' + BConstSystemPlatform)

    account_Develop = 'qushuai@tuyoogame.com'
    password_Develop = 'messi123'
    serial_Develop = 'SC-7XTF-VJ7H-8Y32-R3HU-GY8V'
    account_Publish = 'qushuai@tuyoogame.com'
    password_Publish = 'messi123'
    serial_Publish = 'SC-7XTF-VJ7H-8Y32-R3HU-GY8V'