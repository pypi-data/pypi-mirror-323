from django_filters import CharFilter
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from  django.db.models import JSONField


User = get_user_model()


class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = '__all__'
        filter_overrides = {
            JSONField: {
                'filter_class': CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'exact',
                },
            }
        }