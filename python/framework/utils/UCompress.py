import os
import zipfile
import lz4.block
from . import UOS
##################################################################################################
def ZipDirectory(only_stored : bool, directory : str, zipPath : str, includeTop : bool, createIfZipParentDirectoryNotExisted = False) -> bool:
    if not os.path.exists(directory): return False
    if not os.path.isdir(directory): return False
    if not UOS.IsParentDirectoryExist(zipPath):
        if createIfZipParentDirectoryNotExisted:
            UOS.CreateParentDirectory(zipPath)
        else:
            return False
    compression = zipfile.ZIP_STORED if only_stored else zipfile.ZIP_DEFLATED
    zf = zipfile.ZipFile(zipPath, 'w', compression=compression, compresslevel=9)

    top = ''

    if includeTop:
        top = UOS.NameOfPath(directory)
        zf.write(filename=directory, arcname=top)

    for dir, dns, fns in os.walk(directory):
        for fn in fns:
            fp = os.path.join(dir, fn)
            ar = os.path.relpath(fp, directory)
            if top != '':
                ar = os.path.join(top, ar)
            zf.write(fp, ar)

    zf.close()

    return True

def ZipFiles(only_stored : bool, directory : str, fileNames : list, zipPath : str, includeTop : bool, createIfZipParentDirectoryNotExisted = False) -> bool:
    if not os.path.exists(directory): return False
    if not os.path.isdir(directory): return False
    if not UOS.IsParentDirectoryExist(zipPath):
        if createIfZipParentDirectoryNotExisted:
            UOS.CreateParentDirectory(zipPath)
        else:
            return False
    compression = zipfile.ZIP_STORED if only_stored else zipfile.ZIP_DEFLATED
    zf = zipfile.ZipFile(zipPath, 'w', compression=compression, compresslevel=9)

    top = ''

    if includeTop:
        top = UOS.NameOfPath(directory)
        zf.write(filename=directory, arcname=top)

    for fn in fileNames:
        fp = os.path.join(directory, fn)
        ar = fn if top == '' else os.path.join(top, fn)
        zf.write(fp, ar)

    zf.close()

    return True
##################################################################################################
def LZ4Decompress(bs : bytes, max_length : int) -> bytes:
    dest = lz4.block.decompress(bs, uncompressed_size=max_length)
    return dest