#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
parses the source html for each group where a parser exists & contributed to the post dictionary
always remember..... https://stackoverflow.com/questions/1732348/regex-match-open-tags-except-xhtml-self-contained-tags/1732454#1732454
'''
import os
import json,re, html, time
from sys import platform
from datetime import datetime
from bs4 import BeautifulSoup # type: ignore
from sharedutils import openjson
from sharedutils import runshellcmd
# from sharedutils import todiscord, totwitter, toteams
from sharedutils import stdlog, dbglog, errlog   # , honk
# For screenshot 
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
# For watermark on screenshot 
from PIL import Image
from PIL import ImageDraw
# For Notification 
import http.client, urllib


# on macOS we use 'grep -oE' over 'grep -oP'
if platform == 'darwin':
    fancygrep = 'ggrep -oP'
else:
    fancygrep = 'grep -oP'


def posttemplate(victim, group_name, timestamp,description,website):
    '''
    assuming we have a new post - form the template we will use for the new entry in posts.json
    '''
    schema = {
        'post_title': victim,
        'group_name': group_name,
        'discovered': timestamp,
        'description': description,
        'website': website
    }
    dbglog(schema)
    return schema

def screenshot(webpage,fqdn,delay=1500):
    stdlog('webshot: {}'.format(webpage))
    name = 'docs/screenshots/' + fqdn.replace('.', '-') + '.png'
    try:
        if os.path.getmtime(name) < (time.time() - 2700):
            with sync_playwright() as play:
                try:
                    browser = play.chromium.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                        args=[''])
                    context = browser.new_context(ignore_https_errors= True )
                    Image.MAX_IMAGE_PIXELS = None
                    page = context.new_page()
                    page.goto(webpage, wait_until='load', timeout = 120000)
                    page.bring_to_front()
                    page.wait_for_timeout(delay)
                    page.mouse.move(x=500, y=400)
                    page.wait_for_load_state('networkidle')
                    page.mouse.wheel(delta_y=2000, delta_x=0)
                    page.wait_for_load_state('networkidle')
                    page.wait_for_timeout(5000)
                    page.screenshot(path=name, full_page=True)
                    image = Image.open(name)
                    draw = ImageDraw.Draw(image)
                    draw.text((10, 10), "https://www.ransomware.live", fill=(0, 0, 0))
                    image.save(name)
                except PlaywrightTimeoutError:
                    stdlog('Timeout!')
                except Exception as exception:
                    errlog(exception)
                    errlog("error")
                browser.close()
        else: 
            stdlog('webshot already done : {}'.format(webpage))
    except:
             stdlog('webshot file not found : {}'.format(webpage))


def existingpost(post_title, group_name):
    '''
    check if a post already exists in posts.json
    '''
    posts = openjson('posts.json')
    # posts = openjson('posts.json')
    for post in posts:
        if post['post_title'] == post_title and post['group_name'] == group_name:
            #dbglog('post already exists: ' + post_title)
            return True
    dbglog('post does not exist: ' + post_title)
    return False

def appender(post_title, group_name, description="", website=""):
    '''
    append a new post to posts.json
    '''
    if len(post_title) == 0:
        errlog('post_title is empty')
        return
    # limit length of post_title to 90 chars
    if len(post_title) > 90:
        post_title = post_title[:90]
    post_title=html.unescape(post_title)
    if existingpost(post_title, group_name) is False:
        posts = openjson('posts.json')
        newpost = posttemplate(post_title, group_name, str(datetime.today()),description,website)
        stdlog('adding new post - ' + 'group:' + group_name + ' title:' + post_title)
        posts.append(newpost)
        with open('posts.json', 'w', encoding='utf-8') as outfile:
            '''
            use ensure_ascii to mandate utf-8 in the case the post contains cyrillic 🇷🇺
            https://pynative.com/python-json-encode-unicode-and-non-ascii-characters-as-is/
            '''
            dbglog('writing changes to posts.json')
            json.dump(posts, outfile, indent=4, ensure_ascii=False)
        # if socials are set try post
        #if os.environ.get('DISCORD_WEBHOOK_1') is not None:
        #    todiscord(newpost['post_title'], newpost['group_name'], os.environ.get('DISCORD_WEBHOOK_1'))
        #if os.environ.get('DISCORD_WEBHOOK_2') is not None:
        #    todiscord(newpost['post_title'], newpost['group_name'], os.environ.get('DISCORD_WEBHOOK_2'))
        #if os.environ.get('TWITTER_ACCESS_TOKEN') is not None:
        #    totwitter(newpost['post_title'], newpost['group_name'])
        #if os.environ.get('MS_TEAMS_WEBHOOK') is not None:
        #    toteams(newpost['post_title'], newpost['group_name'])
        try: 
            stdlog('Send notification')
            API_KEY = os.getenv('PUSH_API')
            USER_KEY = os.getenv('PUSH_USER')
            if len(API_KEY) < 5:
                errlog('NO API KEY FOUND')
            if len(USER_KEY) < 5:
                errlog('NO USER KEY FOUND')
            MESSAGE = "<b>" + post_title +  "</b> est victime du ransomware <b>" + group_name + "</b>"
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
              "token": API_KEY,
              "user": USER_KEY,
              "message": MESSAGE
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()
        except: 
            errlog('impossible to push notification')
        groups = openjson('groups.json')
        for group in groups:
            if group["name"] == group_name:
                for webpage in group['locations']:
                    delay = webpage['delay']*1000 if ( 'delay' in webpage and webpage['delay'] is not None ) \
                        else 15000
                    screenshot('http://'+webpage['fqdn'],webpage['fqdn'],delay)


'''
all parsers here are shell - mix of grep/sed/awk & perl - runshellcmd is a wrapper for subprocess.run
'''

def synack():
    stdlog('parser: ' + 'synack')
    parser='''
    grep 'card-title' source/synack-*.html --no-filename | cut -d ">" -f2 | cut -d "<" -f1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('synack: ' + 'parsing fail')
    for post in posts:
        appender(post, 'synack')

