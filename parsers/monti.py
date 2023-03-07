
"""
+------------------------------+------------------+----------+
| Description | Published Date | Victim's Website | Post URL |
+------------------------------+------------------+----------+
|      X      |        X       |                  |          |
+------------------------------+------------------+----------+
Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
"""

import os,datetime
from bs4 import BeautifulSoup
from sharedutils import errlog
from parse import appender 

def main():
    for filename in os.listdir('source'):
        try:
            if filename.startswith('monti-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('a', {"class": "leak-card p-3"})
                for div in divs_name:
                    title = div.find('h5').text.strip()
                    description =  div.find('p').text.strip()
                    published = div.find('div', {'class': 'col-auto published'}).text.strip()
                    date_obj =  datetime.datetime.strptime(published, '%Y-%m-%d %H:%M:%S')
                    published = date_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
                    appender(title, 'monti', description,"",published )
        except:
            errlog('monti: ' + 'parsing fail')
            pass 
                