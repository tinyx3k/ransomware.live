#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import urllib.parse
from datetime import datetime as dt

from sharedutils import gcount
from sharedutils import openjson
from sharedutils import postcount
from sharedutils import hostcount
from sharedutils import groupcount
from sharedutils import postssince
from sharedutils import parsercount
from sharedutils import onlinecount
from sharedutils import postslast24h
from sharedutils import version2count
from sharedutils import poststhisyear
from sharedutils import postslastyear
from sharedutils import currentmonthstr
from sharedutils import monthlypostcount
#from sharedutils import headlesscount
#from sharedutils import countcaptchahosts
# from sharedutils import stdlog, dbglog, errlog, honk
from sharedutils import stdlog
from plotting import trend_posts_per_day, plot_posts_by_group, pie_posts_by_group, plot_posts_by_group_past_7_days

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(fmt, t):
    return t.strftime(fmt).replace('{S}', str(t.day) + suffix(t.day))

friendly_tz = custom_strftime('%B {S}, %Y', dt.now()).lower()

NowTime=dt.now()

def writeline(file, line):
    '''write line to file'''
    with open(file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
        f.close()

def groupreport():
    '''
    create a list with number of posts per unique group
    '''
    stdlog('generating group report')
    posts = openjson('posts.json')
    # count the number of posts by group_name within posts.json
    group_counts = gcount(posts)
    # sort the group_counts - descending
    sorted_group_counts = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)
    stdlog('group report generated with %d groups' % len(sorted_group_counts))
    return sorted_group_counts

