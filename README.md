# Running dev
```
fig up
```

# Restore in dev
```
fig run util /restore_db_from_url.sh "<url_of_db_backup>"
fig run util /restore_wp_content_from_url.sh "<url_of_wp_content_backup>"
```

# Run a backup
```
# backup the DB
fab production backup_db_to_s3

# backup the wp_content directory
fab production backup_wp_content_to_s3
```

# Restore in prod
```
# restore DB
DBURL='http://s3server/path/file.gz' fab production restore_db_from_url

# restore wp_content
WPURL='http://s3server/path/file.tgz' fab production restore_wp_content_from_url

```

# K8s
```
# Create mysql secret
kubectl create secret generic mysql-pass --from-literal=password=changeme

# build wordpress
cd wordpress && docker build -t blog-adamw523-wordpress .

# tag for local development
docker tag blog-adamw523-wordpress host.docker.internal:5000/blog-adamw523-wordpres

# push to local development
docker push host.docker.internal:5000/blog-adamw523-wordpress

# build util tag push locally
cd util && docker build -t blog-adamw523-util .
docker tag blog-adamw523-util host.docker.internal:5000/blog-adamw523-util
docker push host.docker.internal:5000/blog-adamw523-util

# deploy to kubernetes
kubectl apply -f mysql-deployment.yaml
kubectl apply -f mysql-service.yaml
kubectl apply -f wordpress-deployment.yaml
kubectl apply -f wordpress-service.yaml

#


```
