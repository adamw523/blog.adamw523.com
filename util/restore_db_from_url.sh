#!/bin/bash

cd /tmp
curl -o dump.sql.gz $1
zcat dump.sql.gz  |mysql -h mysql --password=$MYSQL_ROOT_PASSWORD wordpress
rm dump.sql.gz