def mainpage():
    '''
    main markdown report generator - used with github pages
    '''
    stdlog('generating main page')
    uptime_sheet = 'docs/README.md'
    dir_path = r'docs/screenshots'
    screenshots=(len([entry for entry in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, entry))]))
    dir_path = r'docs/ransomware_notes'
    nbransom_notes=sum([len(folder) for r, d, folder in os.walk(dir_path)])-4
    with open(uptime_sheet, 'w', encoding='utf-8') as f:
        f.close()
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '## 📈 Ransomware.live Statistics')
    writeline(uptime_sheet, '_' + friendly_tz + '_')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '🔎 Currently tracking `' + str(groupcount()) + '` groups across `' + str(hostcount()) + '` relays & mirrors - _`' + str(onlinecount()) + '` currently online_ 🟢')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, 'Check recent ransomware posts [`here`](recentposts.md)')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '⏰ There have been `' + str(postslast24h()) + '` posts within the `last 24 hours`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '🕓 There have been `' + str(monthlypostcount()) + '` posts within the `month of ' + currentmonthstr() + '`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '📅 There have been `' + str(postssince(90)) + '` posts within the `last 90 days`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '🏚 There have been `' + str(poststhisyear()) + '` posts since the `1st January ' + str(dt.now().year) + '`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '📸 There are `' +  str(screenshots) + '` ransomware goup hosts screenshots')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '📝 There are `' +  str(nbransom_notes) + '` ransomware notes')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '🚀 There have been `' + str(postslastyear()) + '` posts `last year`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '🐣 There have been `' + str(postcount()) + '` posts `since the dawn of ransomwatch`')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '⚙️ There are `' + str(parsercount()) + '` custom parsers indexing posts')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '_`' + str(version2count()) + '` sites using v2 onion services are no longer indexed - [support.torproject.org](https://support.torproject.org/onionservices/v2-deprecation/)_')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '> See the project [README](https://github.com/jmousqueton/ransomwatch#readme) for backend technicals')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, '')
    writeline(uptime_sheet, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    writeline(uptime_sheet, '')

def indexpage():
    index_sheet = 'docs/INDEX.md'
    with open(index_sheet, 'w', encoding='utf-8') as f:
        f.close()
    groups = openjson('groups.json')
    writeline(index_sheet, '# 🚦 Status')
    writeline(index_sheet, '')
    header = '| Group | Title | Status | Last seen | Location | Screenshoot |'
    writeline(index_sheet, header)
    writeline(index_sheet, '|---|---|---|---|---|---|')
    for group in groups:
        stdlog('generating group report for ' + group['name'])
        for host in group['locations']:
            stdlog('generating host report for ' + host['fqdn'])
            if host['available'] is True:
                statusemoji = '🟢'
                lastseen = ''
            elif host['available'] is False:
                # iso timestamp converted to yyyy/mm/dd
                lastseen = host['lastscrape'].split(' ')[0]
                statusemoji = '🔴'
            if host['title'] is not None:
                title = host['title'].replace('|', '-')
            else:
                title = ''
            screenshot=host['fqdn'].replace('.', '-') + '.png'
            screen=''
            if os.path.exists('docs/screenshots/'+screenshot):
                screen='<a href="https://www.ransomware.live/screenshots/' + screenshot + '" target=_blank>📸</a>'
            line = '| [' + group['name'] + '](https://ransomware.live/#/profiles?id=' + group['name'] + ') | ' + title + ' | ' + statusemoji + ' | ' + lastseen + ' | ' + host['fqdn'] + ' | ' + screen + ' | ' 
            writeline(index_sheet, line)

def sidebar():
    '''
    create a sidebar markdown report
    '''
    stdlog('generating sidebar')
    sidebar = 'docs/_sidebar.md'
    # delete contents of file
    with open(sidebar, 'w', encoding='utf-8') as f:
        f.close()
    writeline(sidebar, '- [home](README.md)')
    writeline(sidebar, '- [group index](INDEX.md)')
    writeline(sidebar, '- [recent posts](recentposts.md)')
    writeline(sidebar, '- [stats & graphs](stats.md)')
    writeline(sidebar, '- [group profiles](profiles.md)')
    stdlog('sidebar generated')

def statspage():
    '''
    create a stats page in markdown containing the matplotlib graphs
    '''
    stdlog('generating stats page')
    statspage = 'docs/stats.md'
    # delete contents of file
    with open(statspage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(statspage, '# 📊 stats')
    writeline(statspage, '')
    writeline(statspage, '_timestamp association commenced october 2021_')
    writeline(statspage, '')
    writeline(statspage, '| ![](graphs/postsbygroup7days.png) | ![](graphs/postsbyday.png) |')
    writeline(statspage, '|---|---|')
    writeline(statspage, '![](graphs/postsbygroup.png) | ![](graphs/grouppie.png) |')
    writeline(statspage, '')
    writeline(statspage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('stats page generated')

def recentposts(top):
    '''
    create a list the last X posts (most recent)
    '''
    stdlog('finding recent posts')
    posts = openjson('posts.json')
    # sort the posts by timestamp - descending
    sorted_posts = sorted(posts, key=lambda x: x['discovered'], reverse=True)
    # create a list of the last X posts
    recentposts = []
    for post in sorted_posts:
        recentposts.append(post)
        if len(recentposts) == top:
            break
    stdlog('recent posts generated')
    return recentposts

def recentpage():
    '''create a markdown table for the last 200 posts based on the discovered value'''
    fetching_count = 200
    stdlog('generating recent posts page')
    recentpage = 'docs/recentposts.md'
    # delete contents of file
    with open(recentpage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(recentpage, '# 📰 200 last posts')
    writeline(recentpage, '')
    #writeline(recentpage, '_last `' + str(fetching_count) + '` posts_')
    #writeline(recentpage, '')
    writeline(recentpage, '| Date | Title | Group |')
    writeline(recentpage, '|---|---|---|')
    for post in recentposts(fetching_count):
        # show friendly date for discovered
        date = post['discovered'].split(' ')[0]
        # replace markdown tampering characters
        title = post['post_title'].replace('|', '-')
        group = post['group_name'].replace('|', '-')
        urlencodedtitle = urllib.parse.quote_plus(title)
        grouplink = '[' + group + '](https://ransomware.live/#/profiles?id=' + group + ')'
        line = '| ' + date + ' | [`' + title + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + grouplink + ' |'
        writeline(recentpage, line)
    writeline(recentpage, '')
    writeline(recentpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('recent posts page generated')

def allposts():
    '''create a markdown table for all posts '''
    stdlog('generating allposts page')
    allpage = 'docs/allposts.md'
    # delete contents of file
    with open(allpage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(allpage, '# 📰 All posts')
    writeline(allpage, '')
    writeline(allpage, '')
    writeline(allpage, '| date | title | group |')
    writeline(allpage, '|---|---|---|')
    for post in recentposts('999999'):
        # show friendly date for discovered
        date = post['discovered'].split(' ')[0]
        # replace markdown tampering characters
        title = post['post_title'].replace('|', '-')
        group = post['group_name'].replace('|', '-')
        urlencodedtitle = urllib.parse.quote_plus(title)
        grouplink = '[' + group + '](https://ransomware.live/#/profiles?id=' + group + ')'
        line = '| ' + date + ' | [`' + title + '`](https://google.com/search?q=' + urlencodedtitle + ') | ' + grouplink + ' |'
        writeline(allpage, line)
    writeline(allpage, '')
    writeline(allpage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('all posts page generated')

def profilepage():
    '''
    create a profile page for each group in their unique markdown files within docs/profiles
    '''
    stdlog('generating profile pages')
    profilepage = 'docs/profiles.md'
    # delete contents of file
    with open(profilepage, 'w', encoding='utf-8') as f:
        f.close()
    writeline(profilepage, '# Profiles')
    writeline(profilepage, '')
    groups = openjson('groups.json')
    for group in groups:
        writeline(profilepage, '## **' + group['name']+'**')
        writeline(profilepage, '')
        description_file = './source/descriptions/'+ group['name']+'.txt'
        if os.path.exists(description_file):
            writeline(profilepage, '')
            with open(description_file, 'r') as file:
                data = file.read().replace('\n', ' ')
            writeline(profilepage,'>'+data)
            writeline(profilepage, '')
        #if group['captcha'] is True:
        #    writeline(profilepage, ':warning: _has a captcha_')
        #    writeline(profilepage, '')
        #if group['parser'] is True:
        #    writeline(profilepage, '_parsing : `enabled`_')
        #    writeline(profilepage, '')
        #else:
        #    writeline(profilepage, '_parsing : `disabled`_')
        #    writeline(profilepage, '')
        # add notes if present
        if group['meta'] is not None:
            writeline(profilepage, '_`' + group['meta'] + '`_')
            writeline(profilepage, '')
        #if group['javascript_render'] is True:
        #    writeline(profilepage, '> fetching this site requires a headless browser')
        #    writeline(profilepage, '')
        if len(group['profile']):
            writeline(profilepage, '### External analysis')
            for profile in group['profile']:
                writeline(profilepage, '- ' + profile)
                writeline(profilepage, '')
        writeline(profilepage, '### URLs')
        writeline(profilepage, '| Title | Available | Last visit | fqdn | screen ')
        writeline(profilepage, '|---|---|---|---|---|')        
        for host in group['locations']:
            if host['available'] is True:
                statusemoji = '🟢'
            elif host['available'] is False:
                statusemoji = '🔴'
                lastseen = host['lastscrape'].split(' ')[0]
            # convert date to ddmmyyyy hh:mm
            date = host['lastscrape'].split(' ')[0]
            date = date.split('-')
            date = date[2] + '/' + date[1] + '/' + date[0]
            time = host['lastscrape'].split(' ')[1]
            time = time.split(':')
            time = time[0] + ':' + time[1]
            screenshot=host['fqdn'].replace('.', '-') + '.png'
            screen='❌'
            if os.path.exists('docs/screenshots/'+screenshot):
                screen='<a href="https://www.ransomware.live/screenshots/' + screenshot + '" target=_blank>📸</a>'
            if host['title'] is not None:
                line = '| ' + host['title'].replace('|', '-') + ' | ' + statusemoji +  ' | ' + date + ' ' + time + ' | `http://' + host['fqdn'] + '` | ' + screen + ' | ' 
                writeline(profilepage, line)
            else:
                line = '| none | ' + statusemoji +  ' | ' + date + ' ' + time + ' | `http://' + host['fqdn'] + '` | ' + screen + ' | ' 
                writeline(profilepage, line)
        if os.path.exists('docs/ransomware_notes/'+ group['name']):
            if os.path.exists('docs/ransomware_notes/'+ group['name'] + '/' + group['name'] + '.txt'):
                ransom_note=group['name'] + '.txt'
            else:
                ransom_note=group['name'] + '1.txt'  
            writeline(profilepage, '')
            writeline(profilepage, '### Ransom note')
            writeline(profilepage, '* 📝 <a href="/ransomware_notes/'+group['name']+'/' + ransom_note + '" target=_blank>`Check ransomware note`</a>')
            writeline(profilepage, '')
        writeline(profilepage, '### Posts')
        writeline(profilepage, '')
        writeline(profilepage, '| post | date |')
        writeline(profilepage, '|---|---|')
        posts = openjson('posts.json')
        for post in posts:
            if post['group_name'] == group['name']:
                date = post['discovered'].split(' ')[0]
                date = date.split('-')
                date = date[2] + '/' + date[1] + '/' + date[0]
                line = '| ' + '`' + post['post_title'].replace('|', '') + '`' + ' | ' + date + ' |'
                writeline(profilepage, line)
        writeline(profilepage, '')
        stdlog('profile page for ' + group['name'] + ' generated')
    writeline(profilepage, '')
    writeline(profilepage, 'Last update : _'+ NowTime.strftime('%A %d/%m/%Y %H.%M') + ' (UTC)_')
    stdlog('profile page generation complete')

def main():
    stdlog('generating docs')
    mainpage()
    indexpage()
    # sidebar()
    recentpage()
    allposts()
    # statspage()
    profilepage()
    # if posts.json has been modified within the last 45 mins, assume new posts discovered and recreate graphs
    if os.path.getmtime('posts.json') > (time.time() - 2700):
        stdlog('posts.json has been modified within the last 45 mins, assuming new posts discovered and recreating graphs')
        trend_posts_per_day()
        plot_posts_by_group()
        pie_posts_by_group()
        plot_posts_by_group_past_7_days()
    else:
        stdlog('posts.json has not been modified within the last 45 mins, assuming no new posts discovered')
