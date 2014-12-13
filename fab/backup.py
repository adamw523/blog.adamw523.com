from fabric.contrib.files import cd, put, run

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
