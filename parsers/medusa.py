import os
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('medusa-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card"})
                for div in divs_name:
                    title = div.find('h3', {"class":"card-title"}).text
                    description = div.find("div", {"class": "card-body"}).text.strip()
                    appender(title, 'medusa', description)
                file.close()
        except:
            errlog('medusa: ' + 'parsing fail')
            pass