def everest():
    stdlog('parser: ' + 'everest')
    parser = '''
    grep '<h2 class="entry-title' source/everest-*.html | cut -d '>' -f3 | cut -d '<' -f1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('everest: ' + 'parsing fail')
    for post in posts:
        appender(post, 'everest')


def suncrypt():
    stdlog('parser: ' + 'suncrypt')
    parser = '''
    cat source/suncrypt-*.html | tr '>' '\n' | grep -A1 '<a href="client?id=' | sed -e '/^--/d' -e '/^<a/d' | cut -d '<' -f1 | sed -e 's/[ \t]*$//' "$@" -e '/Read more/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('suncrypt: ' + 'parsing fail')
    for post in posts:
        appender(post, 'suncrypt')

def lorenz():
    stdlog('parser: ' + 'lorenz')
    parser = '''
    grep 'h3' source/lorenz-*.html --no-filename | cut -d ">" -f2 | cut -d "<" -f1 | sed -e 's/^ *//g' -e '/^$/d' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('lorenz: ' + 'parsing fail')
    for post in posts:
        appender(post, 'lorenz')

def lockbit2():
    stdlog('parser: ' + 'lockbit2')
    # egrep -h -A1 'class="post-title"' source/lockbit2-* | grep -v 'class="post-title"' | grep -v '\--' | cut -d'<' -f1 | tr -d ' '
    parser = '''
    awk -v lines=2 '/post-title-block/ {for(i=lines;i;--i)getline; print $0 }' source/lockbit2-*.html | cut -d '<' -f1 | sed -e 's/^ *//g' -e 's/[[:space:]]*$//' | sort | uniq
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('lockbit2: ' + 'parsing fail')
    for post in posts:
        appender(post, 'lockbit2')


def arvinclub():
    stdlog('parser: ' + 'arvinclub')
    # grep 'bookmark' source/arvinclub-*.html --no-filename | cut -d ">" -f3 | cut -d "<" -f1
    parser = '''
    grep 'rel="bookmark">' source/arvinclub-*.html -C 1 | grep '</a>' | sed 's/^[^[:alnum:]]*//' | cut -d '<' -f 1 | sed -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('arvinclub: ' + 'parsing fail')
    for post in posts:
        appender(post, 'arvinclub')

def avaddon():
    stdlog('parser: ' + 'avaddon')
    parser = '''
    grep 'h6' source/avaddon-*.html --no-filename | cut -d ">" -f3 | sed -e s/'<\/a'//
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('avaddon: ' + 'parsing fail')
    for post in posts:
        appender(post, 'avaddon')

def xinglocker():
    stdlog('parser: ' + 'xinglocker')
    parser = '''
    grep "h3" -A1 source/xinglocker-*.html --no-filename | grep -v h3 | awk -v n=4 'NR%n==1' | sed -e 's/^[ \t]*//' -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('xinglocker: ' + 'parsing fail')
    for post in posts:
        appender(post, 'xinglocker')
    
def ragnarlocker():
    stdlog('parser: ' + 'ragnarlocker')
    json_parser = '''
    grep 'var post_links' source/ragnarlocker-*.html --no-filename | sed -e s/"        var post_links = "// -e "s/ ;//"
    '''
    posts = runshellcmd(json_parser)
    post_json = json.loads(posts[0])
    with open('source/ragnarlocker.json', 'w', encoding='utf-8') as f:
        json.dump(post_json, f, indent=4)
        f.close()
    if len(post_json) == 1:
        errlog('ragnarlocker: ' + 'parsing fail')
    for post in post_json:
        try:
            appender(post['title'], 'ragnarlocker')
        except TypeError:
            errlog('ragnarlocker: ' + 'parsing fail')

def revil():
    stdlog('parser: ' + 'revil')
    # grep 'href="/posts' source/revil-*.html --no-filename | cut -d '>' -f2 | sed -e s/'<\/a'// -e 's/^[ \t]*//'
    parser = '''
    grep 'justify-content-between' source/revil-*.html --no-filename | cut -d '>' -f 3 | cut -d '<' -f 1 | sed -e 's/^ *//g' -e 's/[[:space:]]*$//' -e '/ediban/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('revil: ' + 'parsing fail')
    for post in posts:
        appender(post, 'revil')

