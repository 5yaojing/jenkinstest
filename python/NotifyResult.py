from framework.utils import UBase
from framework.utils import UJenkinsArgs
from product.config.CDingDingProduct import *
from product.config.CNFSProduct import *

from framework.modules.MDingDing import *
from framework.modules.MNFS import *

def MakeFeatureTxt(code : int, feature : str, args : dict) -> str:
    if UBase.IsStringNoneOrEmpty(feature): return ''

    jobName = args['name']
    buildNumber = args['build_number']

    txt = ''
    
    if feature == 'NFS_Archive':
        if code == 0:
            nfs = MNFS(CNFSProduct())
            downloadPath = nfs.MakeDownloadPath(CNFSResourceEnum.Archive.value, jobName=jobName, buildNumber=buildNumber)
            if not UBase.IsStringNoneOrEmpty(downloadPath):
                txt = f'Archive: {downloadPath}'

    return txt

def DoAction(code : int, group : str, branch : str, feature : str, message : str, args : dict):
    user = args['user']
    name = args['name']
    link = args['link']

    txt = f'User: {user}\n'
    txt += f'Name: {name}\n'

    if not UBase.IsStringNoneOrEmpty(branch):
        txt += f'Branch: {branch}\n'

    txt += f'Message: {message}\n'
    featureTxt = MakeFeatureTxt(code, feature, args)
    if UBase.IsStringNoneOrEmpty(featureTxt):
        txt += f'Link: {link}'
    else:
        txt += f'Link: {link}\n'
        txt += featureTxt
    
    dingding = MDingDing(CDingDingProduct())
    dingding.SendMessage(group=group, message=txt)

import click
@click.command()
@click.option('-c', '--code', type=click.INT, default=0, help='code')
@click.option('-g', '--group', type=click.STRING, default='All', help='group')
@click.option('-b', '--branch', type=click.STRING, default='', help='branch')
@click.option('-f', '--feature', type=click.STRING, default='', help='feature')
@click.option('-m', '--message', type=click.STRING, default='Message', help='message')
def main(**invoke_args):
    code = invoke_args['code']
    group = invoke_args['group']
    branch = invoke_args['branch']
    feature = invoke_args['feature']    
    message = invoke_args['message']    
    
    args = UJenkinsArgs.FromEnvironment([
        ('BUILD_USER'   , 'user'            , str   , '' ),
        ('JOB_NAME'     , 'name'            , str   , '' ),          
        ('BUILD_URL'    , 'link'            , str   , '' ),
        ('BUILD_NUMBER' , 'build_number'    , int   , 0  )
    ])    
    DoAction(code, group, branch, feature, message, args)

if __name__ == '__main__':
    main()