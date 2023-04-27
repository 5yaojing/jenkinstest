import base64

def ObjectToBase64(v : object):
    s = str(v, 'utf-8')
    return StringToBase64(s)

def StringToBase64(v : str):
    b64 = base64.b64encode(v.encode('utf-8'))
    return str(b64, 'utf-8')

def Base64ToString(v : str):
    bs = base64.b64decode(v)
    return str(bs, 'utf-8')