from enum import Enum
from framework.config.CCDN import *

class CCDNProjectEnum(Enum):
    XProject = '海外X项目'
    
class CCDNResourceEnum(Enum):
    AssetBundle = 'AssetBundle'
    Manifest = 'Manifest'

class CCDNProduct(CCDN):
    version = '0.0.0'
    #
    account = 'coa_jenkins@tuyoogame.com'
    password = 'COa2022!'
    #
    domain = 'https://cdnnew.tuyoo.com/'
    loginURL= f'{domain}rbac/login/'
    uploadLocalURL = f'{domain}api/v1/upload/uploadFile/'
    uploadCloudURL = f'{domain}api/v1/upload/syncFiles/'
    downloadURL = 'https://122-xproject-cdn-aws.qijihdhk.com/xprojecthw/'
    downloadURL2 = 'https://122-xproject-cdn-ali.tytuyoo.com/xprojecthw/'
    uploadRetry = 3
    downloadRetry = 3
    rootPathFormats = {
        'AssetBundle' : 'MiniGame/{game}/{buildVersion}/{bundleVersion}/',
        'Manifest'    : 'MiniGame/{game}/{buildVersion}/'
    }