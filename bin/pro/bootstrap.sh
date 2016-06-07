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
echo '**** Bootstrap away! - Production ****'

update_webroot(){
    source /srv/www/simplyfound.com/pri/venv/bin/activate
    cd /srv/www/simplyfound.com/pri/venv/webroot
    git pull
    git checkout production
    git pull
    pip install -r env/reqs/pro.txt
    bin/pro/manage.py group --load
    bin/pro/manage.py category --load
    bin/pro/manage.py target --load
    bin/pro/manage.py tag --load
}
export -f update_webroot

update_seekrets(){
    cd /srv/www/seekrets/simplyfound-seekrets
    git pull
    git checkout production
    git pull
}
export -f update_seekrets

# Update source code and seekrets
echo '**** Update Webroot simplyfound.com ****'
su $ADMIN_USER -c "bash -c update_webroot"

echo '**** Update seekrets simplyfound.com ****'
su $ADMIN_USER -c "bash -c update_seekrets"

# Restart webserver
echo '**** Restart web server -- simplyfound.com ****'
supervisorctl stop simplyfound.com
supervisorctl start simplyfound.com

# Dump cache
echo '**** Dump cach -- simplyfound.com ****'
redis-cli -h cache-host flushall
