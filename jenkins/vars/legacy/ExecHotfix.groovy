def call(){
    currentBuild.displayName = "${env.BUILD_NUMBER}-${env.BUILD_USER}-${env.__Server}-${env.__Branch}"
    currentBuild.description = "想描述点啥就描述点啥吧！"
    //
    agentLabel = "COA"
    pythonEntry = "Hotfix.py"
    pythonParams = ""
    notifyGroup = "All"
    notifyBranch = "${env.__Branch}"
    notifyFeature = ""
    notifyMsgSuccess = "打${env.__Platform} Hotfix成功"
    notifyMsgFailure = "打${env.__Platform} Hotfix失败"
    notifyMsgAborted = "取消打${env.__Platform} Hotfix了"
    basePipelineNotifyResult(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted)    
}