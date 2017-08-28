from rest_framework.permissions import DjangoObjectPermissions, BasePermission
from django_otp import user_has_device
from noss.settings import app_settings


class RestrictedObjectLevelPermissions(DjangoObjectPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_object_permission(self, request, view, obj):
        try:
            queryset = view.get_queryset()
        except AttributeError:
            queryset = getattr(view, 'queryset', None)

        assert queryset is not None, (
            'Cannot apply DjangoObjectPermissions on a view that '
            'does not have `.queryset` property or overrides the '
            '`.get_queryset()` method.')

        model_cls = queryset.model
        user = request.user

        perms = self.get_required_object_permissions(request.method, model_cls)

        if not user.has_perms(perms, obj):
            return False

        if not getattr(view, 'verification_exempt', False):
            return self.check_verified_status(user)

        return True

    def check_verified_status(self, user):
        if user.is_staff:
            return getattr(user, 'is_verified', False) or app_settings.ALLOW_UNVERIFIED_STAFF
        else:
            return (not user_has_device(user, confirmed=True)) or getattr(user, 'is_verified', False)


class IsSuperUser(BasePermission):
    """
    Allows access only to superusers.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser