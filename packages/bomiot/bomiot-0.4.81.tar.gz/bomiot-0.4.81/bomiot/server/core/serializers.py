from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, required=False)
    email = serializers.CharField(read_only=True, required=False)
    phone = serializers.CharField(read_only=True, required=False)
    permission = serializers.JSONField(read_only=True, required=False)
    request_limit = serializers.IntegerField(read_only=True, required=False)
    is_active = serializers.BooleanField(read_only=True, required=False)
    date_joined = serializers.DateTimeField(read_only=True, required=False, format='%Y-%m-%d %H:%M:%S')
    last_login = serializers.DateTimeField(read_only=True, required=False, format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True, required=False, format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'is_active', 'request_limit', 'permission', 'date_joined', 'last_login', 'updated_time']
        read_only_fields = ['id']
