class CProject:
    name = ''
    root = ''
    busyMark = ''
    # example: 
    # gitRepositorys = {
    #   'name1' : {
    #       'url':'https://tygit.tuyoo.com/unicorn/xxx.git', 
    #       'location':'yyy'
    #   },
    #   'name2' : {
    #       'url':'https://tygit.tuyoo.com/unicorn/xxxxxx.git', 
    #       'location':'yyyyyy'
    #   }
    # }
    gitRepositorys = {}
    #
    untiyRoot = ''    
    unityExportPathApple = ''
    unityExportPathAndroid = ''
    unityExportPathWindows = ''
    unityExportPathLinux = ''
    #
    appleRoot = ''
    xcodeProjectPath = ''
    xcodeWorkspace = False
    # xcodeWorkspace is True : xxx.workspace, 
    # otherwise : yyy.xcodeproj
    xcodeProjectFile = ''
    #
    androidRoot = ''
    androidStudioProjectPath = ''
    androidStudioOutputAPKPath = ''
    androidStudioOutputAABPath = ''
    androidAggregateSDKOutputAPKPath = ''
    androidAggregateSDKOutputAABPath = ''
    #
    windowsRoot = ''
    #
    linuxRoot = ''
    #
    minigameRoot = ''
    minigameOutputPath = ''
    #
    tempLocation = ''
    #
    archiveLocation = ''