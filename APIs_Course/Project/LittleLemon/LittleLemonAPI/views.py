from djoser.conf import User
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.generics import ListCreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from .models import Category, MenuItem, Cart, Order, OrderItem, CartItem
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, \
    CartItemSerializer, UserSerializer
from .permissions import IsManager, IsStaff, NonManager, IsSuperUser, IsDeliveryCrew

from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter


# Create your views here.
class GetMenuItems(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = PageNumberPagination
    ordering_fields = ['price']
    search_fields = ['category__title', 'title']


@api_view(['GET'])
@permission_classes([NonManager])
def get_menu_item(request, pk):
    if request.method == "GET":
        item = get_object_or_404(MenuItem, pk=pk)
        menu_item = MenuItemSerializer(item)
        return Response(menu_item.data, status=200)


@api_view(["PUT", "DELETE"])
@permission_classes([IsManager])
def manage_menu_item(request, pk):
    if request.method == "PUT":
        item = get_object_or_404(MenuItem, pk=pk)
        serializer = MenuItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    if request.method == "DELETE":
        item = get_object_or_404(MenuItem, pk=pk)
        MenuItem.delete(item)
        return Response({"Message": "Item Deleted Successfully"}, status=200)


@api_view(["POST"])
@permission_classes([IsManager])
def create_menu_item(request):
    serializer = MenuItemSerializer(data=request.data)
    category = get_object_or_404(Category, id=request.data["category"])
    if serializer.is_valid():
        serializer.category = category
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsSuperUser])
def list_managers(request):
    if request.method == "GET":
        managers = User.objects.filter(groups__name='Manager')
        managers_list = UserSerializer(managers, many=True)
        return Response(managers_list.data, status=200)


@api_view(["POST", "DELETE"])
@permission_classes([IsSuperUser])
def manage_managers(request, username):
    if request.method == "POST":
        manager = get_object_or_404(User, username=username)
        manager.groups.add(1)
        return Response({"Message": "Manager Added Successfully"}, status=200)
    if request.method == "DELETE":
        manager = get_object_or_404(User, username=username)
        manager.groups.remove(1)
        return Response({"Message": "Manager Removed Successfully"}, status=200)


@api_view(["GET"])
@permission_classes([IsManager])
def list_delivery_crew(request):
    if request.method == "GET":
        managers = User.objects.filter(groups__name='Delivery Crew')
        managers_list = UserSerializer(managers, many=True)
        return Response(managers_list.data, status=200)


@api_view(["POST", "DELETE"])
@permission_classes([IsManager])
def manage_delivery_crew(request, username):
    if request.method == "POST":
        manager = get_object_or_404(User, username=username)
        manager.groups.add(2)
        return Response({"Message": "Delivery Crew Added Successfully"}, status=200)
    if request.method == "DELETE":
        manager = get_object_or_404(User, username=username)
        manager.groups.remove(2)
        return Response({"Message": "Delivery Crew Removed Successfully"}, status=200)


class CartView(ListCreateAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CartSerializer
        return CartItemSerializer

    def get(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        if cart.exists():
            cart = CartSerializer(cart[0])
            return Response(cart.data, status=200)
        else:
            cart = Cart.objects.create(user=request.user)
            return Response({"Message": "Cart Does Not Exist , we will create one for you"}, status=400)

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        if cart.exists():
            cart = cart[0]
            quantity = request.data["quantity"]
            item = request.data["menuitem"]
            item = get_object_or_404(MenuItem, pk=item)
            cart_item = CartItem(cart=cart, menuitem=item, quantity=quantity)
            carts = CartItemSerializer(cart_item)
            cart_item.save()
            # converting cart_item to dictionary
            return Response(carts.data, status=status.HTTP_200_OK)

        else:
            cart = Cart(user=request.user)
            cart.save()
            serializer = CartItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

    def delete(self, request, *args, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response({"Message": "Cart Cleared Successfully"}, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def submit_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    order = Order.objects.create(user=request.user)
    for cart_item in cart_items:
        order_item = OrderItem.objects.create(order=order, menuitem=cart_item.menuitem, quantity=cart_item.quantity)
    serializer = OrderSerializer(order)
    cart.delete()
    return Response({"Message": "Order Submitted Successfully", "Order": serializer.data}, status=200)


class OrderView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['orderTotal']
    search_fields = ["id"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        price = self.request.query_params.get('orderTotal', None)
        if price is not None:
            queryset = queryset.filter(orderTotal=price)
        return queryset

    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(user=request.user)
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsManager])
def assign_delivery(request, order_id, username):
    order = get_object_or_404(Order, pk=order_id)
    if order.status != 0:
        return Response({"Message": "Order Already Delivered"}, status=400)
    user = get_object_or_404(User, username=username)
    if not user.groups.filter(name='Delivery Crew').exists():
        return Response({"Message": "User is not a Delivery Crew"}, status=400)
    order.delivery_crew = user
    order.save()
    return Response({"Message": "Delivery Assigned Successfully"}, status=200)


@api_view(["GET"])
@permission_classes([IsDeliveryCrew])
def deliver_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.delivery_crew != request.user:
        return Response({"Message": "You are not assigned to this order"}, status=400)
    if order.status != 0:
        return Response({"Message": "Order Already Delivered"}, status=400)
    order.status = 1
    order.save()
    return Response({"Message": "Order Delivered Successfully"}, status=200)
