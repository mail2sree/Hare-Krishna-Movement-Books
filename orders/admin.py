from django.contrib import admin
from .models import*

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'full_address', 'phone', 'email', 'razorpay_order_id', 'is_ordered', 'order_id', 'ip', 'status', 'created_at']
    list_filter = ['status', 'is_ordered']
    list_per_page = 20
    inlines = [OrderProductInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)
admin.site.index_title = 'HKM BOOKS'
admin.site.site_title = 'HKM BOOKS'
admin.site.site_header = 'HKM BOOKS'