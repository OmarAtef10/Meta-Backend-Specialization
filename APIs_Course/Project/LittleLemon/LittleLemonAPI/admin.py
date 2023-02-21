from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem

# Register your models here.


class Category_admin(admin.ModelAdmin):
    readonly_fields = ('id', 'slug')


admin.site.register(Category, Category_admin)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
