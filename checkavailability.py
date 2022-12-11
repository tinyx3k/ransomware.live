from sharedutils import striptld
from sharedutils import openjson
from sharedutils import checktcp
from sharedutils import siteschema
from sharedutils import socksfetcher
from sharedutils import getsitetitle
from sharedutils import getonionversion
from sharedutils import checkgeckodriver
from sharedutils import sockshost, socksport
from sharedutils import stdlog, dbglog, errlog, honk
import json

groups = openjson("groups.json")
    # iterate each provider
for group in groups:
        # stdlog('ransomwatch: ' + 'working on ' + group['name'])
        # iterate each location/mirror/relay
        for host in group['locations']:
            # stdlog('ransomwatch: ' + 'updating ' + host['slug'])
            if host['available'] is False:
                if host['enabled'] is True:
                    print('- ' + group['name'] + ' : ' + host['slug'] + ' needs attention')
            else:
                if host['enabled'] is False:
                   print('- ' + group['name'] + ' : ' + host['slug'] + ' is mistakens') 
