#!/bin/bash

cd /var/www/html
curl $1 | tar -xvzf -

