import os
import shutil
from ..basic.BDefines import *
from . import UBase

############################################################################

def DirectoryOfPath(path : str):    
    p = path[0:-1] if path.endswith(('/', '\\')) else path
    return os.path.dirname(p)

def NameOfPath(path : str):
    p = path[0:-1] if path.endswith(('/', '\\')) else path
    return os.path.basename(p)  

#修改文件名（字符串处理）
def ChangeFileName(path : str, suffix : str):
    f,ext = os.path.splitext(path)
    return f + suffix + ext

#修改目录名（字符串处理）
def ChangeDirectoryName(path : str, suffix : str):
    d = path
    c = ''
    if path.endswith(('/', '\\')):
        d = path[0:-1]
        c = path[-1]
    return d + suffix + c

def IsSameExt(path : str, ext : str):
    _,de = os.path.splitext(path)
    return True if de.lower() == f'.{ext.lower()}' else False

############################################################################

def IsFileExist(path : str):
    if not os.path.exists(path): return False
    return os.path.isfile(path)

def IsDirectoryExist(path : str):
    if not os.path.exists(path): return False
    return os.path.isdir(path)

def CreateDirectory(path : str):
    result = True
    try:        
        os.makedirs(name=path, exist_ok=True)
    except Exception as e:
        print('UOS->CreateDirectory, exception: ' + str(e))
        result = False
                
    return result

def DeleteDirectory(path : str):
    if not IsDirectoryExist(path): return False
    result = True
    try:        
        shutil.rmtree(path)
    except Exception as e:
        print('UOS->DeleteDirectory, exception: ' + str(e))
        result = False
                
    return result

def IsParentDirectoryExist(path : str):
    parent = DirectoryOfPath(path)
    return IsDirectoryExist(parent)
    
def CreateParentDirectory(path : str):
    parent = DirectoryOfPath(path)
    result = True
    try:
        os.makedirs(name=parent, exist_ok=True)
    except Exception as e:
        print('UOS->CreateParentDirectory, exception: ' + str(e))
        result = False
                
    return result    

def CreateFileEmpty(path : str, withDirectory : bool = False):
    if IsFileExist(path): return False
    
    if withDirectory:
        parent = DirectoryOfPath(path)
        if not IsDirectoryExist(parent):
            CreateDirectory(parent)
            
    fd = os.open(path, os.O_CREAT)
    os.close( fd )
    return True

def DeleteFile(path : str):
    if not IsFileExist(path): return False

    result = True
    try:
        os.remove(path)
    except Exception as e:
        print('UOS->DeleteFile, exception: ' + str(e))
        result = False
                
    return result    

############################################################################

#拷贝srcFile到destFile
def CopyFile(srcFile : str, destFile : str, createIfDestParentDirectoryNotExisted = False):
    if not IsFileExist(srcFile): return False

    if not IsParentDirectoryExist(destFile): 
        if createIfDestParentDirectoryNotExisted:
            CreateParentDirectory(destFile)
        else:
            return False

    result = True
    try:
        shutil.copy2(srcFile, destFile)
    except Exception as e:
        print('UOS->CopyFile, exception: ' + str(e))
        result = False
                
    return result

#拷贝srcFile到destDirectory目录下
def CopyFile2D(srcFile : str, destDirectory : str, createIfDestNotExisted = False):
    if not IsFileExist(srcFile): return False

    if not IsDirectoryExist(destDirectory): 
        if createIfDestNotExisted:
            CreateDirectory(destDirectory)
        else:
            return False

    result = True
    try:
        shutil.copy2(srcFile, destDirectory)
    except Exception as e:
        print('UOS->CopyFile2D, exception: ' + str(e))
        result = False
                
    return result

