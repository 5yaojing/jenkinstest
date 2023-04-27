def call(agentLabel, pythonEntry, pythonParams, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess, notifyMsgFailure, notifyMsgAborted){
    pipeline {
        agent {
            node {
                label "${agentLabel}"
            }
        }
        // parameters {
        //     string(name: '__Test', defaultValue: 'test', description: '测试的，没其他用')
        // }
        stages {
            stage ('Prepare'){
                steps {
                    script {                        
                        base.DoDefineVars()
                        base.DoDefinePythonVars()
                        base.DoPrintEnv()
                    }
                }
            }
            
            stage ('Git'){
                steps {
                    script {
                        base.DoGit()
                    }
                }
            }

            stage('Action') {
                steps {
                    script {
                        base.DoAction(pythonEntry, pythonParams)
                    }
                }
            }
        }
        post {        
            always {
                script {
                    base.DoCleanResidual()
                }
            }    
            success {
                script {
                    if ("${notifyMsgSuccess}")
                    {
                        base.DoNotifyResult(0, notifyGroup, notifyBranch, notifyFeature, notifyMsgSuccess)
                    }
                }
            }
            failure {
                script {
                    if ("${notifyMsgFailure}")
                    {
                        base.DoNotifyResult(1, notifyGroup, notifyBranch, notifyFeature, notifyMsgFailure)
                    }
                }
            }
            
            aborted {                
                script {                    
                    if ("${notifyMsgAborted}")
                    {
                        base.DoNotifyResult(2, notifyGroup, notifyBranch, notifyFeature, notifyMsgAborted)
                    }
                }
            }
            // unstable {
            // }            
        }
    }    
}