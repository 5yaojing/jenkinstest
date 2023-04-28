from framework.basic.BConstant import *
from framework.utils import UTracking
from framework.config.CGit import *
from product.base.BConstantProduct import *
class CGitProduct(CGit):
    version = '2.30.1'

    if BConstSystemPlatform == BPlatformEnum.OSX:
        appPath = 'git'
    elif BConstSystemPlatform == BPlatformEnum.Windows:
        appPath = 'git'
    else:
        UTracking.RaiseException('CGitProduct->__init__', 'Unsupported system platform: ' + BConstSystemPlatform)

    account = '550707041@qq.com'
    password = '715813zz'