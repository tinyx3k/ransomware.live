from bs4 import BeautifulSoup
import os,re

#for filename in os.listdir('source'):
#        #try:
#            if filename.startswith('unsafe-'):
#                html_doc='source/'+filename
#                file=open(html_doc,'r')
#                soup=BeautifulSoup(file,'html.parser')
#                titles_h4 = soup.find_all("h4")
#                for title_h4 in titles_h4:
#                    print(title_h4.text)
#                    title_h6 = title_h4.find_next("h6", class_="fas fa-link")
#                    print('--' + str(type(title_h6)))
#                    print(str(title_h6.txt))
#        #except:
#        #    pass

for filename in os.listdir('source'):
        #try:
            if filename.startswith('unsafe-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "info"})
                for div in divs_name:
                    title = div.find('h4')
                    print(title.text.strip())
                    titre_h6 = div.find_all("h6")
                    website = ''
                    country = ''
                    revenue = ''
                    for info in titre_h6:
                        print('+' + str(info.text))
                        if "website" in str(info.text):
                            website = info.text.replace('website: ','https://') 
                        if "country" in str(info.text): 
                            country = info.text
                        if "revenue" in str(info.text): 
                            revenue = info.text
                    print(website)
                    print(country + ' -' + revenue)
                    


