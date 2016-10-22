from fabric.api import cd, env, run, task, sudo, put
from fabric.colors import green
from fabric.operations import local

env.use_ssh_config = True
env.forward_agent = True
env.output_prefix = False

gitUrl = 'https://github.com/marmelab/javascript-boilerplate.git'

@task
def install_swap():
    """Install a swapfile on the server, very useful to `npm install` on a t2.micro"""
    print(green('Installing a 1Go swap file at /swapfile'))
    sudo('dd if=/dev/zero of=/swapfile bs=1024 count=1048576')
    sudo('chown root:root /swapfile')
    sudo('chmod 0600 /swapfile')
    sudo('mkswap /swapfile')
    sudo('swapon /swapfile')

@task
def setup_api():
    print(green('Installing dependencies ...'))
    sudo('apt --yes update && apt --yes upgrade')
    sudo('curl -sL https://deb.nodesource.com/setup_6.x | bash -')
    sudo('echo deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main > /etc/apt/sources.list.d/pgdg.list')
    sudo('apt update')
    sudo('apt install --yes --no-install-recommends build-essential git htop libkrb5-dev nodejs htop vim')
    sudo('apt install --force-yes --yes postgresql-9.4 postgresql-contrib-9.4')
    run('npm set progress=false')
    sudo('npm install pm2@latest -g')
    sudo('pm2 startup') # Enable PM2 to restart applications on server boot/reboot

    run('git clone %s %s/%s' % (gitUrl, env.home, env.api_pwd))

@task
def check():
    run('git --version')
    run('node --version')
    run('pm2 version')
    run('psql --version')

@task
def deploy_api():
    with cd('%s/%s' % (env.home, env.api_pwd)):
        # Git
        run('git fetch')
        run('git checkout %s' % env.branch)
        run('git pull')
        # Install dependencies
        run('make install-prod')
        # DB migrations
        run('NODE_ENV=%s make migrate' % env.environment)
        sudo('pm2 restart ./config/pm2_servers/%s.json' % env.environment)

@task
def deploy_static(branch='master'):
    local('git fetch')
    local('git checkout %s' % branch)
    local('git pull')
    local('rm -rf build/*')
    local('NODE_ENV=%s make build' % env.environment)
    local('aws --region=eu-west-1 s3 sync ./build/ s3://%s/' % env.s3_bucket)
