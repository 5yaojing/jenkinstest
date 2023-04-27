def call(){
    agentLabel = "COA"
    pythonEntry = "Test.py"
    pythonParams = ""
    notifyGroup = "All"
    notifyBranch = "what你好"
    notifyFeature = ""
    notifyMsgSuccess = "n这次你是成功的"
    notifyMsgFailure = "b这次你失败了"
    notifyMsgAborted = "c这次你取消了"
    basePipelineNotifyResult(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted)    
}