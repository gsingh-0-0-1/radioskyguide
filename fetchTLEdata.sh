sleep $((60 + $RANDOM % 600))
cd /home/gurmeharsingh/radioskyguide
curl -c cookies.txt -b cookies.txt https://www.space-track.org/ajaxauth/login -d "identity=${SPACETRACKUSER}&password=${SPACETRACKPASS}"
curl --limit-rate 100K --cookie cookies.txt https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID,EPOCH/format/3le > tle.txt
mv tle.txt static/origtle.txt
python3.8 processTLE.py
