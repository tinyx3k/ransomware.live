#!/bin/bash
online_hosts=$(curl -sL https://raw.githubusercontent.com/jmousqueton/ransomwatch/main/groups.json \
| jq -r '.[].locations[] | select(.available==true) | .slug')
for host in $online_hosts; do
    echo "$host"
    curl -s -I -L --socks5-hostname localhost:9050 "${host}"
    echo "---"
    #headers=$(curl -s -I -L --socks5-hostname localhost:9050 "${host}")
    #filename=$(echo $host | cut -c1-20)
    #filename=$(echo $filename | sed -e 's/[:/]//g')
    #echo "${headers}" > headers/${filename}.txt
done 
