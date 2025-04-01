from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from functools import reduce

from .serializers import UserSerializer
from .filter import UserFilter
from.page import CorePageNumberPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Permission
from .message import message_return

from django.contrib.auth import get_user_model

User = get_user_model()


class UserPage(CorePageNumberPagination):

    def get_return_data(self, data):
        return { "label": data.name, "value": data.name }

    def query_data_add(self) -> list:
        permission_list = Permission.objects.all()
        data_list = list(map(lambda data: self.get_return_data(data), permission_list))
        return [
            ("permission", data_list)
        ]


class UserList(viewsets.ModelViewSet):
    """
        list:
            Response a user data list（all）
    """
    pagination_class = UserPage
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "created_time", "updated_time", ]
    filter_class = UserFilter

    def get_project(self):
        try:
            data_id = self.kwargs.get('pk')
            return data_id
        except:
            return None

    def get_queryset(self):
        data_id = self.get_project()
        if self.request.user:
            if data_id is None:
                return User.objects.filter(openid=self.request.auth.openid, is_delete=False)
            else:
                return User.objects.filter(openid=self.request.auth.openid, id=data_id, is_delete=False)
        else:
            return User.objects.none()

    def get_serializer_class(self):
        if self.action in ['list']:
            return UserSerializer
        else:
            return self.http_method_not_allowed(request=self.request)


class PermissionList(viewsets.ModelViewSet):
    """
        list:
            Response a permission data list（all）
    """
    queryset = Permission.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "created_time", "updated_time", ]


class UserCreate(viewsets.ModelViewSet):
    """
        create:
            create a user
    """
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "created_time", "updated_time", ]
    filter_class = UserFilter

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, **kwargs):
        data = self.request.data
        print(data)
        return Response(data, status=200)


class UserPermission(viewsets.ModelViewSet):
    """
        create:
            Set permission for user
    """
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "created_time", "updated_time", ]
    filter_class = UserFilter

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def get_permission_data(self, data):
        permission_data = Permission.objects.filter(name=data).first()
        return {
            permission_data.name: permission_data.api
        }

    def create(self, request, **kwargs):
        data = self.request.data
        message_return('1', '2')
        permission_list = data.get('permission')
        data_list = list(map(lambda data: self.get_permission_data(data), permission_list))
        permission_data = reduce(lambda x, y: {**x , **y}, data_list)
        user_data = User.objects.filter(id=data.get('id')).first()
        user_data.permission = permission_data
        user_data.save()
        return Response({'extra': 'Success Change User Permission'}, status=200)


class UserChangePWD(viewsets.ModelViewSet):
    """
        create:
            Change Password
    """
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "created_time", "updated_time", ]
    filter_class = UserFilter

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, **kwargs):
        data = self.request.data
        user_data = User.objects.filter(id=data.get('id')).first()
        user_data.set_password(str(data.get('pwd')))
        user_data.save()
        return Response({'extra': 'Success Change Password'}, status=200)


class UserLock(viewsets.ModelViewSet):
    """
        create:
            Delete one User
    """
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "created_time", "updated_time", ]
    filter_class = UserFilter

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, **kwargs):
        data = self.request.data
        user_data = User.objects.filter(id=data.get('id')).first()
        if user_data.is_superuser:
            raise APIException('Can not lock superuser')
        else:
            if user_data.is_active is True:
                user_data.is_active = False
                user_data.save()
                return Response({'extra': f'Success unlock User {user_data.username}'}, status=200)
            else:
                user_data.is_active = True
                user_data.save()
                return Response({'extra': f'Success lock User {user_data.username}'}, status=200)


class UserDelete(viewsets.ModelViewSet):
    """
        create:
            Delete one User
    """
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "created_time", "updated_time", ]
    filter_class = UserFilter

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, **kwargs):
        data = self.request.data
        user_data = User.objects.filter(id=data.get('id')).first()
        if user_data.is_superuser:
            raise APIException('Can not delete superuser')
        else:
            user_data.is_delete = True
            user_data.save()
            return Response({'extra': f'Success delete User {user_data.username}'}, status=200)