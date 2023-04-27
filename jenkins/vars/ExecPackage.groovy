def call(){
    currentBuild.displayName = "${env.BUILD_NUMBER}-${env.BUILD_USER}-${env.__Branch}"
    currentBuild.description = "想描述点啥就描述点啥吧！"
    //
    agentLabel = "MiniGame"
    pythonEntry = "Package.py"
    pythonParams = ""
    notifyGroup = "All"
    notifyBranch = "${env.__Branch}"
    notifyFeature = ""
    notifyMsgSuccess = "打Package成功"
    notifyMsgFailure = "打Package失败"
    notifyMsgAborted = "取消打Package了"
    basePipelineNotifyResult(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted)    
}