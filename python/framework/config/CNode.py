from ..basic.BDefines import *
from ..basic.BConstant import *
from .CProject import *

class CNode:
    name = ''
    jenkins = ''
    root = ''
    projectRoot = ''
    #projects is dict('key', CProject)
    #or
    #projects is dict('key1', dict('key2', CProject))
    projects = {}