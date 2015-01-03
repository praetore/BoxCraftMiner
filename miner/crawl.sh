#!/bin/bash

if [ -z "$1" ];
then
	echo "Must pass spider as argument";exit 0
fi

if [ -z "$2" ];
then
	echo "Must pass username as argument";exit 0
fi

if [ -z "$3" ];
then
	echo "Must pass password as argument";exit 0
fi

mkdir data

scrapy crawl $1

arr=$(cat miner/list.txt)
for i in $arr
do
	coll=$(echo $i | awk -F, '{print $1}');filename=$(echo $i | awk -F, '{print $2}'); cat "data/"$filename | mongoimport -h ds055980.mongolab.com:55980 -d boxcraft_hardware_components -c $coll -u $2 -p $3
done

rm -R data