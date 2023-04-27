from framework.utils import UJenkinsArgs
from framework.modules.MNode import *
from framework.modules.MProject import *
from product.config.CNodeProduct import *

def DoAction(configKey : str, args : dict):
    config = CNodeSelector().Do(configKey)
    if config is None:
        UTracking.RaiseException('CleanResidual->DoAction', 'node not existed, key: ' + configKey)
    tag = MProject.GetBusyMarkTag(args)
    if MProject.CleanBusyMarkResidual(config.projectRoot, tag):
        UTracking.LogInfo('CleanResidual->DoAction', f'clean residual busy mark, tag: {tag}, path: {config.projectRoot}')

def main():
    args = UJenkinsArgs.FromEnvironment()
    configKey = ''
    DoAction(configKey, args)

if __name__ == '__main__':
    main()