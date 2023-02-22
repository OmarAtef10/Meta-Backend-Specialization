from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group, User
from rest_framework import exceptions


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        curr_user = User.objects.get(username=request.user.username)
        return curr_user.is_superuser


class IsManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        curr_user = User.objects.get(username=request.user.username)
        return curr_user.groups.filter(name='Manager').exists() or curr_user.is_superuser


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        curr_user = User.objects.get(username=request.user.username)
        return curr_user.groups.filter(name='Delivery Crew').exists() or curr_user.is_superuser


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        curr_user = User.objects.get(username=request.user.username)
        return curr_user.groups.filter(name='Manager').exists() or curr_user.groups.filter(
            name='Delivery Crew').exists()


class NonManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()

        if (request.method == "GET"):
            return True

        curr_user = User.objects.get(username=request.user.username)
        return not curr_user.groups.filter(name='Manager').exists() or curr_user.is_superuser
