#!/usr/bin/env python3
import asyncio
import websockets
import re, ssl, json, base64, shutil, random, string
from sjcl import SJCL
import sys, getopt

def main(argv):
    url = ''
    try:
        opts, args = getopt.getopt(argv,"hu:",["url="])
    except getopt.GetoptError:
        print('python-lufi.py -u <url>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('python-lufi.py -u <url>')
            sys.exit()
        elif opt in ("-u", "--url"):
            url = arg
            key = url.split('#')[1]
            wsurl = re.sub(r'\/r\/','/download/',re.sub(r'^http','ws',url.split('#')[0]))
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.load_default_certs()
            asyncio.get_event_loop().run_until_complete(getFile(wsurl,key,ssl_context))

async def getFile(wsurl,key,ssl=False):
    part = 0
    finished = False
    randomFile = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(16))+".tmp"
    with open(randomFile,"wb") as f:
        async with websockets.connect(wsurl,ssl=ssl,max_size=5000000) as ws:
            while finished is False:
                req = await ws.send('{"part":'+str(part)+'}')

                result = await ws.recv()
                partInfo,partContent = result.split('XXMOJOXX')
                pc = json.loads(partContent[1:-1].replace('\\',''))
                partInfo = json.loads(partInfo)
                print("Downloaded part "+ str(part+1)+"/"+str(partInfo['total']))
                fileContent = SJCL().decrypt(pc, key)
                f.write(base64.b64decode(fileContent))
                if part == partInfo['total']-1:
                    finished = True
                    print("Download finished")
                    shutil.move(randomFile,partInfo['name'])
                else:
                    part += 1

if __name__ == "__main__":
   main(sys.argv[1:])
