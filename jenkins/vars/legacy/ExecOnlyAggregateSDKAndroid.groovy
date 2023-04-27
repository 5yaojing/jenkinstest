def call(){
    currentBuild.displayName = "${env.BUILD_NUMBER}-${env.BUILD_USER}-${env.__PackageJobName}-${env.__PackageBuildNumber}"
    currentBuild.description = "想描述点啥就描述点啥吧！"
    //
    agentLabel = "COA"
    pythonEntry = "OnlyAggregateSDK_Android.py"
    pythonParams = ""
    notifyGroup = "All"
    notifyBranch = ""
    notifyFeature = ""
    notifyMsgSuccess = "聚合Android SDK成功"
    notifyMsgFailure = "聚合Android SDK失败"
    notifyMsgAborted = "取消聚合Android SDK了"
    basePipelineNotifyResult(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted)    
}