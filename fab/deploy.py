from fabric.contrib.files import cd, put, run

def _copy_files():
    run('mkdir -p builds/adamw523blog')
    put('mysql', 'builds/adamw523blog/')
    put('util', 'builds/adamw523blog/')
    put('wordpress', 'builds/adamw523blog/')
    put('private/fig.yml', 'builds/adamw523blog/')

def deploy_build():
    """
    Build the environment remotely
    """
    _copy_files()
    with cd('builds/adamw523blog'):
        run('fig build')

def deploy_up():
    """
    Run the environment remotely
    """
    with cd('~adam/builds/adamw523blog'):
        run('fig up -d')

def deploy_kill():
    """
    Kill the remote environment
    """
    with cd('~adam/builds/adamw523blog'):
        run('fig kill')

def deploy_rm():
    """
    Remove the remote environment
    """
    with cd('~adam/builds/adamw523blog'):
        run('fig rm --force')

