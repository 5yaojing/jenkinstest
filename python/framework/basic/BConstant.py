from .BDefines import *
import platform

def GetSystemPlatform():
    (bits, linkage) = platform.architecture()
    system = platform.system()
    version = platform.version()
    
    systemL = system.lower()
    current = None
    if systemL == 'windows':
        current = BPlatformEnum.Windows
    elif systemL == 'linux':
        current = BPlatformEnum.Linux
    elif systemL == 'darwin':
        current = BPlatformEnum.OSX
    else:
        raise ValueError(f'BConstant->GetSystemPlatform exception, system: {system}')
    return current

BConstSystemPlatform = GetSystemPlatform()