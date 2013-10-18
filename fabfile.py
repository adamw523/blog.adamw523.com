import ConfigParser
import fabtools
import datetime
import os.path
import re
import sys

from bs4 import BeautifulSoup
from fabric.utils import abort
from fabric.colors import green as _green
from fabric.colors import yellow as _yellow
from fabric.colors import red as _red
from fabric.contrib.files import *
from fabtools import require

env.project_name = 'blog.adamw523.com'
env.local_backups_dir = 'backups'

#---------------------------
# Environemnts
#---------------------------

def dodo():
	"""
	Select DigitalOcean environment
	"""

	# get config file
	env.config = ConfigParser.ConfigParser()
	env.config.read(['private/dodo.cfg'])

	# set values from config
	env.hosts = [env.config.get('dodo', 'host')]
	env.user = env.config.get('dodo', 'user')

def vagrant():
    """
    Select vagrant-managed VM for commands
    """
    env.settings = 'vagrant'

    # get vagrant ssh setup
    vagrant_config = _get_vagrant_config()
    env.key_filename = vagrant_config['IdentityFile']
    env.hosts = ['%s:%s' % (vagrant_config['HostName'], vagrant_config['Port'])]
    env.user = vagrant_config['User']
    env.disable_known_hosts = True

    _set_vagrant_env()

#---------------------------
# Database Related
#---------------------------

def backup_db():
    user = env.config.get('mysql', 'user')
    password = env.config.get('mysql', 'password')
    database = env.config.get('mysql', 'database')

    now = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d_%H-%M-%S')
    remote_dir = '~'
    filename = '%s_%s_dump.sql' % (database, now)
    remote_path = remote_dir + '/' + filename
    command = 'mysqldump --user="%s" --password="%s" %s > %s'

    run(command % (user, password, database, remote_path), quiet=True)
    run('gzip %s' % (remote_path))
    get(remote_path + '.gz', env.local_backups_dir + '/' + filename + '.gz')
    run('rm %s' % (remote_path + '.gz'))

def restore_posterous_pics():
    """Gets Posterous backup from S3"""
    backup_zip_url = "http://s3.amazonaws.com/adamw523_backups/blog.adamw523.com/space-1613972-adamw523-66bc5c3f7d11552b9215dd76c3254c05.zip"
    filename = backup_zip_url.split('/')[-1]
    dirname = filename.split('.')[0]

    with cd('/tmp'):
        #run('wget %s' % backup_zip_url)
        run('unzip -q %s' % filename)

        run('mv %s/image /sites/blog/wp-content/posterous_images' % dirname)

        run('rm -fR %s' % dirname)
        #run('rm %s' % filename)

def wordpress_get_all_posts_content():
    """Write all posts contents to backups/posts_content"""
    user = env.config.get('mysql', 'user')
    password = env.config.get('mysql', 'password')
    database = env.config.get('mysql', 'database')

    command = "mysql -NB --user=%s --password=%s -e 'select post_content from wp_posts' %s"
    contents = run(command % (user, password, database), quiet=True)
    with open('backups/posts_content', 'w') as pcfile:
        pcfile.write(contents)

def get_posterous_images():
    """Get all img and a URLs that link to Posterous from backups/posts_content"""
    contents = ""
    with open('backups/posts_content') as pcfile:
        contents = pcfile.read()

    doc = BeautifulSoup(contents)

    img_tags = doc.select('img[src*=".posterous.com"]')
    with open('backups/img_tags', 'w') as outf:
        for tag in img_tags:
            outf.write(tag['src'] + '\n')

    a_tags = doc.select('a[href*=".posterous.com"]')
    with open('backups/a_tags', 'w') as outf:
        for tag in a_tags:
            href = tag['href']
            if re.search(r".*[png|jpg|jpeg]$", href):
                outf.write(href + '\n')

def replace_posterous_urls():
    # replace all instances of Posterous image urls with local URLs
    # update table_name set field = replace(field, 'foo', 'bar') where instr(field, 'foo') > 0;

    a_tags = []
    img_tags = []
    posterous_paths = []

    for path, arr in [  ('posterous_image_files', posterous_paths),
                        ('backups/a_tags', a_tags),
                        ('backups/img_tags', img_tags)]:
        with open(path) as f:
            arr.extend(f.readlines())

    for a_path in a_tags:
        print a_path


#---------------------------
# Vagrant
#---------------------------

def _vagrant_remount():
    """Remount the vagrant partition"""
    sudo("mount /vagrant -o remount")
    sudo("mount /data -o remount")

def _get_vagrant_config():
    """
    Parses vagrant configuration and returns it as dict of ssh parameters
    and their values
    """
    result = local('vagrant ssh-config', capture=True)
    conf = {}
    for line in iter(result.splitlines()):
        parts = line.split()
        conf[parts[0]] = ' '.join(parts[1:])

    return conf

