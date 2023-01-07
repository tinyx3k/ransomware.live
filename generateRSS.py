import json
from datetime import datetime
import uuid
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

# Chargez les données du fichier JSON
with open('posts.json') as f:
  data = json.load(f)

# Créez l'élément rss et ajoutez-y les attributs nécessaires
rss = Element('rss', {'version': '2.0', 'xmlns:atom': 'http://www.w3.org/2005/Atom'})

# Créez l'élément channel et ajoutez-y les éléments enfants nécessaires
channel = SubElement(rss, 'channel')
title = SubElement(channel, 'title')
title.text = 'Ransomware.live RSS Feed'
link = SubElement(channel, 'link')
link.text = 'https://www.ransomware.live/rss.xml'
description = SubElement(channel, 'description')
description.text = 'Last entry monitoring by Ransomware.live'

# Parcourez les données du fichier JSON et ajoutez un élément item pour chaque enregistrement
for i in reversed(range(len(data)-50, len(data))):
  item = data[i]
  rss_item = SubElement(channel, 'item')
  item_title = SubElement(rss_item, 'title')
  item_title.text = str(item['group_name']) + " publish a now posts : " + str(item['post_title'])
  item_link = SubElement(rss_item, 'link')
  item_link.text = 'https://www.ransomware.live/#/profiles/{}'.format(item['group_name'])
  #item_description = SubElement(rss_item, 'description')
  #item_description.text = 'Publication de {}'.format(item['group_name'])
  item_guid = SubElement(rss_item, 'guid')
  item_guid.text = 'https://www.ransomware.live/#/profiles/' + str(item['group_name']) + '?' +  str(uuid.uuid1(1234567890))
  
  date_iso = item['discovered']
  date_rfc822 = datetime.strptime(date_iso, '%Y-%m-%d %H:%M:%S.%f').strftime('%a, %d %b %Y %H:%M:%S +0000')
  
  item_pubdate = SubElement(rss_item, 'pubDate')
  item_pubdate.text = date_rfc822

# Convertissez l'objet rss en chaîne de caractères et enregistrez-le dans un fichier
rss_str = tostring(rss, encoding='unicode')
with open('./docs/rss.xml', 'w') as f:
  f.write(rss_str)
