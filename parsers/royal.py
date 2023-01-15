import os
from bs4 import BeautifulSoup
import json
import html
import re
from sharedutils import errlog
from parse import appender 

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('royal-royal4'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                soup=BeautifulSoup(file,'html.parser')
                jsonpart = soup.pre.contents
                data = json.loads(jsonpart[0])
                for entry in data['data']:
                    title = html.unescape(entry['title'])
                    website = str(entry['url'])
                    description = html.unescape((re.sub(r'<[^>]*>', '',entry['text'])))
                    appender(title, 'royal', description,website)
                file.close()
        except:
            errlog('royal: ' + 'parsing fail')
            pass    