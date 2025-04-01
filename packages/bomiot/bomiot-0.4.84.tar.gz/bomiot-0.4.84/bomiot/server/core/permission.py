from django.contrib.auth import get_user_model
from bomiot.server.core.utils import contains_value
import tomllib


User = get_user_model()


class CorePermission:
    def has_permission(self, request, view) -> bool:
        user_permission = request.auth.permission
        if request.user:
            return contains_value(user_permission, request.path)
        else:
            return False
        # return bool(request.user and request.user.is_authenticated)