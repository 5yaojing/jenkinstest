def call(){
    currentBuild.displayName = "${env.BUILD_NUMBER}-${env.BUILD_USER}-${env.__Server}-${env.__Branch}"
    currentBuild.description = "想描述点啥就描述点啥吧！"
    //
    agentLabel = "COA"
    pythonEntry = "Package_Android.py"
    pythonParams = ""
    notifyGroup = "All"
    notifyBranch = "${env.__Branch}"
    notifyFeature = "NFS_Archive"
    notifyMsgSuccess = "打Android Package成功"
    notifyMsgFailure = "打Android Package失败"
    notifyMsgAborted = "取消打Android Package了"
    basePipelineNotifyResult(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted)    
}