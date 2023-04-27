######### Log ########################################################################
def LogInfo(tag : str, message : str):
    print(f'Info! {tag}, {message}')

def LogWarning(tag : str, message : str):
    print(f'Warning! {tag}, {message}')

def LogError(tag : str, message : str):
    print(f'Error! {tag}, {message}')
######### Raise ########################################################################

def RaiseException(tag : str, message : str):
    #LogError(tag, message)
    raise RuntimeError(f'Exception! {tag}, {message}')

######### Log ########################################################################
def __BeautifyLog(o : object, level : int = 0) -> str:
    if o is None: return 'Object is None'
    #
    ConstSpace = '     '
    # 
    r = ''
    t = type(o)
    # 
    if t == list:
        if len(o) > 0:
            index = 0
            rs = ''
            space = ConstSpace
            for i in range(level):
                space += ConstSpace
                rs += ConstSpace                
            r = f'\n{rs}[\n'

            for v in o:
                r += f'{space}{index} : {__BeautifyLog(v, level + 1)}\n'
                index += 1
            
            r += f'{rs}]'
        else:
            r = 'List is empty'
    
    elif t == dict:
        if len(o) > 0:
            rs = ''
            space = ConstSpace
            for i in range(level):
                space += ConstSpace
                rs += ConstSpace                
            r = f'\n{rs}{{\n'

            for k,v in o.items():
                r += f'{space}{k} -> {__BeautifyLog(v, level + 1)}\n'

            r += f'{rs}}}'
        else:
            r = 'Dict is empty'
    
    elif t == tuple:
        if len(o) > 0:
            index = 0
            rs = ''
            space = ConstSpace
            for i in range(level):
                space += ConstSpace
                rs += ConstSpace                
            r = f'\n{rs}(\n'

            for v in o:
                r += f'{space}{index} > {__BeautifyLog(v, level + 1)}\n'
                index += 1
            
            r += f'{rs})'
        else:
            r = 'Tuple is empty'

    else:
        r = f'{o}'
    # 
    return r

def BeautifyLog(o : object) -> str:
    return __BeautifyLog(o)