def call(pythonEntry, pythonParams){
    pipeline {
        agent any
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
        }
    }    
}