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
    sudo('apt --yes install build-essential')
    sudo('apt --yes install libkrb5-dev')
    sudo('apt --yes install nodejs')
    sudo('apt --yes install git htop vim')
    run('npm set progress=false')
    sudo('npm install pm2@latest -g')
    sudo('pm2 startup') # Enable PM2 to restart applications on server boot/reboot

    run('git clone %s %s/%s' % (gitUrl, env.home, env.api_pwd))

@task
def check():
    run('git --version')
    run('node --version')
    run('pm2 version')

@task
def deploy_api(branch='master'):
    with cd('%s/%s' % (env.home, env.api_pwd)):
        # Git
        run('git fetch')
        run('git checkout %s' % branch)
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
