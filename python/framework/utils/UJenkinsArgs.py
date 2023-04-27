import os
import re
from . import UOS

#默认变量，自动填写
def FromDefault() -> dict:
    result = {}
    #
    busyMaskTag = os.environ.get('___BUSY_MARK_TAG')
    if busyMaskTag is None or busyMaskTag == '':
        raise RuntimeError(f'UJenkinsArgs->FromDefault, ___BUSY_MARK_TAG not found!')
    result['bmt975310'] = busyMaskTag
    #
    return result

#从环境变量转换成我们的变量，这个处理虽然多一道手续，但可以校验参数有效性
#descs : list of tuple(var name : string, alias : string, type, default)
def FromEnvironment (descs : list = None) -> dict:
    result = FromDefault()
    if descs is None: return result
    
    for key, alias, et, default in descs:
        dt = type(default)
        if et != dt:
            raise RuntimeError(f'UJenkinsArgs->FromEnvironment, key {key}, type {et} expected, but type of default is {dt}')

        if alias == '':
            raise RuntimeError(f'UJenkinsArgs->FromEnvironment, key {key}, alias is empty!')

        if not result.get(alias) is None:
            raise RuntimeError(f'UJenkinsArgs->FromEnvironment, key {key}, alias {alias} is duplicated!')

        value = os.environ.get(key)
        if value is None:
            result[alias] = default
        else:
            v = value
            successed = True            
            if et == int:
                try: v = int(value) 
                except: successed = False                        
            elif et == float:
                try: v = float(value) 
                except: successed = False 
            elif et == bool:
                v = True if value.lower() == 'true' else False

            if successed:
                result[alias] = v
            else:
                raise RuntimeError(f'UJenkinsArgs->FromEnvironment, key {key}, type {et} expected, but value is {value}')

    return result

#检测是否从Jenkins调用（利用传入环境变量），如果是则抛异常
def RaiseIfComingFromJenkins(function : str):
    check0 = os.environ.get('JENKINS_HOME')
    check1 = os.environ.get('JOB_BASE_NAME')
    check2 = os.environ.get('___BUSY_MARK_TAG')

    if check0 is None: return
    if check1 is None: return
    if check2 is None: return
    message = f'can\'t call function({function}) when coming from jenkins, kill it first!'
    raise RuntimeError(f'UJenkinsArgs->RaiseIfComingFromJenkins, {message}')

#测试用，手写环境变量
def Test_FillEnvironmentByManual(vars : dict):
    RaiseIfComingFromJenkins('Test_FillEnvironmentByManual')
    #default
    os.environ['___BUSY_MARK_TAG'] = '13579'
    #
    for key, value in vars.items():
        os.environ[key] = value

#测试用，从Jenkins build的console复制文本，转换成环境变量
def Test_FillTestEnvironmentByConsoleTextFile(path : str):
    RaiseIfComingFromJenkins('Test_FillTestEnvironmentByConsoleTextFile')
    #
    lines = UOS.LoadTextFile(path)
    if lines is None: return
    #
    patternEmpty = r'\s+$'
    patternAnnotate = r'\s*[(//)(##)]+'
    patternResult = r'\s*Env: (\S+) -> ([ \S]*)'
    for line in lines:
        if re.match(pattern=patternEmpty, string=line) is not None: continue
        if re.match(pattern=patternAnnotate, string=line) is not None: continue
        #
        mo = re.match(pattern=patternResult, string=line)
        if mo is None:
            raise RuntimeError(f'UJenkinsArgs->Test_FillTestEnvironmentByConsoleTextFile, reg-expressions match error at line {line}')
        key = mo.group(1)
        value = mo.group(2)
        os.environ[key] = value    
