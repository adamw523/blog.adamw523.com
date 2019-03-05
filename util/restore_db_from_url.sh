#!/bin/bash

cd /tmp
curl -o dump.sql.gz $1
zcat dump.sql.gz  |mysql -h wordpress-mysql --password=$WORDPRESS_DB_PASSWORD wordpress
rm dump.sql.gz

