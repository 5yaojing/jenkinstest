################ string ###########################################################################
def IsStringNoneOrEmpty(s : str):
    if s is None : return True
    if s == '' : return True
    return False

def SplitString(s : str, sep : str):
    if IsStringNoneOrEmpty(s) : return []
    ss = s.split(sep)
    sss = []
    for x in ss:
        if x == '': continue
        sss.append(x)
    return sss

def ReplaceString(s : str, old : str, new : str):
    if IsStringNoneOrEmpty(s) : return s
    return s.replace(old, new)

def ReplaceStrings(s : str, olds : list, new : str):
    if IsStringNoneOrEmpty(s) : return s
    r = s
    for old in olds:
        r = r.replace(old, new)
    return r
   
################ container ###########################################################################
def IsContainerNoneOrEmpty(c : object):
    if c is None : return True
    if len(c) <= 0 : return True
    return False
################ ip ###########################################################################
def IsIPv4(v : str):
    ss = v.split(":")
    ssL = len(ss)
    if ssL != 1 and ssL != 2: return False

    ss0 = ss[0].split(".")
    if len(ss0) != 4: return False
    if ss0[0].isdigit():
        si = int(ss0[0])
        if (ss0[0] != f'{si}'): return False
        if si < 0 or si > 255: return False
    if ss0[1].isdigit():
        si = int(ss0[1])
        if (ss0[1] != f'{si}'): return False
        if si < 0 or si > 255: return False
    if ss0[2].isdigit():
        si = int(ss0[2])
        if (ss0[2] != f'{si}'): return False
        if si < 0 or si > 255: return False
    if ss0[3].isdigit():
        si = int(ss0[3])
        if (ss0[3] != f'{si}'): return False
        if si < 0 or si > 255: return False
    
    if ssL == 2:
        if ss[1].isdigit():
            si = int(ss[1])
            if (ss[1] != f'{si}'): return False
            if si < 0 or si > 65535: return False
    
    return True
################ int ###########################################################################
#[min, max]
def IsIntRange(v : str, min : int, max : int):
    if IsStringNoneOrEmpty(v): return False
    if not v.isdigit(): return False

    i = int(v)
    if (v != f'{i}'): return False
    return (i >= min) and (i <= max)

################ other ###########################################################################