def conti():
    stdlog('parser: ' + 'conti')
    # grep 'class="title">&' source/conti-*.html --no-filename | cut -d ";" -f2 | sed -e s/"&rdquo"//
    parser = '''
    grep 'newsList' source/conti-continewsnv5ot*.html --no-filename | sed -e 's/        newsList(//g' -e 's/);//g' | jq '.[].title' -r  || true
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('conti: ' + 'parsing fail')
    for post in posts:
        appender(post, 'conti')
    
def pysa():
    stdlog('parser: ' + 'pysa')
    parser = '''
    grep 'icon-chevron-right' source/pysa-*.html --no-filename | cut -d '>' -f3 | sed 's/^ *//g'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('pysa: ' + 'parsing fail')
    for post in posts:
        appender(post, 'pysa')

def nefilim():
    stdlog('parser: ' + 'nefilim')
    parser = '''
    grep 'h2' source/nefilim-*.html --no-filename | cut -d '>' -f3 | sed -e s/'<\/a'//
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('nefilim: ' + 'parsing fail')
    for post in posts:
        appender(post, 'nefilim') 

def mountlocker():
    stdlog('parser: ' + 'mountlocker')
    parser = '''
    grep '<h3><a href=' source/mount-locker-*.html --no-filename | cut -d '>' -f5 | sed -e s/'<\/a'// -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('mountlocker: ' + 'parsing fail')
    for post in posts:
        appender(post, 'mountlocker')

def babuk():
    stdlog('parser: ' + 'babuk')
    parser = '''
    grep '<h5>' source/babuk-*.html --no-filename | sed 's/^ *//g' | cut -d '>' -f2 | cut -d '<' -f1 | grep -wv 'Hospitals\|Non-Profit\|Schools\|Small Business' | sed '/^[[:space:]]*$/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('babuk: ' + 'parsing fail')
    for post in posts:
        appender(post, 'babuk')
    
def ransomexx():
    stdlog('parser: ' + 'ransomexx')
    parser = '''
    grep 'card-title' source/ransomexx-*.html --no-filename | cut -d '>' -f2 | sed -e s/'<\/h5'// -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('ransomexx: ' + 'parsing fail')
    for post in posts:
        appender(post, 'ransomexx')

#def cuba():
#    stdlog('parser: ' + 'cuba')
#    # grep '<p>' source/cuba-*.html --no-filename | cut -d '>' -f3 | cut -d '<' -f1
#    # grep '<a href="http://' source/cuba-cuba4i* | cut -d '/' -f 4 | sort -u
#    parser = '''
#    grep --no-filename '<a href="/company/' source/cuba-*.html | cut -d '/' -f 3 | cut -d '"' -f 1 | sort --uniq | grep -v company
#    '''
#    posts = runshellcmd(parser)
#    if len(posts) == 1:
#        errlog('cuba: ' + 'parsing fail')
#    for post in posts:
#        appender(post, 'cuba')

def pay2key():
    stdlog('parser: ' + 'pay2key')
    parser = '''
    grep 'h3><a href' source/pay2key-*.html --no-filename | cut -d '>' -f3 | sed -e s/'<\/a'//
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('pay2key: ' + 'parsing fail')
    for post in posts:
        appender(post, 'pay2key')

def azroteam():
    stdlog('parser: ' + 'azroteam')
    parser = '''
    grep "h3" -A1 source/aztroteam-*.html --no-filename | grep -v h3 | awk -v n=4 'NR%n==1' | sed -e 's/^[ \t]*//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('azroteam: ' + 'parsing fail')
    for post in posts:
        appender(post, 'azroteam')

def lockdata():
    stdlog('parser: ' + 'lockdata')
    parser = '''
    grep '<a href="/view.php?' source/lockdata-*.html --no-filename | cut -d '>' -f2 | cut -d '<' -f1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('lockdata: ' + 'parsing fail')
    for post in posts:
        appender(post, 'lockdata')
    
def blacktor():
    stdlog('parser: ' + 'blacktor')
    # sed -n '/tr/{n;p;}' source/bl@cktor-*.html | grep 'td' | cut -d '>' -f2 | cut -d '<' -f1
    parser = '''
    grep '>Details</a></td>' source/blacktor-*.html --no-filename | cut -f2 -d '"' | cut -f 2- -d- | cut -f 1 -d .
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('blacktor: ' + 'parsing fail')
    for post in posts:
        appender(post, 'blacktor')
    
def darkleakmarket():
    stdlog('parser: ' + 'darkleakmarket')
    parser = '''
    grep 'page.php' source/darkleakmarket-*.html --no-filename | sed -e 's/^[ \t]*//' | cut -d '>' -f3 | sed '/^</d' | cut -d '<' -f1 | sed -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('darkleakmarket: ' + 'parsing fail')
    for post in posts:
        appender(post, 'darkleakmarket')

def blackmatter():
    stdlog('parser: ' + 'blackmatter')
    parser = '''
    grep '<h4 class="post-announce-name" title="' source/blackmatter-*.html --no-filename | cut -d '"' -f4 | sort -u
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('blackmatter: ' + 'parsing fail')
    for post in posts:
        appender(post, 'blackmatter')

