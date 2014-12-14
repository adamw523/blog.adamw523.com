from fabric.colors import red as _red
from fabric.contrib.files import cd, env, put, run
from fabric.utils import abort
import os

def backup_db_to_s3():
    with cd('builds/adamw523blog'):
        v = (env.s3_access_key, env.s3_secret_key, env.s3_backup_bucket)
        run('fig run util /backup_db_to_s3.sh "%s" "%s" "%s"' % v)

def backup_wp_content_to_s3():
    with cd('builds/adamw523blog'):
        v = (env.s3_access_key, env.s3_secret_key, env.s3_backup_bucket)
        run('fig run util /backup_wp_content_to_s3.sh "%s" "%s" "%s"' % v)

def restore_db_from_url():
    path = os.getenv('DBURL', None)
    if not path:
        abort(_red("Must provide DBURL in environment eg:") + "\n$ DBURL='http://s3server/path/file.gz' fab production restore_db_from_url")
    with cd('builds/adamw523blog'):
        run('fig run util /restore_db_from_url.sh "%s"' % (path))

def restore_wp_content_from_url():
    path = os.getenv('DBURL', None)
    if not path:
        abort(_red("Must provide DBURL in environment eg:") + "\n$ DBURL='http://s3server/path/file.gz' fab production restore_db_from_url")
    with cd('builds/adamw523blog'):
        run('fig run util /restore_wp_content_from_url.sh "%s"' % (path))

