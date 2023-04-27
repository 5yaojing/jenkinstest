import httpx
import asyncio


def Get(url : str, params : dict) -> bool:
    print(url)

def Post(url : str, content : str, form : dict) -> bool:
    print(url)

def PostFile(url : str, file : str) -> bool:
    f = open(file, 'rb')
    fs = {'file': f}
    response = httpx.post(url, files=fs)
    print(response.text)
    f.close()
    
def PostFiles(url : str, files : list) -> bool:
    fs = {}
    for file in files:
        f = open(file, 'rb')
        fs[''] = f
    response = httpx.post(url, files=fs)
    print(response.text)
    for f in fs:
        f.close() 