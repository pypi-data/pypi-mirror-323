from django.contrib import admin
from .models import UnauthorizedAccessAttempt


@admin.register(UnauthorizedAccessAttempt)
class UnauthorizedAccessAttemptAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'attempt_time')
    list_filter = ('attempt_time', )
    search_fields = ('ip_address', 'prefer_languages', 'os', 'browser')