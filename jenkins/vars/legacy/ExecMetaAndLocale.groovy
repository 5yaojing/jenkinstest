def call(){
    currentBuild.displayName = "${env.BUILD_NUMBER}-${env.BUILD_USER}-${env.__Purpose}-${env.__Server}-${env.__BranchMetadata}"
    currentBuild.description = "想描述点啥就描述点啥吧！"
    //
    agentLabel = "COA"
    pythonEntry = "MetaAndLocale.py"
    pythonParams = ""
    notifyGroup = "All"
    if (env.__SyncUnity == "true") {
        notifyBranch = "Metadata:${env.__BranchMetadata}, Server:${env.__BranchServer}, Unity:${env.__BranchUnity}"
    }
    else {
        notifyBranch = "Metadata:${env.__BranchMetadata}, Server:${env.__BranchServer}"
    }
    notifyFeature = ""
    notifyMsgSuccess = ""
    notifyMsgFailure = ""
    notifyMsgAborted = ""
    if (env.__Purpose == "Locale") {
        notifyMsgSuccess = "生成Locale成功"
        notifyMsgFailure = "生成Locale失败"
        notifyMsgAborted = "取消生成Locale了"
    }
    else if (env.__Purpose == "Meta") {
        notifyMsgSuccess = "生成Meta成功"
        notifyMsgFailure = "生成Meta失败"
        notifyMsgAborted = "取消生成Meta了"
    }
    else
    {        
        notifyMsgSuccess = "生成Meta和Locale成功"
        notifyMsgFailure = "生成Meta和Locale失败"
        notifyMsgAborted = "取消生成Meta和Locale了"
    }
    basePipelineNotifyResult(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted)    
}