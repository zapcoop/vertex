"""noss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
"""
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views.i18n import javascript_catalog
from rest_framework.routers import DefaultRouter

from noss.api import viewsets as noss_viewsets
from noss.api.apiviews import (CurrentUserView, CurrentUserPasswordChangeView,
                               ObtainJSONWebTokenView, CurrentUserSetPrimaryEmailView,
                               RefreshJSONWebTokenView)

router = DefaultRouter(trailing_slash=False)

router.register(r'users', noss_viewsets.UserViewSet)
router.register(r'groups', noss_viewsets.GroupViewSet)
router.register(r'permissions', noss_viewsets.PermissionViewSet)
router.register(r'totp_devices', noss_viewsets.TOTPDeviceViewSet, base_name='totpdevice')
router.register(r'recovery_codes', noss_viewsets.RecoveryCodeViewSet, base_name='recovery_code')

js_info_dict = {
    'packages': (
        'contacts',),
}

urlpatterns = [
    url(r'^api/auth/', include(router.urls)),
    url(r'^api/contacts/', include('contacts.urls')),
    url(r'^api/service/', include('service.urls')),
    url(r'^api/contracts/', include('contracts.urls')),
    url(r'^api/tags/', include('tags.urls')),
    url(r'^files/contracts/', include('contracts.fileurls')),
    url(r'^api/ipam/', include('ipam.urls')),
    url(r'^api/me$', CurrentUserView.as_view()),
    url(r'^api/me/change_password$', CurrentUserPasswordChangeView.as_view()),
    url(r'^api/me/set_primary_email$', CurrentUserSetPrimaryEmailView.as_view()),
    url(r'^api-auth$', ObtainJSONWebTokenView.as_view()),
    url(r'^api-auth/refresh', RefreshJSONWebTokenView.as_view()),
    url(r'^api-auth/verify', 'rest_framework_jwt.views.verify_jwt_token'),
    # url(r'^api-auth/add-totp', 'some view must be created'),
    url(r'^drf-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [url(r'__debug__/', include(debug_toolbar.urls))]
