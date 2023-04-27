def DoDefineVars()
{
    if (isUnix()) {
        env._PYTHON_PATH = 'python3'
    }
    else{
        env._PYTHON_PATH = 'python'
    }
    env._FRAMEWORK_PATH = './Framework/'
    env._JOB_ACTION_PATH = './Framework/python/'
    //
    env._FRAMEWORK_GIT_URL = 'https://tygit.tuyoo.com/unicorn/SLGJenkins_Python.git'
    env._FRAMEWORK_GIT_CREDENTIALS_ID = 'COACredentialID'
    env._FRAMEWORK_GIT_BRANCH = 'minigame'
}

def DoDefinePythonVars()
{
    env.___BUSY_MARK_TAG = env.BUILD_TAG
}

def DoPrintEnv()
{
    str = ''
    env.getEnvironment().each { name, value -> str += "Env: ${name} -> ${value}\n" }
    print(str)
}

def DoGit()
{
    dir(path: env._FRAMEWORK_PATH) {	
        git(
            branch: env._FRAMEWORK_GIT_BRANCH,
            credentialsId: env._FRAMEWORK_GIT_CREDENTIALS_ID,				
            url : env._FRAMEWORK_GIT_URL,
            changelog: true
        )
    }	
}

def DoCommand(cmd)
{
    if (isUnix()) {
        sh encoding: 'utf-8', script: """
            ${cmd}
        """
    }
    else
    {
        bat encoding: 'utf-8', script: """
            chcp 65001
            ${cmd}
        """
        //bat """
        //    CALL C:/Users/TU/miniconda3/condabin/conda.bat activate Jenkins
        //    C:/Users/TU/miniconda3/python D:/Node/UpdatePython.py
        //    CALL C:/Users/TU/miniconda3/condabin/conda.bat deactivate
        //"""
    }
}

def DoAction(pythonEntry, pythonParams)
{
    DoCommand("${env._PYTHON_PATH} -u ${env._JOB_ACTION_PATH}${pythonEntry} ${pythonParams}")
}

def DoNotifyResult(code, group, branch, feature, message)
{
    DoCommand("${env._PYTHON_PATH} -u ${env._JOB_ACTION_PATH}NotifyResult.py -c ${code} -g \"${group}\" -b \"${branch}\" -f \"${feature}\" -m \"${message}\"")
}

def DoCleanResidual()
{
    DoCommand("${env._PYTHON_PATH} -u ${env._JOB_ACTION_PATH}CleanResidual.py")
}

CleanResidual.py