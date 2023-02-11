import requests
import json
from datetime import datetime as dt
from sharedutils import stdlog, errlog

def writefile(file, line):
    with open(file, 'a', encoding='utf-8') as f:
        f.write(line)
        f.close()

url = "https://api.ransomwhe.re/export"

NowTime=dt.now() 

# Fetch the JSON data from the URL
response = requests.get(url)
response.raise_for_status()
result = response.json()

# Load the other JSON file
with open("groups.json") as json_file:
    groups = json.load(json_file)

for group in groups:
    write = False
    lines=''
    stdlog(group["name"] + ' : analyze crypto')
    # Sort the result list by family
    result["result"].sort(key=lambda x: x.get("family", ""))

    # Iterate through the sorted result list
    for address_info in result["result"]:
        family = address_info.get("family", "").split(" ", 1)[0].lower()
        # print(family)
        if family == group["name"]:
            write = True
            lines += "| " + address_info['address'] + " | " + address_info['blockchain'] + " | $ " + str(round(float(address_info['balanceUSD']))) + " | \n"

    if write == True:
        stdlog(group["name"] + ' : found crypto address')
        cryptofile='docs/crypto/'+ group["name"] +'.md'
        with open(cryptofile, 'w', encoding='utf-8') as f:
            f.close()
        writefile(cryptofile,'# ' + group["name"] + ' : Crypto wallet(s)\n')
        writefile(cryptofile,'\n')
        writefile(cryptofile,'| address | blockchain | Balance |\n')
        writefile(cryptofile,lines)
        writefile(cryptofile, '\n')
        writefile(cryptofile, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_ \n')
        writefile(cryptofile, '\n')
    else:
        stdlog(group["name"] + ' : no crypto address found')
        
        
