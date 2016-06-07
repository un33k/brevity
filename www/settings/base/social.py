import sys

from .seekrets import *

# Social Settings
#######################################
SOCIAL_AUTH_LOGIN_ERROR_URL = '/account/user/login'

this_file = sys.modules[__name__]
for key, value in SEEKRETS.get('social_settings', {}).items():
    setattr(this_file, key, value)

SOCIAL_AUTH_ENABLED_PROVIDERS = [
    {
        'name': 'Facebook',
        'module': 'facebook',
        'icon': 'facebook-f'
    },
    {
        'name': 'Google',
        'module': 'google-plus',
        'icon': 'google-plus'
    }
]

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'profileware.pipeline.get_unique_username',
    'profileware.pipeline.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'profileware.pipeline.save_photo',
    # 'social.pipeline.debug.debug',
)

# Google+ SignIn (google-plus)
SOCIAL_AUTH_GOOGLE_PLUS_IGNORE_DEFAULT_SCOPE = True
SOCIAL_AUTH_GOOGLE_PLUS_SCOPE = [
    # 'https://www.googleapis.com/auth/plus.login',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, first_name, last_name, email'
}
