cat groups.json | jq 'map(.name)'  | tr -cd '[:alnum:].\n' | while read group;
do
    echo "Checking information for Group ${group} ...  "
    curl -s  https://malpedia.caad.fkie.fraunhofer.de/details/win.${group} > /tmp/desc.txt
    metadescription=$(cat /tmp/desc.txt | xmllint --html --xpath 'string(/html/head/meta[@name="description"]/@content)' - 2>/dev/null)
    if [ ! -z "$metadescription" ]
    then
        if [[ "$metadescription" != "Details"* ]]; 
        then
            if [[ $metadescription != "Ransomware." ]];
            then 
                echo "${metadescription}"  > ./source/descriptions/${group}.txt
            fi
        fi
    fi
done