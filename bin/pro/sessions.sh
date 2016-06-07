#!/usr/bin/env bash
# If you are storing the user sessions in DB, it is a good idea to purge them often.
###################################################################################

source /srv/www/simplyfound.com/pri/venv/bin/activate
cd /srv/www/simplyfound.com/pri/venv/webroot
bin/pro/manage.py clearsessions

exit 0
