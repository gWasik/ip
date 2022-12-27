#!/bin/bash

function ProgressBar {
  let _progress=(${1}*100/${2}*100)/100
  let _done=(${_progress}*4)/10
  let _left=40-$_done
  _fill=$(printf "%${_done}s")
  _empty=$(printf "%${_left}s")
  printf "\rAdd routes to route table (${1}/${2}): [${_fill// /#}${_empty// /-}] ${_progress}%%"
}

# Variables
file_stat="russian.json"
file_raw="russian_subnets_list_raw.txt"
file_user="subnets_user_list.txt"
file_for_calc="russian_subnets_list_raw_for_calc.txt"
file_processed="russian_subnets_list_processed.txt"
#gateway_for_internal_ip=`ip route | awk '/default/ {print $3; exit}'`
#interface=`ip link show | awk -F ': ' '/state UP/ {print $2}'`

wget https://download.ip2location.com/lite/IP2LOCATION-LITE-DB1.BIN.ZIP

# Get addresses RU segment
if [ -e $file_stat ]; then
   echo "File $file_stat exists."
else
  echo "Download RU subnets...";
  curl -o $file_stat -z $file_stat "https://stat.ripe.net/data/country-resource-list/data.json?resource=ru"
  cat $file_stat | jq -r ".data.resources.ipv4[]" > $file_raw
fi;

python3 ./ru_ip.py

# Flush route table
#echo "Flush route table (down interface $interface)..."
#ifdown $interface > /dev/null 2>&1
#echo "Up interface $interface..."
#ifup $interface > /dev/null 2>&1

# Add route
routes_count_in_file=`wc -l $file_processed`
routes_count_current=0
#for line in $(cat $file_processed); do ip route add $line via $gateway_for_internal_ip dev $interface; let "routes_count_current+=1" ; ProgressBar ${routes_count_current} ${routes_count_in_file}; done
#for line in $(cat $file_processed); let "routes_count_current+=1" ; ProgressBar ${routes_count_current} ${routes_count_in_file}; done
echo "routes ${routes_count_in_file}"

if [ -e $file_for_calc ]; then
    echo "Remove temp files..."
    #rm $file_raw $file_for_calc
    rm $file_for_calc
fi;

#routes_count=`ip r | wc -l`
#echo "Routes in routing table: $routes_count"

cp $file_processed $file_for_calc
sort -t . -k 1,1n -k 2,2n -k 3,3n -k 4,4n $file_for_calc>$file_processed

rm $file_for_calc

date=`date`
git commit -a -m "$date"
git push