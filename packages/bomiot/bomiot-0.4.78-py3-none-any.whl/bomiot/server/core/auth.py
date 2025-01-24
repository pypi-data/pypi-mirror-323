from rest_framework.exceptions import APIException
from .jwt_auth import parse_payload
from django.contrib.auth import get_user_model

User = get_user_model()

class CoreAuthentication(object):
    def authenticate(self, request) -> tuple[User, bool]:
        if request.path in ['/', '/api/docs/', '/api/debug/', '/api/']:
            return (False, None)
        else:
            token = request.META.get('HTTP_TOKEN', '')
            result = parse_payload(token)
            if token:
                try:
                    user_data = User.objects.get(id=int(result.get('data', '').get('id', '')))
                    return (True, user_data)
                except:
                    raise APIException({"msg": "User Does Not Exists"})
            else:
                raise APIException({"msg": "Please Login First"})

    def authenticate_header(self, request):
        pass
