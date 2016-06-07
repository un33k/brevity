from django.contrib import admin

from .models import CommentCode


class CommentCodeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "active", "code", "updated_at"]
admin.site.register(CommentCode, CommentCodeAdmin)
