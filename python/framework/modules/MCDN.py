import os
import requests
from requests import Request, Session
from ..utils import UBase
from ..utils import UOS
from ..utils import UTracking
from ..config.CCDN import *

class MCDN:
    __config : CCDN = None
    ################################################################ 
    def __init__(self, config : CCDN):
        if config is None:
            UTracking.RaiseException('MCDN->__init__', 'config is none')
        self.__config = config
    ######## from cdn api provider ########################################################
    def __get_token(self, username, password) -> str:
        """
        获取token
        :param username:
        :param password:
        :return:
        """
        token = ''
        resp = requests.post(self.__config.loginURL, data={'username': username, 'password': 'OPENAPI ' + password})
        if resp.status_code == 200:
            ret = resp.json()
            token = 'JWT ' + ret.get('token')        
        return token

    def __upload_local_file(self, token, localPath, path, projectName, rootPath, isPackage):
        """
        :param localPath: 本地文件路径
        :param token:
        :param path: 文件名
        :param projectName:
        :param rootPath:
        :param isPackage:
        :return:
        """
        data = {
            'path': path,
            'projectName': projectName,
            'rootPath': rootPath,
            'isPackage': 'true' if isPackage else 'false',
        }


        request = Request(
            'POST',
            self.__config.uploadLocalURL,
            headers={'Authorization': token},
            files={
                'file': open(localPath, 'rb'),
                'path': (None, data['path']),
                'projectName': (None, data['projectName']),
                'rootPath': (None, data['rootPath']),
                'isPackage': (None, data['isPackage']),
            }
        ).prepare()

        s = Session()
        response = s.send(request)

        result = True
        if response.status_code != 200:
            result = False
            UTracking.LogInfo('MCDN->__upload_local_file', f'status_code: {response.status_code}, url: {self.__config.uploadLocalURL}, localPath: {localPath}, path: {path}, projectName: {projectName}, rootPath: {rootPath}, isPackage: {isPackage}')#, full txt: {response.text}')

        return result

    # 同步文件到云存储
    def __upload_cloud_file(self, token, projectName, fileList) -> bool:
        """
        :param fileList:
        :param token:
        :param projectName:
        :return:
        """
        #upload_cloud_file(tk, PROJECT_NAME, [{'type': 'file', 'name': 'testdd/01/fstab2'}])
        data = {
            'projectName': projectName,
            'file_list': fileList,
        }

        response = None
        responseException = ''
        try:
            response = requests.post(self.__config.uploadCloudURL, json=data, headers={'Authorization': token})    
        except Exception as e:
            responseException = str(e)

        result = True
        if response is None:
            UTracking.LogInfo('MCDN->__upload_cloud_file', f'response is None, url: {self.__config.uploadCloudURL}, projectName: {projectName}, fileList: {UTracking.BeautifyLog(fileList)}, exception: {responseException}')
            result = False
            
        if result:
            if response.status_code != 200:
                result = False
                UTracking.LogInfo('MCDN->__upload_cloud_file', f'status_code: {response.status_code}, url: {self.__config.uploadCloudURL}, projectName: {projectName}, fileList: {UTracking.BeautifyLog(fileList)}')#, full txt: {response.text}')
            else:
                ret = response.json()
                responseCode = ret.get('responseCode')
                if responseCode != 200:
                    result = False
                    UTracking.LogInfo('MCDN->__upload_cloud_file', f'responseCode: {responseCode}, url: {self.__config.uploadCloudURL}, projectName: {projectName}, fileList: {UTracking.BeautifyLog(fileList)}')

        return result

    def __download_file(self, url, savePath, allowNotExisted):
        response = None
        responseException = ''
        try:
            response = requests.get(url)
        except Exception as e:
            responseException = str(e)
        
        if response is None:
            UTracking.LogInfo('MCDN->__download_file', f'response is None, url: {url}, savePath: {savePath}, exception: {responseException}')
            return False

        if response.status_code != 200:
            if allowNotExisted:
                UTracking.LogInfo('MCDN->__download_file', f'not existed at CDN, this is allowed, url: {url}')
                return True
            else:
                UTracking.LogInfo('MCDN->__download_file', f'status_code: {response.status_code}, url: {url}, savePath: {savePath}')#, full txt: {response.text}')
                return False

        if response.content is None:
            if allowNotExisted:
                UTracking.LogInfo('MCDN->__download_file', f'not existed at CDN, this is allowed, url: {url}')
                return True
            else:
                UTracking.LogInfo('MCDN->__download_file', f'content is None, url: {url}, savePath: {savePath}')
                return False

        with open(savePath, 'wb') as file:
            file.write(response.content)

        return True
    ################################################################
    def __UploadLocalFile(self, token, localPath, path, projectName, rootPath, isPackage) -> bool:
        times = max(self.__config.uploadRetry, 0) + 1

        result = False
        for i in range(0, times):
            if self.__upload_local_file(token, localPath, path, projectName, rootPath, isPackage): 
                result = True
                break
            else:
                if i == times - 1:
                    UTracking.LogError('MCDN->__UploadLocalFile', f'complete failure, url: {self.__config.uploadLocalURL}, localPath: {localPath}, path: {path}, projectName: {projectName}, rootPath: {rootPath}, isPackage: {isPackage}')
                else:
                    UTracking.LogInfo('MCDN->__UploadLocalFile', f'failed but will be try again, url: {self.__config.uploadLocalURL}, localPath: {localPath}, path: {path}, projectName: {projectName}, rootPath: {rootPath}, isPackage: {isPackage}')

        return result

    def __UploadCloudFile(self, token, projectName, fileList) -> bool:
        times = max(self.__config.uploadRetry, 0) + 1

        result = False
        for i in range(0, times):
            if self.__upload_cloud_file(token, projectName, fileList): 
                result = True
                break
            else:
                if i == times - 1:
                    UTracking.LogError('MCDN->__UploadCloudFile', f'complete failure, url: {self.__config.uploadCloudURL}, projectName: {projectName}, fileList: {UTracking.BeautifyLog(fileList)}')
                else:
                    UTracking.LogInfo('MCDN->__UploadCloudFile', f'failed but will be try again, url: {self.__config.uploadCloudURL}, projectName: {projectName}, fileList: {UTracking.BeautifyLog(fileList)}')

        return result

    def __DownloadFile(self, url, savePath, allowNotExisted):
        times = max(self.__config.downloadRetry, 0) + 1

        result = False
        for i in range(0, times):
            if self.__download_file(url, savePath, allowNotExisted): 
                result = True
                break
            else:
                if i == times - 1:
                    UTracking.LogError('MCDN->__DownloadFile', f'complete failure, url: {url}, savePath: {savePath}')
                else:
                    UTracking.LogInfo('MCDN->__DownloadFile', f'failed but will be try again, url: {url}, savePath: {savePath}')

        return result        
    ################################################################
    def __MakeRootPath(self, format : str, **kwargs) -> str:
        return format.format(**kwargs)

    def __UploadFile(self, token, file, path, project, rootPath, package, packageWithRootFolder, uploadCloud = True):
        if not self.__UploadLocalFile(token, file, path, project, rootPath, package): return False
        typeStr = 'dir' if package else 'file'
        if package:
            if packageWithRootFolder:
                path,_ = os.path.splitext(path)
                nameStr = os.path.join(rootPath, path)
            else:
                path = '\'\''
                nameStr = rootPath
        else:
            nameStr = os.path.join(rootPath, path)

        if uploadCloud:
            if not self.__UploadCloudFile(token, project, [{'type': typeStr, 'name': nameStr}]): return False

        if uploadCloud:
            UTracking.LogInfo('MCDN->__UploadFile', f'upload file: {file} to: {rootPath} package: {package} name: {path} cloud type: {typeStr} cloud name: {nameStr}')
        else:
            UTracking.LogInfo('MCDN->__UploadFile', f'upload file: {file} to: {rootPath} package: {package} name: {path}')
        return True

    def __UploadDirectory(self, token, directory, project, rootPath, package, level = 0):
        result = True

        for fn in os.listdir(directory):
            p = os.path.join(directory, fn)
            if os.path.isfile(p):
                file = p
                path = fn
                if self.__UploadLocalFile(token, file, path, project, rootPath, package):
                    UTracking.LogInfo('MCDN->__UploadDirectory', f'upload file: {file} to: {rootPath} name: {path}')
                else:
                    UTracking.LogError('MCDN->__UploadDirectory', f'upload failed, file: {file} to: {rootPath} name: {path}')
                    result = False
                    break
            elif os.path.isdir(p):
                dir = p
                rp = os.path.join(rootPath, fn)
                if not self.__UploadDirectory(token, dir, project, rp, package, level + 1):
                    result = False
                    break        
            
            if not result: break

        if result and level == 0:
            result = self.__UploadCloudFile(token, project, [{'type': 'dir', 'name': rootPath}])
            if result:
                UTracking.LogInfo('MCDN->__UploadDirectory', f'upload directory: {directory} to: {rootPath} cloud type: dir')
            else:
                UTracking.LogError('MCDN->__UploadDirectory', f'upload failed, directory: {directory}')

        return result
    ################################################################
    def MakePath(self, pathKey : str, **kwargs) -> str:
        format = self.__config.rootPathFormats.get(pathKey)
        if format is None: return ''
        return self.__MakeRootPath(format, **kwargs)
    
    def UploadFile(self, file : str, package : bool, packageWithRootFolder : bool, project : str, pathKey : str, **kwargs) -> bool:
        UTracking.LogInfo('MCDN->UploadFile', f'begin params, file: {file}, package: {package}, packageWithRootFolder: {packageWithRootFolder}, project: {project}, pathKey: {pathKey}')
        
        result = False
        if not UOS.IsFileExist(file):
            UTracking.LogError('MCDN->UploadFile', f'not found file: {file}')
        else:
            format = self.__config.rootPathFormats.get(pathKey)
            if format is None:
                UTracking.LogError('MCDN->UploadFile', 'not found format')
            else:              
                # 登陆获取token
                token = self.__get_token(self.__config.account, self.__config.password)
                if UBase.IsStringNoneOrEmpty(token):
                    UTracking.LogError('MCDN->UploadFile', 'token is empty')
                else:
                    rootPath = self.__MakeRootPath(format, **kwargs)
                    path = UOS.NameOfPath(file)                    
                    result = self.__UploadFile(token, file, path, project, rootPath, package, packageWithRootFolder)
                    if not result:
                        UTracking.LogError('MCDN->UploadFile', f'upload failed, file: {file}')
        
        UTracking.LogInfo('MCDN->UploadFile', 'end')
        return result

    def UploadFiles(self, files : list, package : bool, packageWithRootFolder : bool, project : str, pathKey : str, **kwargs) -> bool:
        UTracking.LogInfo('MCDN->UploadFiles', f'begin params, files: {UTracking.BeautifyLog(files)}, package: {package}, packageWithRootFolder: {packageWithRootFolder}, project: {project}, pathKey: {pathKey}')
        result = False

        format = self.__config.rootPathFormats.get(pathKey)
        if format is None:
            UTracking.LogError('MCDN->UploadFiles', 'not found format')
        else:
            # 登陆获取token
            token = self.__get_token(self.__config.account, self.__config.password)
            if UBase.IsStringNoneOrEmpty(token):
                UTracking.LogError('MCDN->UploadFiles', 'token is empty')
            else:
                result = True
                rootPath = self.__MakeRootPath(format, **kwargs)
                for file in files:
                    if not UOS.IsFileExist(file):
                        result = False
                        UTracking.LogError('MCDN->UploadFiles', f'not found file: {file}')
                    else:
                        path = UOS.NameOfPath(file)
                        if not self.__UploadFile(token, file, path, project, rootPath, package, packageWithRootFolder):
                            result = False
                            UTracking.LogError('MCDN->UploadFiles', f'upload failed, file: {file}')
                    if not result: break                        

        UTracking.LogInfo('MCDN->UploadFiles', 'end')
        return result

    def UploadFilesInDirectory(self, directory : str, files : list, package : bool, packageWithRootFolder : bool, project : str, pathKey : str, **kwargs) -> bool:
        UTracking.LogInfo('MCDN->UploadFilesInDirectory', f'begin params, directory: {directory}, files: {UTracking.BeautifyLog(files)}, package: {package}, packageWithRootFolder: {packageWithRootFolder}, project: {project}, pathKey: {pathKey}')
        result = False

        format = self.__config.rootPathFormats.get(pathKey)
        if format is None:
            UTracking.LogError('MCDN->UploadFilesInDirectory', 'not found format')
        else:
            # 登陆获取token
            token = self.__get_token(self.__config.account, self.__config.password)
            if UBase.IsStringNoneOrEmpty(token):
                UTracking.LogError('MCDN->UploadFilesInDirectory', 'token is empty')
            else:
                result = True

                rootPath = self.__MakeRootPath(format, **kwargs)
                for f in files:
                    file = os.path.join(directory, f)
                    if not UOS.IsFileExist(file):
                        result = False
                        UTracking.LogError('MCDN->UploadFilesInDirectory', f'not found file: {file}')
                    else:
                        path = UOS.NameOfPath(file)
                        if not self.__UploadFile(token, file, path, project, rootPath, package, packageWithRootFolder, False):
                            result = False
                            UTracking.LogError('MCDN->UploadFilesInDirectory', f'upload failed, file: {file}')
                    if not result: break                        

                if result:
                    result = self.__UploadCloudFile(token, project, [{'type': 'dir', 'name': rootPath}])
                    if result:
                        UTracking.LogInfo('MCDN->UploadFilesInDirectory', f'upload directory: {directory} to: {rootPath} cloud type: dir')
                    else:
                        UTracking.LogError('MCDN->UploadFilesInDirectory', f'upload failed, directory: {directory}')
                
        UTracking.LogInfo('MCDN->UploadFilesInDirectory', 'end')
        return result

    def UploadDirectory(self, directory : str, package : bool, project : str, pathKey : str, **kwargs) -> bool:        
        UTracking.LogInfo('MCDN->UploadDirectory', f'begin params, directory: {directory}, project: {project}, pathKey: {pathKey}')
        result = False
        if not UOS.IsDirectoryExist(directory):
            UTracking.LogError('MCDN->UploadDirectory', f'not found directory: {directory}')
        else:
            format = self.__config.rootPathFormats.get(pathKey)
            if format is None:
                UTracking.LogError('MCDN->UploadDirectory', 'not found format')
            else:              
                # 登陆获取token
                token = self.__get_token(self.__config.account, self.__config.password)
                if UBase.IsStringNoneOrEmpty(token):
                    UTracking.LogError('MCDN->UploadDirectory', 'token is empty')
                else:
                    rootPath = self.__MakeRootPath(format, **kwargs)
                    result = self.__UploadDirectory(token, directory, project, rootPath, package)

        UTracking.LogInfo('MCDN->UploadDirectory', 'end')
        return result

    def DownloadFile(self, remoteFile : str, saveDirectory : str, allowNotExisted : bool, pathKey : str, **kwargs) -> bool:
        UTracking.LogInfo('MCDN->DownloadFile', f'begin params, remoteFile: {remoteFile}, saveDirectory: {saveDirectory}, allowNotExisted: {allowNotExisted}, pathKey: {pathKey}')
        
        fileName = UOS.NameOfPath(remoteFile)
        savePath = os.path.join(saveDirectory, fileName)
        
        if not UOS.IsDirectoryExist(saveDirectory):
            UOS.CreateDirectory(saveDirectory)
        if UOS.IsFileExist(savePath):
            UOS.DeleteFile(savePath)

        result = False
        format = self.__config.rootPathFormats.get(pathKey)
        if format is None:
            UTracking.LogError('MCDN->DownloadFile', 'not found format')
        else:              
            rootPath = self.__MakeRootPath(format, **kwargs)
            remoteFile = os.path.join(rootPath, remoteFile)
            url = os.path.join(self.__config.downloadURL, remoteFile)
            result = self.__DownloadFile(url, savePath, allowNotExisted)
            if result:
                UTracking.LogInfo('MCDN->DownloadFile', f'download successed, url1: {url} to: {savePath}')
            else:
                url2 = os.path.join(self.__config.downloadURL2, remoteFile)
                result = self.__DownloadFile(url2, savePath, allowNotExisted)
                if result:
                    UTracking.LogInfo('MCDN->DownloadFile', f'download successed, url2: {url2} to: {savePath}')
                else:
                    UTracking.LogError('MCDN->DownloadFile', f'download failed')
        
        UTracking.LogInfo('MCDN->DownloadFile', 'end')
        return result