def payloadbin():
    stdlog('parser: ' + 'payloadbin')
    parser = '''
    grep '<h4 class="h4' source/payloadbin-*.html --no-filename | cut -d '>' -f3 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('payloadbin: ' + 'parsing fail')
    for post in posts:
        appender(post, 'payloadbin')

def groove():
    stdlog('parser: ' + 'groove')
    parser = '''
    egrep -o 'class="title">([[:alnum:]]| |\.)+</a>' source/groove-*.html | cut -d '>' -f2 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('groove: ' + 'parsing fail')
    for post in posts:
        appender(post, 'groove')

def bonacigroup():
    stdlog('parser: ' + 'bonacigroup')
    parser = '''
    grep 'h5' source/bonacigroup-*.html --no-filename | cut -d '>' -f 3 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('bonacigroup: ' + 'parsing fail')
    for post in posts:
        appender(post, 'bonacigroup')

def karma():
    stdlog('parser: ' + 'karma')
    parser = '''
    grep "h2" source/karma-*.html --no-filename | cut -d '>' -f 3 | cut -d '<' -f 1 | sed '/^$/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('karma: ' + 'parsing fail')
    for post in posts:
        appender(post, 'karma')


def spook():
    stdlog('parser: ' + 'spook')
    parser = '''
    grep 'h2 class' source/spook-*.html --no-filename | cut -d '>' -f 3 | cut -d '<' -f 1 | sed -e 's/^ *//g' -e '/^$/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('spook: ' + 'parsing fail')
    for post in posts:
        appender(post, 'spook')

def quantum():
    stdlog('parser: ' + 'quantum')
    parser = '''
    awk '/h2/{getline; print}' source/quantum-*.html | sed -e 's/^ *//g' -e '/<\/a>/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('quantum: ' + 'parsing fail')
    for post in posts:
        appender(post, 'quantum')

def atomsilo():
    stdlog('parser: ' + 'atomsilo')
    parser = '''
    grep "h4" source/atomsilo-*.html | cut -d '>' -f 3 | cut -d '<' -f 1 | sed -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('atomsilo: ' + 'parsing fail')
    for post in posts:
        appender(post, 'atomsilo')
        
def lv():
    stdlog('parser: ' + 'lv')
    # %s "blog-post-title.*?</a>" source/lv-rbvuetun*.html | cut -d '>' -f 3 | cut -d '<' -f 1
    parser = '''
    jq -r '.posts[].title' source/lv-rbvuetun*.html | sed -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('lv: ' + 'parsing fail')
    for post in posts:
        appender(post, 'lv')

def five4bb47h():
    stdlog('parser: ' + 'sabbath')
    parser = '''
    %s "aria-label.*?>" source/sabbath-*.html | cut -d '"' -f 2 | sed -e '/Search button/d' -e '/Off Canvas Menu/d' -e '/Close drawer/d' -e '/Close search modal/d' -e '/Header Menu/d' | tr "..." ' ' | grep "\S" | cat
    ''' % (fancygrep)
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('sabbath: ' + 'parsing fail')
    for post in posts:
        appender(post, 'sabbath')

def midas():
    stdlog('parser: ' + 'midas')
    parser = '''
    grep "/h3" source/midas-*.html --no-filename | sed -e 's/<\/h3>//' -e 's/^ *//g' -e '/^$/d' -e 's/^ *//g' -e 's/[[:space:]]*$//' -e '/^$/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('midas: ' + 'parsing fail')
    for post in posts:
        appender(post, 'midas')

#def snatch():
#    stdlog('parser: ' + 'snatch')
#    parser = '''
#    %s "a-b-n-name.*?</div>" source/snatch-*.html | cut -d '>' -f 2 | cut -d '<' -f 1
#    ''' % (fancygrep)
#    posts = runshellcmd(parser)
#    if len(posts) == 1:
#        errlog('snatch: ' + 'parsing fail')
#    for post in posts:
#        appender(post, 'snatch')

def marketo():
    stdlog('parser: ' + 'marketo')
    parser = '''
    grep '<a href="/lot' source/marketo-*.html | sed -e 's/^ *//g' -e '/Show more/d' -e 's/<strong>//g' | cut -d '>' -f 2 | cut -d '<' -f 1 | sed -e '/^$/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('marketo: ' + 'parsing fail')
    for post in posts:
        appender(post, 'marketo')

def rook():
    stdlog('parser: ' + 'rook')
    parser = '''
    grep 'class="post-title"' source/rook-*.html | cut -d '>' -f 2 | cut -d '<' -f 1 | sed '/^&#34/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('rook: ' + 'parsing fail')
    for post in posts:
        appender(post, 'rook')

