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
    source /srv/www/simplyfound.net/pri/venv/bin/activate
    cd /srv/www/simplyfound.net/pri/venv/webroot
    git pull
    git checkout integration
    git pull
    pip install -r env/reqs/int.txt
    bin/int/manage.py migrate
}
export -f do_migrate

update_seekrets(){
    cd /srv/www/seekrets/simplyfound-seekrets
    git pull
    git checkout integration
    git pull
}
export -f update_seekrets

# Update source code and seekrets
echo '**** Update Webroot simplyfound.net ****'
su $ADMIN_USER -c "bash -c update_webroot"

# Collect static assets
echo '**** Migrate Integration Database ****'
su $ADMIN_USER -c "bash -c do_migrate"

# Restart webserver
echo '**** Restart web server -- simplyfound.net ****'
supervisorctl stop simplyfound.net
supervisorctl start simplyfound.net
