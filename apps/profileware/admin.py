from django import forms
from django.contrib import admin
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model

from .forms import UserProfileCreationForm
from .forms import UserProfileChangeAdminForm
from .models import UserProfile
from .models import Track


class UserProfileAdmin(UserAdmin):
    fieldsets = (
        (_('Required Info'), {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'username',
                                         'bio', 'public_email', 'website', 'location', 'company')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'created_on')}),
        (_('Other'), {'fields': ('photo', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser',
        'username', 'created_on', 'last_login',)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('id', 'first_name', 'last_name', 'email', 'username', 'public_email',
        'location',)
    ordering = ('email', 'id',)
    filter_horizontal = ('groups', 'user_permissions',)

    form = UserProfileChangeAdminForm
    add_form = UserProfileCreationForm

    def get_urls(self):
        return [
            url(
                r'^(.+)/change/password/$',
                self.admin_site.admin_view(self.user_change_password),
                name='auth_user_password_change',
            ),
        ] + super(UserAdmin, self).get_urls()

try:
    admin.site.unregister(get_user_model())
except NotRegistered:
    pass
admin.site.register(UserProfile, UserProfileAdmin)


class TrackAdmin(admin.ModelAdmin):
    list_display = ["id", "profile", "view", "star", "updated_at"]
admin.site.register(Track, TrackAdmin)
