#Quick & Dirty script to update Clop description 
# Done by ChatGPT ;) 
 

import json
import requests
import random
import re
from bs4 import BeautifulSoup
# from sharedutils import randomagent

# load json data from file
with open('posts.json', 'r') as f:
    data = json.load(f)

# iterate over each item in the json data
for item in data:
    # check if the group_name matches a specific value
    if item['group_name'] == 'clop':
        # check if the 'description' field is empty or doesn't exist
        if 'description' not in item or not item['description']:
            website_url = item['post_title']
            # check if the post_title starts with "www"
            if not website_url.startswith("www"):
                website_url = "www." + website_url
            # check if the post_title starts with "http" or "https"
            if not website_url.startswith("http"):
                website_url = "https://" + website_url
            # retrieve the title of the website from its URL
            print('Trying to parse : '+ website_url)
            try:
                with open("asset/useragent.txt", "r") as f:
                    user_agents = f.readlines()
                # Strip newlines from the user agents
                user_agents = [ua.strip() for ua in user_agents]
                # Pick a random user agent
                headers = {'User-Agent': random.choice(user_agents)}
                # Make the request
                page = requests.get(website_url, headers=headers, timeout=10)
                page = requests.get(website_url,timeout=10)
                soup = BeautifulSoup(page.content, 'html.parser')
                website_title = soup.find('title').get_text()
                website_title = re.sub(r'[\r\n\t]', '', website_title).replace('|', '-')
                # add the title of the website as the description
                item['description'] = website_title
                print('parsing finish with description : '+ website_title)
            except requests.exceptions.Timeout:
                print('Website did not respond, timeout')
                item['description'] = ""
            except:
                print('Website did not respond')
                item['description'] = ""


# save the updated json data to file
with open('posts.json', 'w') as f:
    json.dump(data, f)
