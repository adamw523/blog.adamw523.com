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
            s = re.search(r".*(png|jpg|jpeg)$", href)
            if s:
                outf.write(href + '\n')

def create_posterous_url_replacements():
    """Create CSV files of Posterous image urls to local URLs"""

    a_tags = [] # anchor tags linking to posterous images from posts
    img_tags = [] # image src attributes from posts
    posterous_paths = [] # image paths in posterous backup

    # read source files into arrays
    for path, arr in [  ('posterous_image_files', posterous_paths),
                        ('backups/a_tags', a_tags),
                        ('backups/img_tags', img_tags)]:
        with open(path) as f:
            arr.extend(f.readlines())

    _make_replacment_csv('backups/a_tags_replacments.csv', a_tags, posterous_paths)
    _make_replacment_csv('backups/img_tags_replacments.csv', img_tags, posterous_paths)

def run_posterous_replacements():
    """replace all instances of Posterous image urls with local URLs"""
    # update table_name set field = replace(field, 'foo', 'bar') where instr(field, 'foo') > 0;
    user = env.config.get('mysql', 'user')
    password = env.config.get('mysql', 'password')
    database = env.config.get('mysql', 'database')

    csvs = ['backups/a_tags_replacments.csv', 'backups/img_tags_replacments.csv']
    for path in csvs:
        with open(path) as f:
            reader = csv.reader(f)
            for row in reader:
                sql_command = "update wp_posts set post_content = replace(post_content, '%s', '%s') where instr(post_content, '%s') > 0;"
                sql_command = sql_command % (row[0], row[1], row[0])
                command = "mysql -NB --user=%s --password=%s -e \"%s\" %s"
                command = command % (user, password, sql_command, database)
                run(command, quiet=True)

def _make_replacment_csv(out_path, originals, posterous_paths):
    prefix = "http://blog.adamw523.com/wp-content/posterous_images/"

    # regex for matching/extracting name of image
    e = re.compile(r"(.*?)\.(png|jpg).*")

    # get replacements for src vals
    with open(out_path, 'w') as file_:
        outwriter = csv.writer(file_)
        for a_path in originals:
            path_parts = a_path.split('/')
            m = e.match(path_parts[-1])
            name, extension = m.groups()
            parts = re.split(r"[-_]", name) + [extension]
            matching = filter(lambda x: _contains_all_parts(x, parts), posterous_paths)

            if len(matching) > 0:
                outwriter.writerow([a_path.strip(), prefix + matching[0].strip()])
            else:
                print "not found: %s" % a_path

def _contains_all_parts(s, parts, start=0):
    # Does s contain all strings in parts, in order

    index = s.find(parts[0], start);

    if index == -1:
        return False

    if len(parts) > 1:
        return _contains_all_parts(s, parts[1:], index+1)

    return True


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

