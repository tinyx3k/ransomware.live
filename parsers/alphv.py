import os
from bs4 import BeautifulSoup
import json
from sharedutils import stdlog, errlog
import parse

def main():
    for filename in os.listdir('source'):
        try:
           if filename.startswith('alphv-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                if 'alphvmmm' in filename:
                        stdlog('alphv : Parse ' +  'json file')
                        jsonpart= soup.pre.contents
                        data = json.loads(jsonpart[0])
                        for entry in data['items']:
                            title = entry['title'].strip()
                            description =''
                            website =''
                            if 'publication' in entry and entry['publication'] is not None:
                                # Si oui, accédez au champ "description"
                                description = entry['publication']['description'].strip()
                                # description = entry['publication']['description'].strip()
                                website = entry['publication']['url'].strip()
                            parse.appender(title, 'alphv',description.replace('\n',' '),website)
                else: 
                    stdlog('alphv : Parse ' +  'html file')
                    divs_name=soup.find_all('div', {'class': 'post-body'})
                    for div in divs_name:
                        title = div.find('div', {'class': 'post-header'}).text.strip()
                        description = div.find('div', {'class': 'post-description'}).text.strip()
                        parse.appender(title, 'alphv',description.replace('\n',' '))
                file.close()
        except:
            errlog('alphv: ' + 'parsing fail')
            pass