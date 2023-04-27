from enum import Enum

class BPlatformEnum(Enum):
    DontCare        = 'DontCare'    
    Android         = 'Android'
    IOS             = 'IOS'
    Windows         = 'Windows'
    OSX             = 'OSX'
    Linux           = 'Linux'
    #
    Standalone      = 'Standalone'
    #
    MiniGame        = 'MiniGame'
    @staticmethod
    def FromS(v : str):
        lv = v.lower()
        if lv == BPlatformEnum.DontCare.value.lower():
            r = BPlatformEnum.DontCare
        elif lv == BPlatformEnum.Android.value.lower():
            r = BPlatformEnum.Android
        elif lv == BPlatformEnum.IOS.value.lower():
            r = BPlatformEnum.IOS
        elif lv == BPlatformEnum.Windows.value.lower():
            r = BPlatformEnum.Windows
        elif lv == BPlatformEnum.OSX.value.lower():
            r = BPlatformEnum.OSX
        elif lv == BPlatformEnum.Linux.value.lower():
            r = BPlatformEnum.Linux
        elif lv == BPlatformEnum.Standalone.value.lower():
            r = BPlatformEnum.Standalone
        elif lv == BPlatformEnum.MiniGame.value.lower():
            r = BPlatformEnum.MiniGame
        else:
            raise ValueError(f'BPlatformEnum->FromS exception, value: {v}')
        return r

class BArchitectureEnum(Enum):
    ARMv7 = 'armeabi-v7a'
    ARM64 = 'arm64-v8a'
    @staticmethod
    def FromS(v : str):
        if v == BArchitectureEnum.ARMv7.value.lower():
            r = BArchitectureEnum.ARMv7
        elif v == BArchitectureEnum.ARM64.value.lower():
            r = BArchitectureEnum.ARM64
        else:
            raise ValueError(f'BArchitectureEnum->FromS exception, value: {v}')
        return r

class BPackageTypeEnum(Enum):
    APK             = 'apk'
    AAB             = 'aab'
    @staticmethod
    def FromS(v : str):
        vl = v.lower()
        if vl == BPackageTypeEnum.APK.value.lower():
            r = BPackageTypeEnum.APK
        elif vl == BPackageTypeEnum.AAB.value.lower():
            r = BPackageTypeEnum.AAB
        else:
            raise ValueError(f'BPackageTypeEnum->FromS exception, value: {v}')
        return r

class BPackagePurposeEnum(Enum):
    Publish         = 'Publish'
    Test            = 'Test'
    @staticmethod
    def FromS(v : str):
        vl = v.lower()
        if vl == BPackagePurposeEnum.Publish.value.lower():
            r = BPackagePurposeEnum.Publish
        elif vl == BPackagePurposeEnum.Test.value.lower():
            r = BPackagePurposeEnum.Test
        else:
            raise ValueError(f'BPackagePurposeEnum->FromS exception, value: {v}')
        return r

class BPackageResourceEmbedEnum(Enum):
    Full            = 'Full'
    ReleaseFull     = 'ReleaseFull'
    Mini            = 'Mini'
    @staticmethod
    def FromS(v : str):
        vl = v.lower()
        if vl == BPackageResourceEmbedEnum.Full.value.lower():
            r = BPackageResourceEmbedEnum.Full
        elif vl == BPackageResourceEmbedEnum.ReleaseFull.value.lower():
            r = BPackageResourceEmbedEnum.ReleaseFull
        elif vl == BPackageResourceEmbedEnum.Mini.value.lower():
            r = BPackageResourceEmbedEnum.Mini
        else:
            raise ValueError(f'BPackageResourceEmbedEnum->FromS exception, value: {v}')
        return r
