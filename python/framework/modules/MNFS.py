import os
import requests
from requests import Request, Session
from ..utils import UBase
from ..utils import UOS
from ..utils import UTracking
from ..config.CNFS import *

class MNFS:
    __config : CNFS = None
    ################################################################ 
    def __init__(self, config : CNFS):
        if config is None:
            UTracking.RaiseException('MNFS->__init__', 'config is none')
        self.__config = config
    ################################################################
    # def __upload_file(self, localPath, path, rootPath):
    #     UTracking.RaiseException('MNFS->__upload_file', 'can\'t be used')
    #     url = f'{self.__config.uploadURL}{rootPath}'
    #     request = Request(
    #         'POST',
    #         url,
    #         files={
    #             'file': open(localPath, 'rb'),
    #             'path': (None, path)
    #         }
    #     ).prepare()

    #     s = Session()
    #     response = s.send(request)

    #     result = True
    #     if response.status_code != 200:
    #         result = False
    #         UTracking.LogInfo('MNFS->__upload_file', f'status_code: {response.status_code}, url: {self.__config.uploadURL}, localPath: {localPath}, path: {path}, rootPath: {rootPath}')

    #     return result

    def __download_file(self, url, savePath, allowNotExisted):
        response = None
        responseException = ''
        try:
            response = requests.get(url)
        except Exception as e:
            responseException = str(e)
        
        if response is None:
            UTracking.LogInfo('MNFS->__download_file', f'response is None, url: {url}, savePath: {savePath}, exception: {responseException}')
            return False

        if response.status_code != 200:
            if allowNotExisted:
                UTracking.LogInfo('MNFS->__download_file', f'not existed at NFS, this is allowed, url: {url}')
                return True
            else:
                UTracking.LogInfo('MNFS->__download_file', f'status_code: {response.status_code}, url: {url}, savePath: {savePath}')
                return False

        if response.content is None:
            if allowNotExisted:
                UTracking.LogInfo('MNFS->__download_file', f'not existed at NFS, this is allowed, url: {url}')
                return True
            else:
                UTracking.LogInfo('MNFS->__download_file', f'content is None, url: {url}, savePath: {savePath}')
                return False

        with open(savePath, 'wb') as file:
            file.write(response.content)

        return True
    ################################################################
    # def __UploadFile(self, localPath, path, rootPath) -> bool:
    #     times = max(self.__config.uploadRetry, 0) + 1

    #     result = False
    #     for i in range(0, times):
    #         if self.__upload_file(localPath, path, rootPath): 
    #             result = True
    #             break
    #         else:
    #             if i == times - 1:
    #                 UTracking.LogError('MNFS->__UploadFile', f'complete failure, url: {self.__config.uploadURL}, localPath: {localPath}, path: {path}, rootPath: {rootPath}')
    #             else:
    #                 UTracking.LogInfo('MNFS->__UploadFile', f'failed but will be try again, url: {self.__config.uploadURL}, localPath: {localPath}, path: {path}, rootPath: {rootPath}')
        
    #     if result:
    #          UTracking.LogInfo('MNFS->__UploadFile', f'upload successed, file: {localPath} to: {rootPath} name: {path}')

    #     return result

    def __DownloadFile(self, url, savePath, allowNotExisted):
        times = max(self.__config.downloadRetry, 0) + 1

        result = False
        for i in range(0, times):
            if self.__download_file(url, savePath, allowNotExisted): 
                result = True
                break
            else:
                if i == times - 1:
                    UTracking.LogError('MNFS->__DownloadFile', f'complete failure, url: {url}, savePath: {savePath}')
                else:
                    UTracking.LogInfo('MNFS->__DownloadFile', f'failed but will be try again, url: {url}, savePath: {savePath}')

        if result:
             UTracking.LogInfo('MNFS->DownloadFile', f'download successed, url: {url} to: {savePath}')

        return result        
    ################################################################
    def __MakeRootPath(self, format : str, **kwargs) -> str:
        return format.format(**kwargs)

    def __MakeUploadPath(self, format : str, **kwargs) -> str:
        path = format.format(**kwargs)
        return os.path.join(self.__config.uploadURL, path)

    def __MakeDownloadPath(self, format : str, **kwargs) -> str:
        path = format.format(**kwargs)
        return os.path.join(self.__config.downloadURL, path)

    def __MakeDiskPath(self, format : str, **kwargs) -> str:
        path = format.format(**kwargs)
        return os.path.join(self.__config.diskLink, path)

    ################################################################
    def MakeDownloadPath(self, pathKey : str, **kwargs) -> str:
        format = self.__config.rootPathFormats.get(pathKey)
        if format is None: return ''
        return self.__MakeDownloadPath(format, **kwargs)

    def MakeDiskPath(self, pathKey : str, **kwargs) -> str:
        format = self.__config.rootPathFormats.get(pathKey)
        if format is None: return ''
        return self.__MakeDiskPath(format, **kwargs)

    # def __UploadDirectory(self, directory, rootPath, level = 0):
    #     result = True

    #     for fn in os.listdir(directory):
    #         p = os.path.join(directory, fn)
    #         if os.path.isfile(p):
    #             file = p
    #             path = fn
    #             if self.__UploadFile(file, path, rootPath):
    #                 UTracking.LogInfo('MNFS->__UploadDirectory', f'upload file: {file} to: {rootPath} name: {path}')
    #             else:
    #                 UTracking.LogError('MNFS->__UploadDirectory', f'upload failed, file: {file} to: {rootPath} name: {path}')
    #                 result = False
    #                 break
    #         elif os.path.isdir(p):
    #             dir = p
    #             rp = os.path.join(rootPath, fn)
    #             if not self.__UploadDirectory(dir, rp, level + 1):
    #                 result = False
    #                 break        
            
    #         if not result: break

    #     if result and level == 0:
    #         UTracking.LogInfo('MNFS->__UploadDirectory', f'upload successed, directory: {directory} to: {rootPath}')

    #     return result
    ################################################################
    # def UploadFile(self, file : str, pathKey : str, **kwargs) -> bool:
    #     UTracking.LogInfo('MNFS->UploadFile', f'begin params, file: {file}, pathKey: {pathKey}')
        
    #     result = False
    #     if not UOS.IsFileExist(file):
    #         UTracking.LogError('MNFS->UploadFile', f'not found file: {file}')
    #     else:
    #         format = self.__config.rootPathFormats.get(pathKey)
    #         if format is None:
    #             UTracking.LogError('MNFS->UploadFile', 'not found format')
    #         else:              
    #             rootPath = self.__MakeRootPath(format, **kwargs)
    #             path = UOS.NameOfPath(file)                    
    #             result = self.__UploadFile(file, path, rootPath)
    #             if not result:
    #                 UTracking.LogError('MNFS->UploadFile', f'upload failed, file: {file}')
        
    #     UTracking.LogInfo('MNFS->UploadFile', 'end')
    #     return result

    # def UploadFiles(self, files : list, pathKey : str, **kwargs) -> bool:
    #     UTracking.LogInfo('MNFS->UploadFiles', f'begin params, files: {UTracking.BeautifyLog(files)}, pathKey: {pathKey}')
    #     result = False

    #     format = self.__config.rootPathFormats.get(pathKey)
    #     if format is None:
    #         UTracking.LogError('MNFS->UploadFiles', 'not found format')
    #     else:
    #         result = True
    #         rootPath = self.__MakeRootPath(format, **kwargs)
    #         for file in files:
    #             if not UOS.IsFileExist(file):
    #                 result = False
    #                 UTracking.LogError('MNFS->UploadFiles', f'not found file: {file}')
    #             else:
    #                 path = UOS.NameOfPath(file)
    #                 if not self.__UploadFile(file, path, rootPath):
    #                     result = False
    #                     UTracking.LogError('MNFS->UploadFiles', f'upload failed, file: {file}')
    #             if not result: break                        

    #     UTracking.LogInfo('MNFS->UploadFiles', 'end')
    #     return result

    # def UploadFilesInDirectory(self, directory : str, files : list, pathKey : str, **kwargs) -> bool:
    #     UTracking.LogInfo('MNFS->UploadFilesInDirectory', f'begin params, directory: {directory}, files: {UTracking.BeautifyLog(files)}, pathKey: {pathKey}')
    #     result = False

    #     format = self.__config.rootPathFormats.get(pathKey)
    #     if format is None:
    #         UTracking.LogError('MNFS->UploadFilesInDirectory', 'not found format')
    #     else:
    #         result = True

    #         rootPath = self.__MakeRootPath(format, **kwargs)
    #         for f in files:
    #             file = os.path.join(directory, f)
    #             if not UOS.IsFileExist(file):
    #                 result = False
    #                 UTracking.LogError('MNFS->UploadFilesInDirectory', f'not found file: {file}')
    #             else:
    #                 path = UOS.NameOfPath(file)
    #                 if not self.__UploadFile(file, path, rootPath):
    #                     result = False
    #                     UTracking.LogError('MNFS->UploadFilesInDirectory', f'upload failed, file: {file}')
    #             if not result: break
                
    #     UTracking.LogInfo('MNFS->UploadFilesInDirectory', 'end')
    #     return result

    # def UploadDirectory(self, directory : str, pathKey : str, **kwargs) -> bool:        
    #     UTracking.LogInfo('MNFS->UploadDirectory', f'begin params, directory: {directory}, pathKey: {pathKey}')
    #     result = False
    #     if not UOS.IsDirectoryExist(directory):
    #         UTracking.LogError('MNFS->UploadDirectory', f'not found directory: {directory}')
    #     else:
    #         format = self.__config.rootPathFormats.get(pathKey)
    #         if format is None:
    #             UTracking.LogError('MNFS->UploadDirectory', 'not found format')
    #         else:              
    #             rootPath = self.__MakeRootPath(format, **kwargs)
    #             result = self.__UploadDirectory(directory, rootPath)

    #     UTracking.LogInfo('MNFS->UploadDirectory', 'end')
    #     return result

    def DownloadFile(self, remoteFile : str, saveDirectory : str, allowNotExisted : bool, pathKey : str, **kwargs) -> bool:
        fileName = UOS.NameOfPath(remoteFile)
        savePath = os.path.join(saveDirectory, fileName)
        
        if not UOS.IsDirectoryExist(saveDirectory):
            UOS.CreateDirectory(saveDirectory)
        if UOS.IsFileExist(savePath):
            UOS.DeleteFile(savePath)

        result = False
        format = self.__config.rootPathFormats.get(pathKey)
        if format is None:
            UTracking.LogError('MNFS->DownloadFile', f'not found format, pathKey:{pathKey}')
        else:              
            downloadPath = self.__MakeDownloadPath(format, **kwargs)
            url = os.path.join(downloadPath, remoteFile)
            result = self.__DownloadFile(url, savePath, allowNotExisted)

        return result
    ################################################################
    def CopyFileToNFS(self, localFile : str, pathKey : str, **kwargs) -> bool:
        result = False
        if not UOS.IsFileExist(localFile):
            UTracking.LogError('MNFS->CopyFileToNFS', f'not found file: {localFile}')
        else:
            format = self.__config.rootPathFormats.get(pathKey)
            if format is None:
                UTracking.LogError('MNFS->CopyFileToNFS', f'not found format, pathKey:{pathKey}')
            else:              
                nfsDirectory = self.__MakeDiskPath(format, **kwargs)     
                result = UOS.CopyFile2D(localFile, nfsDirectory, True)
                if result:
                    UTracking.LogInfo('MNFS->CopyFileToNFS', f'copy successed, from: {localFile} to: {nfsDirectory}')
                else:
                    UTracking.LogError('MNFS->CopyFileToNFS', f'copy failed, from: {localFile} to: {nfsDirectory}')

        return result

    def CopyFileFromNFS(self, localDirectory : str, nfsFileName : str, pathKey : str, **kwargs) -> bool:
        result = False
        format = self.__config.rootPathFormats.get(pathKey)
        if format is None:
            UTracking.LogError('MNFS->CopyFileFromNFS', f'not found format, pathKey:{pathKey}')
        else:
            nfsDirectory = self.__MakeDiskPath(format, **kwargs)
            nfsFile = os.path.join(nfsDirectory, nfsFileName)
            if not UOS.IsFileExist(nfsFile):
                UTracking.LogError('MNFS->CopyFileFromNFS', f'not found file: {nfsFile}')
            else:              
                result = UOS.CopyFile2D(nfsFile, localDirectory, True)
                if result:
                    UTracking.LogInfo('MNFS->CopyFileFromNFS', f'copy successed, from: {nfsFile} to: {localDirectory}')
                else:
                    UTracking.LogError('MNFS->CopyFileFromNFS', f'copy failed, from: {nfsFile} to: {localDirectory}')

        return result

    def CopyFilesToNFS(self, localDirectory : str, pathKey : str, **kwargs) -> bool:
        result = False
        if not UOS.IsDirectoryExist(localDirectory):
            UTracking.LogError('MNFS->CopyFilesToNFS', f'not found directory: {localDirectory}')
        else:
            format = self.__config.rootPathFormats.get(pathKey)
            if format is None:
                UTracking.LogError('MNFS->CopyFilesToNFS', f'not found format, pathKey:{pathKey}')
            else:
                nfsDirectory = self.__MakeDiskPath(format, **kwargs)
                result = UOS.CopyFiles(localDirectory, nfsDirectory, True)
                if result:
                    UTracking.LogInfo('MNFS->CopyFilesToNFS', f'copy successed, from: {localDirectory} to: {nfsDirectory}')
                else:
                    UTracking.LogError('MNFS->CopyFilesToNFS', f'copy failed, from: {localDirectory} to: {nfsDirectory}')

        return result

    def CopyFilesFromNFS(self, localDirectory : str, pathKey : str, **kwargs) -> bool:
        result = False
        format = self.__config.rootPathFormats.get(pathKey)
        if format is None:
            UTracking.LogError('MNFS->CopyFilesFromNFS', f'not found format, pathKey:{pathKey}')        
        else:
            nfsDirectory = self.__MakeDiskPath(format, **kwargs)
            if not UOS.IsDirectoryExist(nfsDirectory):
                UTracking.LogError('MNFS->CopyFilesFromNFS', f'not found directory: {nfsDirectory}')
            else:                
                result = UOS.CopyFiles(nfsDirectory, localDirectory, True)
                if result:
                    UTracking.LogInfo('MNFS->CopyFilesFromNFS', f'copy successed, from: {nfsDirectory} to: {localDirectory}')
                else:
                    UTracking.LogError('MNFS->CopyFilesFromNFS', f'copy failed, from: {nfsDirectory} to: {localDirectory}')

        return result
    ################################################################
    def DeleteFileFromNFS(self, nfsFileName : str, pathKey : str, **kwargs) -> bool:
        result = False
        format = self.__config.rootPathFormats.get(pathKey)
        if format is None:
            UTracking.LogError('MNFS->DeleteFileFromNFS', f'not found format, pathKey:{pathKey}')
        else:
            result = True
            nfsDirectory = self.__MakeDiskPath(format, **kwargs)
            nfsFile = os.path.join(nfsDirectory, nfsFileName)
            if UOS.IsFileExist(nfsFile):
                UOS.DeleteFile(nfsFile)
                UTracking.LogInfo('MNFS->DeleteFileFromNFS', f'delete file: {nfsFile}')                
            else:
                UTracking.LogInfo('MNFS->DeleteFileFromNFS', f'done, not found file: {nfsFile}')

        return result

    def DeleteDirectoryFromNFS(self, pathKey : str, **kwargs) -> bool:
        result = False

        format = self.__config.rootPathFormats.get(pathKey)
        if format is None:
            UTracking.LogError('MNFS->DeleteDirectoryFromNFS', f'not found format, pathKey:{pathKey}')
        else:
            result = True
            nfsDirectory = self.__MakeDiskPath(format, **kwargs)     
            if UOS.IsDirectoryExist(nfsDirectory):
                UOS.DeleteDirectory(nfsDirectory)
                UTracking.LogInfo('MNFS->DeleteDirectoryFromNFS', f'delete directory: {nfsDirectory}')                
            else:
                UTracking.LogInfo('MNFS->DeleteDirectoryFromNFS', f'done, not found directory: {nfsDirectory}')

        return result