from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem


# Register your models here.


class Category_admin(admin.ModelAdmin):
    readonly_fields = ('id', 'slug')


admin.site.register(Category, Category_admin)
admin.site.register(MenuItem)
admin.site.register(Cart)


class Order_admin(admin.ModelAdmin):
    readonly_fields = ('id', 'total')


admin.site.register(Order, Order_admin)


class OrderItem_admin(admin.ModelAdmin):
    readonly_fields = ('id', 'price', 'unit_price')


admin.site.register(OrderItem, OrderItem_admin)
