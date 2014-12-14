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

from fab.backup import *
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

    # S3 config
	env.s3_config = ConfigParser.ConfigParser()
	env.s3_config.read(['private/boto.cfg'])
	env.s3_access_key = env.s3_config.get('Credentials', 'aws_access_key_id')
	env.s3_secret_key = env.s3_config.get('Credentials', 'aws_secret_access_key')
	env.s3_backup_bucket = env.s3_config.get('Credentials', 'backup_bucket')

#---------------------------
# Local
#---------------------------

#---------------------------
# Database Related
#---------------------------


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

