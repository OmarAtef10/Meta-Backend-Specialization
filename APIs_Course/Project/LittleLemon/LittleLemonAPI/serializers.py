from .models import Category, MenuItem, Cart, Order, OrderItem, CartItem
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category"]


class CartItemSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(read_only=True)
    quantity = serializers.IntegerField(min_value=1, max_value=10)
    total = serializers.DecimalField(read_only=True, max_digits=6, decimal_places=2)
    menuitem = serializers.PrimaryKeyRelatedField(required=True, queryset=MenuItem.objects.all())

    def save(self, userId):
        _item = self.validated_data['item']
        _quantity = self.validated_data['quantity']
        currentCart, _ = Cart.objects.get_or_create(user__id=userId)
        createdItem = CartItem(cart=currentCart, menuItem=_item, quantity=_quantity)
        createdItem.save()
        return createdItem

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'quantity', 'total', 'menuitem']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, source='cart')

    class Meta:
        model = Cart
        fields = ['user', 'cartTotal', 'items']


class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'price', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, source='order')

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'orderTotal', 'status']
