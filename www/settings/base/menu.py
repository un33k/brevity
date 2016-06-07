from .seekrets import *

# Menu settings - Not used directly
#########################################
SUBMENU_ACCOUNT_PROFILE = [
    {
        "name": "Profile",
        "url": "profileware:account_profile",
        "render_for_authenticated": True,
        "icon": "fa fa-user",
        "display": "icon-name",
    },
    {
        "name": "Preferences",
        "url": "profileware:account_profile_preferences",
        "render_for_authenticated": True,
        "icon": "fa fa-cog",
        "display": "icon-name",
    },
    {
        "name": "Password Change",
        "url": "userware:user_password_change",
        "render_for_authenticated": True,
        "icon": "fa fa-key",
        "display": "icon-name",
    },
    {
        "name": "Disable Account",
        "url": "userware:user_disable_account",
        "render_for_authenticated": True,
        "icon": "fa fa-trash",
        "display": "icon-name",
    },
]

SUBMENU_ACCOUNT_SETTINGS = [
    {
        "name": "Social Associations",
        "url": "profileware:account_settings_social",
        "render_for_authenticated": True,
        "render_for_user_when_condition_is_true": "profileware.utils.is_social_auth_enabled",
        "icon": "fa fa-group",
        "display": "icon-name",
    },
    {
        "name": "AdShare",
        "url": "adware:adsense_update",
        "render_for_authenticated": True,
        "icon": "fa fa-cart-plus",
        "display": "icon-name",
    },
    {
        "name": "Switch User",
        "url": "userware:user_switch_on",
        "render_for_authenticated": True,
        "render_for_superuser": True,
        "icon": "fa fa-user",
        "display": "icon-name",
    },
]

SUBMENU_ACCOUNT = [
    {
        "name": "Account",
        "url": "profileware:account_profile",
        "render_for_authenticated": True,
        "icon": "fa fa-user",
        "display": "name-icon",
        "submenu": SUBMENU_ACCOUNT_PROFILE,
    },
    {
        "name": "Settings",
        "url": "profileware:account_settings_social",
        "render_for_authenticated": True,
        "icon": "fa fa-cogs",
        "display": "name-icon",
        "submenu": SUBMENU_ACCOUNT_SETTINGS,
    },
    {
        "name": "Admin",
        "url": "/admino/",
        "render_for_authenticated": True,
        "render_for_staff": True,
        "icon": "fa fa-tasks",
    },
    {
        "name": "Logout",
        "url": "userware:user_logout",
        "render_for_authenticated": True,
        "icon": "fa fa-sign-out",
        "display": "name-icon",
        "tooltip": "Logout",
        "visibility": ["top-nav"],
        "separator": ["top"],
        "class": "text-danger",

    },
]

SUBMENU_PUBLISH_ARTICLES = [
    {
        "name": "Public Articles",
        "url": "articleware:article_public_list_view",
        "render_for_authenticated": True,
        "icon": "fa fa-newspaper-o",
        "display": "name-icon",
        "class": "text-success",
    },
    {
        "name": "Unlisted Articles",
        "url": "articleware:article_unlisted_list_view",
        "render_for_authenticated": True,
        "icon": "fa fa-chain",
        "display": "name-icon",
    },
    {
        "name": "Private Articles",
        "url": "articleware:article_private_list_view",
        "render_for_authenticated": True,
        "icon": "fa fa-eye-slash",
        "display": "name-icon",
    },
    {
        "name": "Archived Articles",
        "url": "articleware:article_archived_list_view",
        "render_for_authenticated": True,
        "icon": "fa fa-archive",
        "display": "name-icon",
    },
    {
        "name": "Add Article",
        "url": "articleware:article_add",
        "render_for_authenticated": True,
        "icon": "fa fa-plus",
        "display": "icon-name",
        "class": "brown bold",
        "separator": ["top"],
    },
]

SUBMENU_PUBLISH_BLOGS = [
    {
        "name": "Blog Posts",
        "url": "articleware:article_blog_list_view",
        "render_for_authenticated": True,
        "icon": "fa fa-rss-square",
        "display": "name-icon",
    },
    {
        "name": "Add Blog Post",
        "url": "articleware:article_blog_add",
        "render_for_authenticated": True,
        "icon": "fa fa-plus",
        "display": "icon-name",
        "class": "brown bold",
        "separator": ["top"],
    },
]


SUBMENU_PUBLISH_PAGES = [
    {
        "name": "Flat Pages",
        "url": "articleware:article_page_list_view",
        "render_for_authenticated": True,
        "icon": "fa fa-file-text-o",
        "display": "name-icon",
    },
    {
        "name": "Add Flat Page",
        "url": "articleware:article_page_add",
        "render_for_authenticated": True,
        "icon": "fa fa-plus",
        "display": "icon-name",
        "class": "brown bold",
        "separator": ["top"],
    },
]