def cryp70n1c0d3():
    stdlog('parser: ' + 'cryp70n1c0d3')
    parser = '''
    grep '<td class="selection"' source/cryp70n1c0d3-*.html | cut -d '>' -f 2 | cut -d '<' -f 1 | sed -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('cryp70n1c0d3: ' + 'parsing fail')
    for post in posts:
        appender(post, 'cryp70n1c0d3')

def mosesstaff():
    stdlog('parser: ' + 'mosesstaff')
    parser = '''
    grep '<h2 class="entry-title">' source/moses-moses-staff.html -A 3 --no-filename | grep '</a>' | sed 's/^ *//g' | cut -d '<' -f 1 | sed 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('mosesstaff: ' + 'parsing fail')
    for post in posts:
        appender(post, 'mosesstaff')

def nightsky():
    stdlog('parser: ' + 'nightsky')
    parser = '''
    grep 'class="mdui-card-primary-title"' source/nightsky-*.html --no-filename | cut -d '>' -f 3 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('nightsky: ' + 'parsing fail')
    for post in posts:
        appender(post, 'nightsky')

def pandora():
    stdlog('parser: ' + 'pandora')
    parser = '''
    grep '<span class="post-title gt-c-content-color-first">' source/pandora-*.html | cut -d '>' -f 2 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('pandora: ' + 'parsing fail')
    for post in posts:
        appender(post, 'pandora')

def stormous():
    stdlog('parser: ' + 'stormous')
    # grep '<p> <h3> <font color="' source/stormous-*.html | grep '</h3>' | cut -d '>' -f 4 | cut -d '<' -f 1 | sed -e 's/^ *//g' -e 's/[[:space:]]*$//'
    # grep '<h3>' source/stormous-*.html | sed -e 's/^ *//g' -e 's/[[:space:]]*$//' | grep "^<h3> <font" | cut -d '>' -f 3 | cut -d '<' -f 1 | sed 's/[[:space:]]*$//'
    parser = '''
    awk '/<h3>/{getline; print}' source/stormous-*.html | sed -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('stormous: ' + 'parsing fail')
    for post in posts:
        appender(post, 'stormous')

def leaktheanalyst():
    stdlog('parser: ' + 'leaktheanalyst')
    parser = '''
    grep '<label class="news-headers">' source/leaktheanalyst-*.html | cut -d '>' -f 2 | cut -d '<' -f 1 | sed -e 's/Section //' -e 's/#//' -e 's/^ *//g' -e 's/[[:space:]]*$//' | sort -n | uniq
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('leaktheanalyst: ' + 'parsing fail')
    for post in posts:
        appender(post, 'leaktheanalyst')

def kelvinsecurity():
    stdlog('parser: ' + 'kelvinsecurity')
    parser = '''
    egrep -o '<span style="font-size:20px;">([[:alnum:]]| |\.)+</span>' source/kelvinsecurity-*.html | cut -d '>' -f 2 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('kelvinsecurity: ' + 'parsing fail')
    for post in posts:
        appender(post, 'kelvinsecurity')

def onyx():
    stdlog('parser: ' + 'onyx')
    parser = '''
    grep '<h6>' source/onyx-*.html | cut -d '>' -f 2 | cut -d '<' -f 1 | sed -e '/^[[:space:]]*$/d' -e '/Connect with us/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('onyx: ' + 'parsing fail')
    for post in posts:
        appender(post, 'onyx')

def mindware():
    stdlog('parser: ' + 'mindware')
    parser = '''
    grep '<div class="card-header">' source/mindware-*.html | cut -d '>' -f 2 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('mindware: ' + 'parsing fail')
    for post in posts:
        appender(post, 'mindware')


def cheers():
    stdlog('parser: ' + 'cheers')
    parser = '''
    grep '<a href="' source/cheers-*.html | grep -v title | cut -d '>' -f 2 | cut -d '<' -f 1 | sed -e '/Cheers/d' -e '/Home/d' -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('cheers: ' + 'parsing fail')
    for post in posts:
        appender(post, 'cheers')

def yanluowang():
    stdlog('parser: ' + 'yanluowang')
    parser = '''
    grep '<a href="/posts' source/yanluowang-*.html | cut -d '>' -f 2 | cut -d '<' -f 1 | sed -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('yanluowang: ' + 'parsing fail')
    for post in posts:
        appender(post, 'yanluowang')

def omega():
    stdlog('parser: ' + '0mega')
    parser = '''
    grep "<tr class='trow'>" -C 1 source/0mega-*.html | grep '<td>' | cut -d '>' -f 2 | cut -d '<' -f 1 | sort --uniq
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('0mega: ' + 'parsing fail')
    for post in posts:
        appender(post, '0mega')

def redalert():
    stdlog('parser: ' + 'redalert')
    parser = '''
    egrep -o "<h3>([A-Za-z0-9 ,\'.-])+</h3>" source/redalert-*.html | cut -d '>' -f 2 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('redalert: ' + 'parsing fail')
    for post in posts:
        appender(post, 'redalert')

def daixin():
    stdlog('parser: ' + 'daixin')
    parser = '''
    grep '<h4 class="border-danger' source/daixin-*.html | cut -d '>' -f 3 | cut -d '<' -f 1 | sed -e 's/^ *//g' -e '/^$/d' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('daixin: ' + 'parsing fail')
    for post in posts:
        appender(post, 'daixin')

