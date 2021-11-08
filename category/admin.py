from django.contrib import admin
from .models import Category

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'slug')
    prepopulated_fields = {'slug': ('category',)}
admin.site.register(Category, CategoryAdmin)
admin.site.index_title = 'HKM BOOKS'
admin.site.site_title = 'HKM BOOKS'
admin.site.site_header = 'HKM BOOKS'