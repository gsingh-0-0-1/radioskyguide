sleep $((180 + $RANDOM % 600))
cd /home/gurmeharsingh/radioskyguide
. /home/gurmeharsingh/.profile
. /home/gurmeharsingh/.bashrc
curl -c /home/gurmeharsingh/radioskyguide/cookies.txt -b /home/gurmeharsingh/radioskyguide/cookies.txt https://www.space-track.org/ajaxauth/login -d "identity=${SPACETRACKUSER}&password=${SPACETRACKPASS}"
echo 
curl --limit-rate 100K --cookie /home/gurmeharsingh/radioskyguide/cookies.txt https://www.space-track.org/basicspacedata/query/class/gp/EPOCH/%3Enow-30/orderby/NORAD_CAT_ID,EPOCH/format/3le > /home/gurmeharsingh/radioskyguide/tle.txt
echo
mv /home/gurmeharsingh/radioskyguide/tle.txt /home/gurmeharsingh/radioskyguide/static/origtle.txt
