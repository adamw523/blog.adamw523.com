import ConfigParser
import csv
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

from fab.deploy import *

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

def production():
	"""
	Select production environment
	"""

	# get config file
	env.config = ConfigParser.ConfigParser()
	env.config.read(['private/dodo.cfg'])

	# set values from config
	env.hosts = [env.config.get('production', 'host')]
	env.user = env.config.get('production', 'user')

#---------------------------
# Local
#---------------------------

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

def backup_wp_content():
    now = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d_%H-%M-%S')
    remote_dir = '~'
    #filename = '%s_%s_dump.sql' % (database, now)
    #remote_path = remote_dir + '/' + filename
    #command = 'mysqldump --user="%s" --password="%s" %s > %s'

    file_path = '/tmp/wp-content-%s.tgz' % now
    run('tar -czf %s --directory=/sites/blog wp-content' % (file_path))
    get(file_path, 'backups/')
    run('rm %s' % (file_path))



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

