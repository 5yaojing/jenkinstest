from framework.basic.BConstant import *
from framework.utils import UTracking
from framework.config.CAndroidGradle import *
from product.base.BConstantProduct import *
class CAndroidGradleProduct(CAndroidGradle):
    version = '0.0.0.0'
    toolsBuildGradleVersion = '4.0.1'
    compileSdkVersion = 31
    buildToolsVersion = '31.0.0'
    minSdkVersion = 21
    targetSdkVersion = 31
    keystoreFromMainProject = True
    keystoreName = 'Assets/Keystore/coa_keystore.keystore'
    keyaliasName ='base2'
    keystorePass = '12345678'
    keyPassword = '12345678'
    #
    if BConstSystemPlatform == BPlatformEnum.OSX:       
        gradlePath = '/var/jenkins/tools/Android/gradle/gradle-6.1.1/bin/gradle'
        sdkPath = '/var/jenkins/tools/Android/sdk/'
        ndkPath = '/var/jenkins/tools/Android/sdk/ndk/21.3.6528147/'
        jdkPath = '/Library/Java/JavaVirtualMachines/jdk1.8.jdk/Contents/Home/'
    elif BConstSystemPlatform == BPlatformEnum.Windows:
        gradlePath = 'C:/jenkins/tools/Android/gradle/gradle-6.1.1/bin/gradle'
        sdkPath = 'C:/jenkins/tools/Android/sdk/'
        ndkPath = 'C:/jenkins/tools/Android/sdk/ndk/21.3.6528147/'
        #jdkPath 与上面几个path写法，有点不太一样，非常规，要注意
        jdkPath = '"C:/Program Files/Java/jdk1.8.0_311/"'
    else:
        UTracking.RaiseException('CAndroidStudioProduct->__init__', 'Unsupported system platform: ' + BConstSystemPlatform)