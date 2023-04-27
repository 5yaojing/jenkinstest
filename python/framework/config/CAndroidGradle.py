class CAndroidGradle:
    version = ''
    
    toolsBuildGradleVersion = ''
    compileSdkVersion = 0
    buildToolsVersion = ''
    minSdkVersion = 0
    targetSdkVersion = 0
    #keystoreFromMainProject is True: 
    #       keystoreName must be relative path, such as 'Assets/xxx/yyy/zzz.keystore' or 'xxx/yyy/zzz.keystore', etc.
    #       the final path we used is 'main project path' + keystoreName, main project may be unity project or UE4 project, etc.
    #keystoreFromMainProject is False: 
    #       keystoreName must be absolute path, such as 'C:/Unity/Assets/xxx/yyy/zzz.keystore' or 'C:/Unity/xxx/yyy/zzz.keystore' or 'C:/xxx/yyy/zzz.keystore', etc.
    #       the final path we used is keystoreName directly
    keystoreFromMainProject = False
    keystoreName = ''
    keyaliasName =''
    keystorePass = ''
    keyPassword = ''

    gradlePath = ''
    sdkPath = ''
    ndkPath = ''
    jdkPath = ''