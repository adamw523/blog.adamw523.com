filename=wp-content-`date +'%Y-%m-%d_%H-%M-%S%z'`.tgz

cd /var/www/html
tar -czf $filename wp-content
s3put -a "$1" -s "$2" -b "$3" -p `pwd` -k /blog.adamw523.com/ $filename
rm $filename

