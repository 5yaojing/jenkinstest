from framework.basic.BConstant import *
from framework.utils import UTracking
from framework.config.CNFS import *

class CNFSResourceEnum(Enum):
    Archive = 'Archive'

class CNFSProduct(CNFS):
    version = '0.0.0'
    
    if BConstSystemPlatform == BPlatformEnum.OSX:
        diskLink = '/Tmp/JenkinsSync/'
    elif BConstSystemPlatform == BPlatformEnum.Windows:
        diskLink = 'C:/JenkinsSync/'
    else:
        UTracking.RaiseException('CNFSProduct->__init__', 'Unsupported system platform: ' + BConstSystemPlatform)
    
    domain = 'https://xpackage.tuyoo.com/'
    uploadURL = f'{domain}'
    downloadURL = f'{domain}'
    uploadRetry = 3
    downloadRetry = 3
    
    rootPathFormats = {
        'Archive'   : 'Archive/MiniGames/{game}/{jobName}/{buildNumber}/'
    }