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
echo '**** Bootstrap away! - Integration ****'

update_webroot(){
    source /srv/www/simplyfound.net/pri/venv/bin/activate
    cd /srv/www/simplyfound.net/pri/venv/webroot
    git pull
    git checkout integration
    git pull
    pip install -r env/reqs/int.txt
    bin/int/manage.py group --load
    bin/int/manage.py category --load
    bin/int/manage.py target --load
    bin/int/manage.py tag --load
}
export -f update_webroot

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

echo '**** Update seekrets simplyfound.net ****'
su $ADMIN_USER -c "bash -c update_seekrets"

# Restart webserver
echo '**** Restart web server -- simplyfound.net ****'
supervisorctl stop simplyfound.net
supervisorctl start simplyfound.net

# Dump cache
echo '**** Dump cach -- simplyfound.com ****'
redis-cli -h cache-host flushall
