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

