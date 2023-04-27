def call(){
    currentBuild.displayName = "${env.BUILD_NUMBER}-${env.BUILD_USER}-${env.__Server}-${env.__Branch}"
    currentBuild.description = "想描述点啥就描述点啥吧！"
    //
    agentLabel = "COA"
    pythonEntry = "AssetBundle.py"
    pythonParams = ""
    notifyGroup = "All"
    notifyBranch = "${env.__Branch}"
    notifyFeature = ""
    notifyMsgSuccess = "打${env.__Platform} AssetBundle成功"
    notifyMsgFailure = "打${env.__Platform} AssetBundle失败"
    notifyMsgAborted = "取消打${env.__Platform} AssetBundle了"
    basePipelineNotifyResult(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted)    
}