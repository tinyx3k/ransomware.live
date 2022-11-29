#!/bin/bash

# url configuration
URL="https://www.ransomware.live/#/profiles?id="

# values: always hourly daily weekly monthly yearly never
FREQ="weekly"

# begin new sitemap
exec 1> docs/sitemap.xml

# print head
echo '<?xml version="1.0" encoding="UTF-8"?>'
echo '<!-- generator="Julien Mousqueton Sitemap Generator" -->'
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

# print urls
for GROUP in $(grep name groups.json  | cut -d: -f2  | tr -d , | tr -d \")
do 
  DATE=$(date +%F)
  echo "<url>"
  echo " <loc>${URL}${GROUP}</loc>"
  echo " <lastmod>$DATE</lastmod>"
  echo " <changefreq>$FREQ</changefreq>"
  echo "</url>"
done

# print foot
echo "</urlset>"
