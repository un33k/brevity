#!/usr/bin/env bash
# If your site has sitemap.xml that changes often, it is a good idea to let Google know.
# Note: It is not a good idea to call Google everytime something changes.
# Instead: Add this script to your cronjob to run as often as you want and no more!
#######################################################################################

source /srv/www/simplyfound.com/pri/venv/bin/activate
cd /srv/www/simplyfound.com/pri/venv/webroot
bin/pro/manage.py ping_google /sitemap.xml

exit 0
