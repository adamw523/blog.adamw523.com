#!/bin/bash

filename=wordpress_`date +'%Y-%m-%d_%H-%M-%S%z'`

cd /tmp
mysqldump -h mysql --password=$MYSQL_ROOT_PASSWORD wordpress | gzip > $filename.gz
s3put -a "$1" -s "$2" -b "$3" -p /tmp/ -k /blog.adamw523.com/ $filename.gz
rm $filename.gz

