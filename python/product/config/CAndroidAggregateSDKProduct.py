from framework.config.CAndroidAggregateSDK import *
from .CAndroidGradleProduct import *
class CAndroidAggregateSDKProduct(CAndroidAggregateSDK):
    version = '0.0.0.0'
    gradle = CAndroidGradleProduct()
    if BConstSystemPlatform == BPlatformEnum.OSX:
        antPath = '/var/jenkins/tools/Android/apache-ant-1.10.12/bin/ant'
        python2Path = '/usr/local/bin/python2'
        tuyooSdkDir = ''
    elif BConstSystemPlatform == BPlatformEnum.Windows:
        antPath = 'C:/jenkins/tools/Android/apache-ant-1.10.12/bin/ant.bat'
        python2Path = 'C:/Python27/python.exe'
        tuyooSdkDir = ''
    else:
        UTracking.RaiseException('CAndroidAggregateSDKProduct->__init__', 'Unsupported system platform: ' + BConstSystemPlatform)        
   