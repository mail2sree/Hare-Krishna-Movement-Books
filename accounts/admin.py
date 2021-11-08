from django.contrib import admin
from .models import Account, MyAccountManager
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ['first_name', 'last_name', 'username', 'email', 'last_login', 'is_active', 'date_joined']
    list_display_links = ['email', 'first_name', 'last_name', 'username']
    readonly_fields = ['last_login', 'date_joined']
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()    
admin.site.register(Account, AccountAdmin)
admin.site.index_title = 'HKM BOOKS'
admin.site.site_title = 'HKM BOOKS'
admin.site.site_header = 'HKM BOOKS'