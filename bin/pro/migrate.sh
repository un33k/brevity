#!/bin/bash
# Running as root
##############################################
if [ -z "$*" ]; then
    echo "Missing username"
    echo "Example: command <username>"
    echo ""
    exit 0
fi

ADMIN_USER=$1

do_migrate(){
    source /srv/www/simplyfound.com/pri/venv/bin/activate
    cd /srv/www/simplyfound.com/pri/venv/webroot
    git pull
    git checkout production
    git pull
    pip install -r env/reqs/pro.txt
    bin/pro/manage.py migrate
}
export -f do_migrate

update_seekrets(){
    cd /srv/www/seekrets/simplyfound-seekrets
    git pull
    git checkout production
    git pull
}
export -f update_seekrets

# Update source code and seekrets
echo '**** Update seekrets simplyfound.com ****'
su $ADMIN_USER -c "bash -c update_seekrets"

# Collect static assets
echo '**** Migrate Production Database ****'
su $ADMIN_USER -c "bash -c do_migrate"

# Restart webserver
echo '**** Restart web server -- simplyfound.com ****'
supervisorctl stop simplyfound.com
supervisorctl start simplyfound.com