#拷贝srcDirectory的子目录和文件，到destDirectory目录下
def CopyFiles(srcDirectory : str, destDirectory : str, createIfDestNotExisted = False):
    if not IsDirectoryExist(srcDirectory): return False

    if not IsDirectoryExist(destDirectory): 
        if createIfDestNotExisted:
            CreateDirectory(destDirectory)
        else:
            return False

    paths = os.listdir(srcDirectory)
    for path in paths:
        fp = os.path.join(srcDirectory, path)
        if os.path.isfile(fp):  
            shutil.copy2(fp, destDirectory)
        elif os.path.isdir(fp):
            fd = os.path.join(destDirectory, path)
            if not os.path.exists(fd):
                os.mkdir(path=fd)
            CopyFiles(fp, fd)
        else:
            continue

    return True

#拷贝srcDirectory到destDirectory下的newName目录下，如果newName为空，沿用srcDirectory的目录名
def CopyFiles2D(srcDirectory : str, destDirectory : str, createIfDestNotExisted = False, newName : str = None):
    if not IsDirectoryExist(srcDirectory): return False

    if not IsDirectoryExist(destDirectory): 
        if createIfDestNotExisted:
            CreateDirectory(destDirectory)
        else:
            return False
    
    dn = NameOfPath(srcDirectory) if UBase.IsStringNoneOrEmpty(newName) else newName
    path = os.path.join(destDirectory, dn)
    return CopyFiles(srcDirectory, path, True)    

#移动srcDirectory到destDirectory目录下
def MoveDirectory(srcDirectory : str, destDirectory : str, createIfDestNotExisted = False):
    if not IsDirectoryExist(srcDirectory): return False

    if not IsDirectoryExist(destDirectory): 
        if createIfDestNotExisted:
            CreateDirectory(destDirectory)
        else:
            return False
    
    result = True
    try:
        shutil.move(srcDirectory, destDirectory)
    except Exception as e:
        print('UOS->MoveDirectory, exception: ' + str(e))
        result = False
                
    return result

#重命名oldPath为newPath，arbitrary允许目录不存在，非常霸道
def RenameFile(oldPath : str, newPath : str, arbitrary : bool = False):
    if not IsFileExist(oldPath): return False

    result = True
    try:
        if arbitrary:
            os.renames(oldPath, newPath)
        else:
            os.rename(oldPath, newPath)
    except Exception as e:
        print('UOS->RenameFile, exception: ' + str(e))
        result = False
                
    return result

#重命名oldPath为newPath，arbitrary允许目录不存在，非常霸道
def RenameDirectory(oldPath : str, newPath : str, arbitrary : bool = False):
    if not IsDirectoryExist(oldPath): return False

    result = True
    try:
        if arbitrary:
            os.renames(oldPath, newPath)
        else:
            os.rename(oldPath, newPath)
    except Exception as e:
        print('UOS->RenameDirectory, exception: ' + str(e))
        result = False

    return result

############################################################################

def LoadTextFile(path : str) -> list:
    if not IsFileExist(path): return None

    f = open(path, mode='rt', encoding='utf-8')
    lines = f.readlines()
    f.close()    
    return lines
    
def SaveTextFile(path : str, lines : list, withNewlineCharacter : bool = False) -> bool:
    if lines is None: return False
    
    f = open(path, mode='wt+', encoding='utf-8')
    if withNewlineCharacter:
        f.writelines(lines)
    else:
        for line in lines:
            f.write(f'{line}\n')
    f.close()
    return True

def LoadStringFile(path : str) -> str:
    if not IsFileExist(path): return ''

    f = open(path, mode='r', encoding='utf-8')
    s = f.read()
    f.close()
    return s
    
def SaveStringFile(path : str, s : str) -> bool:   
    f = open(path, mode='w+', encoding='utf-8')
    f.write(s)
    f.close()
    return True

def LoadByteFile(path : str) -> bytes:
    if not IsFileExist(path): return ''

    f = open(path, mode='rb')
    b = f.read()
    f.close()
    return b
    
def SaveByteFile(path : str, b : bytes) -> bool:   
    f = open(path, mode='wb+')
    f.write(b)
    f.close()
    return True

############################################################################