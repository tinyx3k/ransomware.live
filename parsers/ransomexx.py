import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ransomexx-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card-body"})
                for div in divs_name:
                    title = div.find('h5').text.strip()
                    description = div.find_all('p', {"class", "card-text"})[1].text.strip()
                    appender(title, 'ransomexx', description)
                file.close()
        except:
            errlog('ransomexx: ' + 'parsing fail')
            pass
