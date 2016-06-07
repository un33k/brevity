import os
import json

PROJ_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))

# Path to our secret file outside our project directory. @ (wwww level)
#######################################
SECRET_FILE = os.path.abspath(os.path.join(PROJ_ROOT_DIR, "seekrets.json"))
if not os.path.exists(SECRET_FILE):
    warnings.warn('Secret file not found')
    sys.exit(0)
else:
    SEEKRETS = json.load(open(SECRET_FILE, 'r'))

DEPLOYMENT_TYPE = str(SEEKRETS['deployment_type']).upper()
