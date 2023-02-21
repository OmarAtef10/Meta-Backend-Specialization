from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.shortcuts import get_object_or_404
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsManager, Is_Staff, NonManager


# Create your views here.


@api_view(['GET'])
@permission_classes([NonManager])
def get_all_menu_items(request):
    if request.method == "GET":
        items = MenuItem.objects.all()
        menu_items = MenuItemSerializer(items, many=True)
        return Response(menu_items.data, status=200)


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({'message': 'You found the secret!'}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def manager_secret(request):
    if request.user.groups.filter(name='Manager').exists():
        return Response({'message': 'You found the Manager secret!'}, status=200)

    return Response({'message': 'This is not the API you are looking for'}, status=403)
