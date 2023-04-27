class CCDN:
    version = ''
    #
    account = ''
    password = ''
    #
    domain = ''
    loginURL = ''
    uploadLocalURL = ''
    uploadCloudURL = ''
    downloadURL = ''
    downloadURL2 = ''
    uploadRetry = 0
    downloadRetry = 0
    # example: 
    # rootPathFormats = {
    #   'AssetBundle'   : '{environment}/{server}/AssetBundle/{platform}/',
    #   'Meta'          : '{environment}/{server}/Meta/{version}/'
    #   'xyz'           : 'xxx/yyy/zzz/'
    #   ...             : ...
    # }
    rootPathFormats = {}