def icefire():
    stdlog('parser: ' + 'icefire')
    parser = '''
    grep align-middle -C 2 source/icefire-*.html | grep span | grep -v '\*\*\*\*' | grep -v updating | grep '\*\.' | cut -d '>' -f 2 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('icefire: ' + 'parsing fail')
    for post in posts:
        appender(post, 'icefire')

def donutleaks():
    stdlog('parser: ' + 'donutleaks')
    parser = '''
    grep '<h2 class="post-title">' source/donutleaks-*.html --no-filename | cut -d '>' -f 3 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('donutleaks: ' + 'parsing fail')
    for post in posts:
        appender(post, 'donutleaks')
        
def sparta():
    stdlog('parser: ' + 'sparta')
    parser = '''
    grep 'class="card-header d-flex justify-content-between"><span>' source/sparta-*.html | cut -d '>' -f 4 | cut -d '<' -f 1 | sed -e '/^[[:space:]]*$/d' && grep '<div class="card-header d-flex justify-content-between"><span>' source/sparta-*.html | grep -v '<h2>' | cut -d '>' -f 3 | cut -d '<' -f 1 | sed -e 's/^ *//g' -e 's/[[:space:]]*$//'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('sparta: ' + 'parsing fail')
    for post in posts:
        appender(post, 'sparta')

def qilin():
    stdlog('parser: ' + 'qilin')
    parser = '''
    grep 'class="item_box-info__link"' source/qilin-kb*.html | cut -d '"' -f 2 | sed '/#/d'
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('qilin: ' + 'parsing fail')
    for post in posts:
        appender(post, 'qilin')

def shaoleaks():
    stdlog('parser: ' + 'shaoleaks')
    parser = '''
    grep '<h2 class="entry-title' source/shaoleaks-*.html | cut -d '>' -f 3 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('shaoleaks: ' + 'parsing fail')
    for post in posts:
        appender(post, 'shaoleaks')

def mallox():
    stdlog('parser: ' + 'mallox')
    parser = '''
    grep 'class="card-title"' source/mallox-*.html | cut -d '>' -f 2 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('mallox: ' + 'parsing fail')
    for post in posts:
        appender(post, 'mallox')

