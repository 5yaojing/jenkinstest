class CNFS:
    version         = ''

    diskLink        = ''

    domain          = ''
    uploadURL       = ''
    downloadURL     = ''
    uploadRetry     = 0
    downloadRetry   = 0
    # example: 
    # rootPathFormats = {
    #   'AssetBundle'   : '{environment}/{server}/AssetBundle/{platform}/',
    #   'Meta'          : '{environment}/{server}/Meta/{version}/'
    #   'xyz'           : 'xxx/yyy/zzz/'
    #   ...             : ...
    # }
    rootPathFormats = {}
