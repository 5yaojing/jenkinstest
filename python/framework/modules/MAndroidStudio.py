import os
from ..basic.BDefines import *
from ..utils import UBase
from ..utils import UOS
from ..utils import UTracking
from ..utils import UCommand
from ..config.CAndroidStudio import *
 
class MAndroidStudioParams:
    projectPath = ''    
    outputAPKPath = ''
    outputAABPath = ''
    mainProjectPath = ''
    
    APKOrAAB = True
    bundleVersion = ''
    bundleVersionCode = 0
    releaseMode = False
    generateSymbolTable = False
    engineSymbolTablePath = []
    
class MAndroidStudio:
    __config : CAndroidStudio = None
    ################################################################ 
    def __init__(self, config : CAndroidStudio):
        if config is None:
            UTracking.RaiseException('MAndroidStudio->__init__', 'config is none')
        self.__config = config
    ################################################################
    def __GradleCommand(self, cmd : str, withJDK : bool = False):
        jdk = ''
        if withJDK:
            if not UBase.IsStringNoneOrEmpty(self.__config.gradle.jdkPath):
                jdk = ' -Dorg.gradle.java.home=' + self.__config.gradle.jdkPath
        return self.__config.gradle.gradlePath + ' ' + cmd + jdk

    def __LogModifyLine(self, tag : str, line : str, newLine : str):
        if UBase.IsStringNoneOrEmpty(line):
            UTracking.LogInfo(tag, f'add line: \'{newLine.strip()}\'')
        else:
            UTracking.LogInfo(tag, f'change line: from \'{line.strip()}\' to \'{newLine.strip()}\'')

    def __ModifyGradle(self, path : str, mainProjectPath : str, withKeyStore = True) -> bool:
        UTracking.LogInfo('MAndroidStudio->__ModifyGradle', f'begin file: \'{path}\'')
        if not UOS.IsFileExist(path): 
            UTracking.LogError('MAndroidStudio->__ModifyGradle', 'file not existed')
            return False
        
        lines = UOS.LoadTextFile(path)
        if lines is None:
            UTracking.LogError('MAndroidStudio->__ModifyGradle', 'file load error')
            return False
        
        newLines = []
        for line in lines:
            index = line.find('classpath')
            if index >= 0 and line.find('com.android.tools.build:gradle:', index) >= 0:
                newLine = f'{line[0 : index]}classpath \'com.android.tools.build:gradle:{self.__config.gradle.toolsBuildGradleVersion}\'\n'
                newLines.append(newLine)
                self.__LogModifyLine('MAndroidStudio->__ModifyGradle', line, newLine)
                continue
            
            index = line.find('compileSdkVersion')
            if index >= 0:
                newLine = f'{line[0 : index]}compileSdkVersion {self.__config.gradle.compileSdkVersion}\n'
                newLines.append(newLine)
                self.__LogModifyLine('MAndroidStudio->__ModifyGradle', line, newLine)
                continue

            index = line.find('buildToolsVersion')
            if index >= 0:
                newLine = f'{line[0 : index]}buildToolsVersion \'{self.__config.gradle.buildToolsVersion}\'\n'
                newLines.append(newLine)
                self.__LogModifyLine('MAndroidStudio->__ModifyGradle', line, newLine)
                continue

            index = line.find('minSdkVersion')
            if index >= 0:
                newLine = f'{line[0 : index]}minSdkVersion {self.__config.gradle.minSdkVersion}\n'
                newLines.append(newLine)
                self.__LogModifyLine('MAndroidStudio->__ModifyGradle', line, newLine)
                continue

            index = line.find('targetSdkVersion')
            if index >= 0:
                newLine = f'{line[0 : index]}targetSdkVersion {self.__config.gradle.targetSdkVersion}\n'
                newLines.append(newLine)
                self.__LogModifyLine('MAndroidStudio->__ModifyGradle', line, newLine)
                continue

            if withKeyStore:
                index = line.find('storeFile file(')
                if index >= 0:
                    keystorePath = os.path.join(mainProjectPath, self.__config.gradle.keystoreName) if self.__config.gradle.keystoreFromMainProject else self.__config.gradle.keystoreName
                    newLine = f'{line[0 : index]}storeFile file(\'{keystorePath}\')\n'
                    newLines.append(newLine)
                    self.__LogModifyLine('MAndroidStudio->__ModifyGradle', line, newLine)
                    continue

                index = line.find('storePassword')
                if index >= 0:
                    newLine = f'{line[0 : index]}storePassword \'{self.__config.gradle.keystorePass}\'\n'
                    newLines.append(newLine)
                    self.__LogModifyLine('MAndroidStudio->__ModifyGradle', line, newLine)
                    continue

                index = line.find('keyAlias')
                if index >= 0:
                    newLine = f'{line[0 : index]}keyAlias \'{self.__config.gradle.keyaliasName}\'\n'
                    newLines.append(newLine)
                    self.__LogModifyLine('MAndroidStudio->__ModifyGradle', line, newLine)
                    continue

                index = line.find('keyPassword')
                if index >= 0:
                    newLine = f'{line[0 : index]}keyPassword \'{self.__config.gradle.keyPassword}\'\n'
                    newLines.append(newLine)
                    self.__LogModifyLine('MAndroidStudio->__ModifyGradle', line, newLine)
                    continue

            newLines.append(line)

        result = UOS.SaveTextFile(path, newLines, True)

        UTracking.LogInfo('MAndroidStudio->__ModifyGradle', 'end')
        return result
    ################################################################
    @staticmethod
    def GetOutputPackageDirectory(params : MAndroidStudioParams):
        return params.outputAPKPath if params.APKOrAAB else params.outputAABPath

    @staticmethod
    def GetOutputPackagePath(params : MAndroidStudioParams):
        outputPath = ''
        if params.APKOrAAB:
            outputPath = os.path.join(params.outputAPKPath, 'launcher-release.apk' if params.releaseMode else 'launcher-debug.apk')
        else:
            outputPath = os.path.join(params.outputAABPath, 'launcher-release.aab' if params.releaseMode else 'launcher-debug.aab')
        return outputPath
    ################################################################
    def ModifyLocalProperties(self, params : MAndroidStudioParams) -> bool:
        path = os.path.join(params.projectPath, 'local.properties')
        UTracking.LogInfo('MAndroidStudio->ModifyLocalProperties', f'begin file: \'{path}\'')

        if not UOS.IsFileExist(path): 
            UTracking.LogError('MAndroidStudio->ModifyLocalProperties', 'file not existed')
            return False
        
        lines = UOS.LoadTextFile(path)
        if lines is None:
            UTracking.LogError('MAndroidStudio->ModifyLocalProperties', 'file load error')
            return False

        sdkLine = ''
        ndkLine = ''
        newLines = []
        for line in lines:
            if line.find('sdk.dir=') >= 0:
                sdkLine = line
                continue
            if line.find('ndk.dir=') >= 0:
                ndkLine = line
                continue            
            newLines.append(line)

        newSdkLine = f'sdk.dir={self.__config.gradle.sdkPath}\n'
        newNdkLine = f'ndk.dir={self.__config.gradle.ndkPath}\n'
        newLines.append(newSdkLine)
        newLines.append(newNdkLine)
        self.__LogModifyLine('MAndroidStudio->ModifyLocalProperties', sdkLine, newSdkLine)
        self.__LogModifyLine('MAndroidStudio->ModifyLocalProperties', ndkLine, newNdkLine)

        result = UOS.SaveTextFile(path, newLines, True)

        UTracking.LogInfo('MAndroidStudio->ModifyLocalProperties', 'end')
        return result

    def ModifyMainGradle(self, params : MAndroidStudioParams) -> bool:
        path = os.path.join(params.projectPath, 'build.gradle')
        return self.__ModifyGradle(path, params.mainProjectPath, True)
        
    def ModifyLauncherGradle(self, params : MAndroidStudioParams) -> bool:
        path = os.path.join(params.projectPath, 'launcher/build.gradle')
        return self.__ModifyGradle(path, params.mainProjectPath, True)

    def ModifyUnityLibraryGradle(self, params : MAndroidStudioParams) -> bool:
        path = os.path.join(params.projectPath, 'unityLibrary/build.gradle')
        return self.__ModifyGradle(path, params.mainProjectPath, True)

    def Exec(self, params : MAndroidStudioParams) -> bool:
        UTracking.LogInfo('MAndroidStudio->Exec', f'begin params: {UTracking.BeautifyLog(params.__dict__)}')

        if not UOS.IsDirectoryExist(params.projectPath): 
            UTracking.LogError('MAndroidStudio->Exec', 'project path not existed: \'' + params.projectPath + '\'')
            return False

        outputPath = params.outputAPKPath if params.APKOrAAB else params.outputAABPath
        UOS.DeleteDirectory(outputPath)
        UOS.CreateDirectory(outputPath)
        #
        os.chdir(params.projectPath)
        cmd = self.__GradleCommand('-v')
        result = UCommand.RunCmd(cmd)
        if result == 0:
            cmd = self.__GradleCommand('clean', True)
            result = UCommand.RunCmd(cmd)
            if result == 0:
                if params.APKOrAAB:
                    cmd = self.__GradleCommand('assembleRelease' if params.releaseMode else 'assembleDebug', True)
                else:
                    cmd = self.__GradleCommand('bundleRelease' if params.releaseMode else 'bundleDebug', True)
                result = UCommand.RunCmd(cmd)
                if result == 0:
                    if params.APKOrAAB:
                        srcDirectory = os.path.join(params.projectPath, 'launcher/build/outputs/apk/release/' if params.releaseMode else 'launcher/build/outputs/apk/debug/')
                    else:
                        srcDirectory = os.path.join(params.projectPath, 'launcher/build/outputs/bundle/release/' if params.releaseMode else 'launcher/build/outputs/bundle/debug/')
                    
                    if UOS.CopyFiles(srcDirectory, outputPath):
                        UTracking.LogInfo('MAndroidStudio->Exec', f'copy package, from \'{srcDirectory}\' to \'{outputPath}\'')  
                        if params.generateSymbolTable:
                            symbolsDestDirectory = os.path.join(outputPath, 'symbols/')
                            
                            il2cppSymbolsDirectory = os.path.join(params.projectPath, 'unityLibrary/symbols/')                            
                            if UOS.CopyFiles(il2cppSymbolsDirectory, symbolsDestDirectory, True):
                                UTracking.LogInfo('MAndroidStudio->Exec', f'copy symbols il2cpp, from \'{il2cppSymbolsDirectory}\' to \'{symbolsDestDirectory}\'')
                            else:
                                result = 1
                                UTracking.LogError('MAndroidStudio->Exec', f'copy symbols il2cpp failed, from \'{il2cppSymbolsDirectory}\' to \'{symbolsDestDirectory}\'')

                            if result == 0:
                                debugInformationDirectory = UOS.ChangeDirectoryName(params.projectPath, '_BurstDebugInformation_DoNotShip')
                                debugInformationDestDirectory = os.path.join(symbolsDestDirectory, 'DebugInformation/')
                                if UOS.IsDirectoryExist(debugInformationDirectory):
                                    if UOS.CopyFiles(debugInformationDirectory, debugInformationDestDirectory, True):
                                        UTracking.LogInfo('MAndroidStudio->Exec', f'copy symbols debug information, from \'{debugInformationDirectory}\' to \'{debugInformationDestDirectory}\'')
                                    else:
                                        result = 1
                                        UTracking.LogError('MAndroidStudio->Exec', f'copy symbols debug information failed, from \'{debugInformationDirectory}\' to \'{debugInformationDestDirectory}\'')

                            if result == 0:
                                for p in params.engineSymbolTablePath:
                                    if not UOS.IsDirectoryExist(p): continue
                                    if UOS.CopyFiles2D(p, symbolsDestDirectory, True):
                                        UTracking.LogInfo('MAndroidStudio->Exec', f'copy symbols engine, from \'{p}\' to \'{symbolsDestDirectory}\'')
                                    else:
                                        result = 1
                                        UTracking.LogError('MAndroidStudio->Exec', f'copy symbols engine failed, from \'{p}\' to \'{symbolsDestDirectory}\'')
                                        break                           
                    else:
                        result = 1
                        UTracking.LogError('MAndroidStudio->Exec', f'copy package failed, from \'{srcDirectory}\' to \'{outputPath}\'')  

        UTracking.LogInfo('MAndroidStudio->Exec', 'end')
        return result == 0