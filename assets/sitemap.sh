#!/bin/bash

# url configuration
URL="https://www.ransomware.live/#/profiles?id="

# values: always hourly daily weekly monthly yearly never
FREQ="weekly"

# begin new sitemap
exec 1> docs/sitemap.xml

DATE=$(date +%F)

# print head
echo '<?xml version="1.0" encoding="UTF-8"?>'
echo '<!-- generator="Julien Mousqueton Sitemap Generator" -->'
echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'


echo "<url>"
  echo " <loc>https://www.ransomware.live/#/recentposts</loc>"
  echo " <lastmod>$DATE</lastmod>"
  echo " <changefreq>$FREQ</changefreq>"
  echo "</url>"

echo "<url>"
  echo " <loc>https://www.ransomware.live/#/allposts</loc>"
  echo " <lastmod>$DATE</lastmod>"
  echo " <changefreq>$FREQ</changefreq>"
  echo "</url>"

echo "<url>"
  echo " <loc>https://www.ransomware.live/#/about</loc>"
  echo " <lastmod>$DATE</lastmod>"
  echo " <changefreq>$FREQ</changefreq>"
  echo "</url>"

echo "<url>"
  echo " <loc>https://www.ransomware.live/#/INDEX</loc>"
  echo " <lastmod>$DATE</lastmod>"
  echo " <changefreq>$FREQ</changefreq>"
  echo "</url>"

echo "<url>"
  echo " <loc>https://www.ransomware.live/#/stats</loc>"
  echo " <lastmod>$DATE</lastmod>"
  echo " <changefreq>$FREQ</changefreq>"
  echo "</url>"

echo "<url>"
  echo " <loc>https://www.ransomware.live/#/profiles</loc>"
  echo " <lastmod>$DATE</lastmod>"
  echo " <changefreq>$FREQ</changefreq>"
  echo "</url>"

echo "<url>"
  echo " <loc>https://www.ransomware.live/#/decryption</loc>"
  echo " <lastmod>$DATE</lastmod>"
  echo " <changefreq>$FREQ</changefreq>"
  echo "</url>"

# print urls
for GROUP in $(jq '.[].name' groups.json | tr -d \")
do 
  echo "<url>"
  echo " <loc>${URL}${GROUP}</loc>"
  echo " <lastmod>$DATE</lastmod>"
  echo " <changefreq>$FREQ</changefreq>"
  echo "</url>"
done

# print foot
echo "</urlset>"
