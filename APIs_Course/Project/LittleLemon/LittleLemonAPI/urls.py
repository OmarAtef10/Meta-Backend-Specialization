from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('menu-items/', views.get_all_menu_items, name='menu'),
    path('menu-items/<int:pk>/', views.get_menu_item, name='menu-item'),
    path('menu-items/manage/<int:pk>/', views.manage_menu_item, name='manage-menu-item'),
    path('menu-items/create/', views.create_menu_item, name='create-menu-item'),
    path('groups/managers/users', views.list_managers, name='manage-managers'),
    path('groups/managers/users/<str:username>', views.manage_managers, name='manage-managers'),
    path('groups/delivery-crew/users', views.list_delivery_crew, name='manage-managers'),
    path('groups/delivery-crew/users/<str:username>', views.manage_delivery_crew, name='manage-managers'),

    path('api-token/', obtain_auth_token, name='token'),
]