def medusa():
    stdlog('parser: ' + 'medusa')
    parser = '''
    grep --no-filename '<h2 class="entry-title default-max-width">' source/medusa-*.html | cut -d '>' -f 3 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('medusa: ' + 'parsing fail')
    for post in posts:
        appender(post, 'medusa')

def dataleak():
    stdlog('parser: ' + 'play')
    # %s '(?<=\\"\\").*?(?=div)' source/play-*.html | tr -d '<>' | tr -d \\'  | grep -v \?\? 
    parser = '''
    grep '<h2 class="post-title">' source/dataleak-*.html | cut -d '>' -f 2 | cut -d '<' -f 1
    '''
    posts = runshellcmd(parser)
    if len(posts) == 1:
        errlog('dataleak: ' + 'parsing fail')
    for post in posts:
        appender(post, 'dataleak')

### NEW PARSERS USING ONLY PYTHON 

def monti():
    stdlog('parser: ' + 'monti')
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
                    appender(title, 'monti', description)
        except:
            errlog('monti: ' + 'parsing fail')
            pass 
                

def karakurt():
    stdlog('parser: ' + 'karakurt')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('karakurt-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('article', {"class": "ciz-post"})
                for div in divs_name:
                    title = div.h3.a.text.strip()
                    try:
                        description = div.find('div', {'class': 'post-des'}).p.text.strip()
                    except:
                        errlog('karakurt: ' + 'parsing fail')
                    appender(title, 'karakurt', description.replace('\nexpand',''))
                divs_name=soup.find_all('div', {"class": "category-mid-post-two"})
                for div in divs_name:
                    title = div.h2.a.text.strip()
                    try:
                        description = div.find('div', {'class': 'post-des dropcap'}).p.text.strip()
                    except:
                        errlog('karakurt: ' + 'parsing fail')
                    appender(title, 'karakurt', description.replace('\nexpand',''))
                file.close()
        except:
            errlog('karakurt: ' + 'parsing fail')
            pass 


def projectrelic():
    stdlog('parser: ' + 'projectrelic')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('projectrelic-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "content"})
                for div in divs_name:
                    title = div.find('div', {'class': 'name'}).text.strip()
                    description =  div.find('div', {'class': 'description'}).text.strip()
                    # stdlog(title)
                    appender(title, 'projectrelic', description)
                file.close()
        except:
            errlog('projectrelic: ' + 'parsing fail')
            pass 


def royal():
    stdlog('parser: ' + 'royal')
    for filename in os.listdir('source'):
        #try:
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
        #except:
        #    errlog('royal: ' + 'parsing fail')
        #    pass    

def lockbit3():
    stdlog('parser: ' + 'lockbit3')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('lockbit3-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "post-block bad"})
                for div in divs_name:
                    title = div.find('div',{"class": "post-title"}).text.strip()
                    description = div.find('div',{"class" : "post-block-text"}).text.strip()
                    # stdlog(title)
                    appender(title, 'lockbit3', description.replace('\n',''))
                file.close()
        except:
            errlog('lockbit3: ' + 'parsing fail')
            pass    

def blackbasta():
    stdlog('parser: ' + 'blackbasta')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('blackbasta-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card"})
                for div in divs_name:
                    title = div.find('a', {"class": "blog_name_link"}).text.strip()
                    descs = div.find_all('p')
                    description = ''
                    for desc in descs:
                        description += desc.text.strip()
                    appender(title, 'blackbasta', description.replace('\n','').replace('ADDRESS',' Address '))
                file.close()
        except:
            errlog('blackbasta: ' + 'parsing fail')
            pass    

# HTML Version see bellow for JSON version 
#def ransomhouse():
#    stdlog('parser: ' + 'ransomhouse')
#    for filename in os.listdir('source'):
#        try:
#            if filename.startswith('ransomhouse-'):
#                html_doc='source/'+filename
#                file=open(html_doc, 'r')
#                data = json.load(file)
#                for element in data['data']:
#                    title = element['header']
#                    website = element['url']
#                    description = re.sub(r'<[^>]*>', '',element['info'])
#                    # stdlog(title)
#                    appender(title, 'ransomhouse', description, website)
#                file.close()
#        except:
#            errlog('ransomhouse: ' + 'parsing fail')
#            pass    

def hive():
    stdlog('parser: ' + 'hive')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('hive-hiveapi'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                htmlfile = file.read()
                jsonfile = re.sub(r'<[^>]+>', '', htmlfile)
                data = json.loads(jsonfile)
                for element in data:
                    title = element['title']
                    website = element['website']
                    try:
                        description = element['description'].replace('\n',' ')
                    except:
                        errlog('hive: ' + 'something happen')
                    appender(title, 'hive', description, website)
                file.close()
        except:
            errlog('hive: ' + 'parsing fail')
            pass    

# def hive():
#   stdlog('parser: ' + 'hive')
#    for filename in os.listdir('source'):
#        try:
#            html_doc='source/'+filename
#            file=open(html_doc,'r')
#            soup=BeautifulSoup(file,'html.parser')
#            if 'api' in filename:
#                jsonpart= soup.pre.contents
#                data = json.loads(jsonpart[0])
#                for entry in data:
#                    appender(entry['title'].strip(), 'hive', entry["description"].strip(), entry["website"].strip())
#            else:
#                divs_name=soup.find_all('div', {"class": "blog-card-info"})
#                for div in divs_name:
#                    title=div.h2.text.strip()
#                    if div.p is not None:
#                        description=div.p.text.strip()
#                    else:
#                        description = None
#                    appender(title, hive, description)
#        except:
#            errlog('hive: ' + 'parsing fail')
#            pass    

def vicesociety():
    stdlog('parser: ' + 'vicesociety')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('vicesociety-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('td',{"valign":"top"})
                for div in divs_name:
                    try:
                        title = div.find("font", {"size":4}).text.strip()
                        for description in div.find_all("font", {"size":2, "color":"#5B61F6"}):
                            if not description.b.text.strip().startswith("http"):
                                desc = description.get_text()
                                appender(title, 'vicesociety', desc)
                    except:
                        errlog('vicesociety: ' + 'parsing fail')
                file.close()
        except:
            errlog('vicesociety: ' + 'parsing fail')
            pass

def unsafe():
    stdlog('parser: ' + 'unsafe')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('unsafe-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "info"})
                for div in divs_name:
                    title = str(div.find('h4').get_text())
                    titre_h6 = div.find_all("h6")
                    website = ''
                    country = ''
                    revenue = ''
                    for info in titre_h6:
                        if "website" in str(info.text):
                            website = re.sub(r'[^a-zA-Z0-9\.:/]', '', str(info.text.replace('website: ','https://')))
                        if "country" in str(info.text): 
                            country = str(info.text)
                        if "revenue" in str(info.text): 
                            revenue = str(info.text)
                    description = country + ' -' + revenue
                    appender(title, 'unsafe', description, website)
        except:
            errlog('unsafe: ' + 'parsing fail')
            pass

def bianlian():
    stdlog('parser: ' + 'bianlian')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('bianlian-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('section', {"class": "list-item"})
                for div in divs_name:
                    title = div.h1.text.strip()
                    description = div.div.text.strip()
                    appender(title, 'bianlian', description)
                file.close()
        except:
            print("Failed during : " + filename)
            pass

def play():
    stdlog('parser: ' + 'play')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('play-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('th', {"class": "News"})
                for div in divs_name:
                    title = div.next_element.strip()
                    appender(title, 'play')
                file.close()
        except:
            errlog('play: ' + 'parsing fail')
            pass

def clop():
    stdlog('parser: ' + 'clop')
    blacklist=['HOME', 'HOW TO DOWNLOAD?', 'ARCHIVE']
    for filename in os.listdir('source'):
        if filename.startswith('clop-'):
            html_doc='source/'+filename
            file=open(html_doc,'r')
            soup=BeautifulSoup(file,'html.parser')
            divs_name=soup.find_all('span', {"class": "g-menu-item-title"})
            for div in divs_name:
                for item in div.contents :
                    if item in blacklist:
                        continue
                    appender(item, 'clop')

def nokoyawa():
    stdlog('parser: ' + 'nokoyawa')
    for filename in os.listdir('source'):
        try:
           if filename.startswith('nokoyawa-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "relative bg-white rounded-lg shadow dark:bg-gray-700"})
                for div in divs_name:
                    title = div.find('h3').text.strip().split('\n')[0].strip()
                    description = div.find('p', {'class':"break-all"}).text.strip()
                    appender(title, 'nokoyawa',description.replace('\n',' '))
                file.close()
        except:
            errlog('nokoyawa: ' + 'parsing fail')
            pass

def alphv():
    stdlog('parser: ' + 'alphv')
    for filename in os.listdir('source'):
        try:
           if filename.startswith('alphv-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                if 'alphvmmm' in filename:
                    try:
                        jsonpart= soup.pre.contents
                        data = json.loads(jsonpart[0])
                        for entry in data['items']:
                            title = entry['title'].strip()
                            description = entry['publication']['description'].strip()
                            website = entry['publication']['url'].strip()
                            description = re.sub(r"anonfiles.com/.*/", "anonfiles.com/*****/", description)
                            appender(title, 'alphv',description.replace('\n',' '),website)
                    except:
                        errlog('nokoyawa: ' + 'parsing fail')
                else: 
                    divs_name=soup.find_all('div', {'class': 'post-body'})
                    for div in divs_name:
                        title = div.find('div', {'class': 'post-header'}).text.strip()
                        description = div.find('div', {'class': 'post-description'}).text.strip()
                        appender(title, 'alphv',description.replace('\n',' '))
                file.close()
        except:
            errlog('alphv: ' + 'parsing fail')
            pass

def ransomhouse():
    stdlog('parser: ' + 'ransomhouse')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ransomhouse-zoh'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                data = json.load(file)
                for element in data['data']:
                    title = element['header']
                    website = element['url']
                    description = re.sub(r'<[^>]*>', '',element['info'])
                    # stdlog(title)
                    appender(title, 'ransomhouse', description,website)
                file.close()
        except:
            errlog('ransomhouse: ' + 'parsing fail')
        #   pass
    for filename in os.listdir('source'):
        try:
            if filename.startswith('ransomhouse-'):
                html_doc='source/'+filename
                file=open(html_doc, 'r')
                data = json.load(file)
                for element in data['data']:
                    title = element['header']
                    website = element['url']
                    description = re.sub(r'<[^>]*>', '',element['info'])
                    # stdlog(title)
                    appender(title, 'ransomhouse', description, website)
                file.close()
        except:
            errlog('ransomhouse: ' + 'parsing fail')
#            pass    

def avoslocker():
    stdlog('parser: ' + 'avoslocker')
    for filename in os.listdir('source'):
        try:
           if filename.startswith('avoslocker-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "card"})
                for div in divs_name:
                    title = div.find('h5', {"class": "card-brand"}).text.strip()
                    description = div.find('div', {"class": "card-desc"}).text.strip()
                    appender(title, 'avoslocker',description.replace('\n',' '))
                file.close()
        except:
            errlog('avoslocker: ' + 'parsing fail')
            pass

def cuba():
    stdlog('parser: ' + 'cuba')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('cuba-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {'class':'list-text'})
                for div in divs_name:
                    title = div.a['href'].split('/')[2]
                    if '.onion' not in title: 
                        description = div.a.text.strip()
                        appender(title, 'cuba', description)
                file.close()
        except:
            errlog('cuba: ' + 'parsing fail')
            pass

def snatch():
    stdlog('parser: ' + 'snatch')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('snatch-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('div', {"class": "ann-block"})
                for div in divs_name:
                    title = div.find('div', {'class': 'a-b-n-name'}).text.strip()
                    description = div.find('div', {'class': 'a-b-text'}).text.strip()
                    appender(title, 'snatch', description)
                file.close()
        except:
            errlog('snatch: ' + 'parsing fail')
            pass

def blackbyte():
    stdlog('parser: ' + 'blackbyte')
    for filename in os.listdir('source'):
        try:
            if filename.startswith('blackbyte-'):
                html_doc='source/'+filename
                file=open(html_doc,'r')
                soup=BeautifulSoup(file,'html.parser')
                divs_name=soup.find_all('table', {"class": "table table-bordered table-content"})
                # <table class="table table-bordered table-content ">
                for div in divs_name:
                    title = div.find('h1').text.strip()
                    description = div.find('p').text.strip()
                    appender(title, 'blackbyte', description)
                file.close()
        except:
            errlog('blackbyte: ' + 'parsing fail')
            pass