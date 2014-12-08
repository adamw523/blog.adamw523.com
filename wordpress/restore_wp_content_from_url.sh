#!/bin/bash

cd /var/www/html
curl $1 | tar -xvzf -
#tar -xzf wp-content_backup.tgz
#rm wp-content_backup.tgz

