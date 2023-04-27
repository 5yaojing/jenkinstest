def call(){
    currentBuild.displayName = "${env.BUILD_NUMBER}-${env.BUILD_USER}-${env.__Server}-${env.__Platform}"
    currentBuild.description = "想描述点啥就描述点啥吧！"
    //
    agentLabel = "COA"
    pythonEntry = "PublishTool.py"
    pythonParams = ""
    notifyGroup = "All"
    notifyBranch = ""
    notifyFeature = ""
    notifyMsgSuccess = "发布成功,服务器(${env.__Server}),平台(${env.__Platform})"
    notifyMsgFailure = "发布失败,服务器(${env.__Server}),平台(${env.__Platform})"
    notifyMsgAborted = "取消发布,服务器(${env.__Server}),平台(${env.__Platform})"
    basePipelineNotifyResult(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted)    
}