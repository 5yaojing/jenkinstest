from framework.basic.BConstant import *
from framework.utils import UTracking
from framework.config.CAndroidStudio import *
from .CAndroidGradleProduct import *

class CAndroidStudioProduct(CAndroidStudio):
    version = '0.0.0.0'
    
    if BConstSystemPlatform == BPlatformEnum.OSX:
        appPath = '/Applications/Android\ Studio.app/Contents/MacOS/studio'
    elif BConstSystemPlatform == BPlatformEnum.Windows:
        appPath = 'C:/Program\ Files/Android/Android Studio/bin/studio64.exe'
    else:
        UTracking.RaiseException('CAndroidStudioProduct->__init__', 'Unsupported system platform: ' + BConstSystemPlatform)
    
    gradle = CAndroidGradleProduct()