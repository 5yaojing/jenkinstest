import json
import os

def ToJson(o):
    return json.dumps(o)#, ensure_ascii=False)

def FromJson(j):
    return json.loads(j)

def ToJsonFile(o, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(o, f)

def FromJsonFile(path):
    if not os.path.isfile(path): return None
    o = None    
    with open(path, 'r', encoding='utf-8') as f:
        o = json.load(f)
    return o