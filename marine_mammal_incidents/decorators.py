from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def superuser_or_data_curator_required(view_func):
    def check_perms(user):
        if user.is_superuser or user.groups.filter(name='data curator').exists() or user.groups.filter(name='MARINE_ANIMAL_INCIDENTS').exists():
            return True
        raise PermissionDenied
    return user_passes_test(check_perms)(view_func)