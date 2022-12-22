from sharedutils import openjson
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
                    print('- ' + group['name'] + ' : ' + host['slug'] + ' host seems down')
            else:
                if host['enabled'] is False:
                   print('- ' + group['name'] + ' : ' + host['slug'] + ' should be enable !!!') 
