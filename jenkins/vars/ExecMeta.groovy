def call(){
    currentBuild.displayName = "${env.BUILD_NUMBER}-${env.BUILD_USER}-${env.__BranchData}-${env.__BranchClient}"
    currentBuild.description = "想描述点啥就描述点啥吧！"
    //
    agentLabel = "MiniGame"
    pythonEntry = "Meta.py"
    pythonParams = ""
    notifyGroup = "All"
    notifyBranch = "Data:${env.__BranchData}, Client:${env.__BranchClient}"
    notifyFeature = ""
    notifyMsgSuccess = "生成Meta成功"
    notifyMsgFailure = "生成Meta失败"
    notifyMsgAborted = "取消生成Meta了"
    basePipelineNotifyResult(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted)    
}