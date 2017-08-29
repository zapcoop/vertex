from django.contrib.auth.models import User, Group, Permission
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
import django_otp
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework import mixins

from vertex.api.permissions import IsSuperUser
from .serializers import UserSerializer, GroupSerializer, PermissionSerializer,\
    TOTPDeviceSerializer, PasswordSerializer, TOTPTokenSerializer, StaticTokenSerializer


class UserViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = (IsAuthenticated, IsSuperUser)

    @detail_route(methods=['post'])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['password'])
            user.save()
            return Response({'status': _('password set')})
        else:
            return Response(serializer.errors,
                            status=HTTP_400_BAD_REQUEST)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    permission_classes = (IsAuthenticated, IsSuperUser)


class PermissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    permission_classes = (IsAuthenticated, IsSuperUser)


class TOTPDeviceViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    API endpoint that allows TOTP Device keys to be viewed, deleted or confirmed.
    """
    serializer_class = TOTPDeviceSerializer

    def get_queryset(self):
        return TOTPDevice.objects.filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
        if not StaticDevice.objects.filter(user=self.request.user).exists():
            static_device = StaticDevice.objects.create(
                user=self.request.user,
                name=self.request.username
            )
            generate_new_recovery_codes(static_device)

    @detail_route(methods=['post'])
    def confirm(self, request, **kwargs):
        device = self.get_object()
        user = request.user
        serializer = TOTPTokenSerializer(
            device=device,
            user=user,
            data=request.data,
            context=self.get_serializer_context()
        )
        if serializer.is_valid():
            device.confirmed = True
            device.save()
            return Response({'status': _('TOTP Device confirmed')})
        else:
            return Response(serializer.errors,
                            status=HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def verify_session(self, request, **kwargs):
        device = self.get_object()
        user = request.user
        serializer = TOTPTokenSerializer(device=device, user=user, data=request.data)
        if serializer.is_valid():
            django_otp.login(request, device)
            return Response({'status': _('User verified')})
        else:
            return Response(serializer.errors,
                            status=HTTP_400_BAD_REQUEST)


class RecoveryCodeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = StaticTokenSerializer
    resource_name = 'recovery_code'

    def get_queryset(self):
        return StaticToken.objects.filter(device__user=self.request.user)

    @list_route(methods=['post'])
    def generate(self, request, *args, **kwargs):
        """Generate a new set of ten recovery codes. This will permanently invalidate
        the existing codes."""
        device = self.request.user.staticdevice_set.first()
        generate_new_recovery_codes(device)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


def generate_new_recovery_codes(static_device):
    static_device.token_set.all().delete()
    tokens = list()
    for i in range(10):
        tokens.append(StaticToken(device=static_device, token=StaticToken.random_token()))
    StaticToken.objects.bulk_create(tokens)
