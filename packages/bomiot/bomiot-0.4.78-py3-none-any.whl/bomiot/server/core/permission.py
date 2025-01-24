from django.contrib.auth import get_user_model


User = get_user_model()

def contains_value(data: dict, value) -> bool:
    return value in data.values()


class CorePermission:
    def has_permission(self, request, view) -> bool:
        user_permission = request.auth.permission
        if request.user:
            return contains_value(user_permission, request.path)
        else:
            return False
        # return bool(request.user and request.user.is_authenticated)