SUBMENU_PUBLISH = [
    {
        "name": "Articles",
        "url": "articleware:article_public_list_view",
        "render_for_authenticated": True,
        "icon": "fa fa-list-alt",
        "display": "name-icon",
        "submenu": SUBMENU_PUBLISH_ARTICLES,
    },
    {
        "name": "Blog Posts",
        "url": "articleware:article_blog_list_view",
        "render_for_authenticated": True,
        "render_for_user_when_condition_is_true": 'articleware.utils.is_article_blog_admin',
        "icon": "fa fa-rss-square",
        "display": "name-icon",
        "submenu": SUBMENU_PUBLISH_BLOGS,
    },
    {
        "name": "Flat Pages",
        "url": "articleware:article_page_list_view",
        "render_for_authenticated": True,
        "render_for_user_when_condition_is_true": 'articleware.utils.is_article_page_admin',
        "icon": "fa fa-file-text-o",
        "display": "name-icon",
        "submenu": SUBMENU_PUBLISH_PAGES,
    },
    {
        "name": "Get Approved",
        "url": "portal:approval_confirmation_view",
        "render_for_authenticated": True,
        "render_for_user_when_condition_is_false": 'articleware.utils.is_approved_writer',
        "icon": "fa fa-thumbs-o-up",
        "separator": ["top"],
        "class": "text-success",
    },
]

MENUWARE_MENU = {

    "LEFT_NAV_MENU": [
        {
            "name": "Featured",
            "url": "portal:article_featured_view",
            "render_for_unauthenticated": True,
            "render_for_authenticated": True,
            "icon": "fa fa-check",
            # "display": "name-only",
        },
        {
            "name": "Popular",
            "url": "portal:article_popular_view",
            "render_for_unauthenticated": True,
            "render_for_authenticated": True,
            "icon": "fa fa-star",
            # "display": "name-only",
        },
        {
            "name": "Latest",
            "url": "portal:article_latest_view",
            "render_for_unauthenticated": True,
            "render_for_authenticated": True,
            "icon": "fa fa-clock-o",
            # "display": "name-only",
        },
    ],
    "RIGHT_NAV_MENU": [
        {
            "name": "Publish",
            "url": "articleware:article_public_list_view",
            "render_for_authenticated": True,
            "icon": "fa fa-pencil",
            "display": "name-icon",
            # "tooltip": "Publish",
            "submenu": SUBMENU_PUBLISH,
        },
        {
            "name": "Account",
            "url": "profileware:account_index",
            "render_for_authenticated": True,
            "icon": "fa fa-user",
            "display": "icon-only",
            # "tooltip": "Account",
            "submenu": SUBMENU_ACCOUNT,
        },
        {
            "name": "Login",
            "url": "userware:user_login",
            "render_for_unauthenticated": True,
            "icon": "fa fa-sign-out fa-rotate-180",
            "display": "name-only",
            "href_attrs": {"rel": "nofollow,noindex"}
        },
    ],
}

FOOTER_MENU_COMPANY = [
    {
        "name": "Terms & Conditions",
        "url": "/site/terms-conditions",
        "render_for_authenticated": True,
        "render_for_unauthenticated": True,
        "icon": "fa fa-file-text-o",
    },
    {
        "name": "Privacy Policy",
        "url": "/site/privacy-policy",
        "render_for_authenticated": True,
        "render_for_unauthenticated": True,
        "icon": "fa fa-file-text-o",
    },
    {
        "name": "Contact Us",
        "url": "contactware:contactware_form_view",
        "render_for_authenticated": True,
        "render_for_unauthenticated": True,
        "icon": "fa fa-envelope-o",
    },
]

FOOTER_MENU_SOCIAL = [
    {
        "name": "Facebook",
        "url": "https://www.facebook.com/brevitypress",
        "render_for_authenticated": True,
        "render_for_unauthenticated": True,
        "icon": "fa fa-facebook-square",
    },
    {
        "name": "Twitter",
        "url": "https://twitter.com/brevitypub",
        "render_for_authenticated": True,
        "render_for_unauthenticated": True,
        "icon": "fa fa-twitter-square",
    },
    {
        "name": "Blog",
        "url": "portal:article_blog_view",
        "render_for_authenticated": True,
        "render_for_unauthenticated": True,
        "icon": "fa fa-rss-square",
    },
]

FOOTER_MENU_SEARCH = [
    {
        "name": "Featured",
        "url": "portal:article_featured_view",
        "render_for_authenticated": True,
        "render_for_unauthenticated": True,
        "icon": "fa fa-check",
    },
    {
        "name": "Popular",
        "url": "portal:article_popular_view",
        "render_for_authenticated": True,
        "render_for_unauthenticated": True,
        "icon": "fa fa-star",
    },
    {
        "name": "Latest",
        "url": "portal:article_latest_view",
        "render_for_authenticated": True,
        "render_for_unauthenticated": True,
        "icon": "fa fa-clock-o",
    },
]
