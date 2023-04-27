def call(){
    currentBuild.displayName = "${env.BUILD_NUMBER}-${env.BUILD_USER}-${env.__Branch}"
    currentBuild.description = "想描述点啥就描述点啥吧！"
    //
    agentLabel = "COA"
    pythonEntry = "ResourceVerifier.py"
    pythonParams = ""
    notifyGroup = "All"
    notifyBranch = "${env.__Branch}"
    notifyFeature = ""
    notifyMsgSuccess = "验证${env.__Platform} 资源成功"
    notifyMsgFailure = "验证${env.__Platform} 资源失败"
    notifyMsgAborted = "取消验证${env.__Platform} 资源了"
    basePipelineNotifyResult(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted)    
}