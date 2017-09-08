from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from contacts.viewsets import DepartmentViewSet

from .viewsets import (
    TicketViewSet,
    UpdateViewSet,
    NoteViewSet,
    TeamViewSet,
    TicketSubscriberViewSet
)

from .views import CloseTicketView, UpdateRelationshipView, TicketRelationshipView, TeamRelationshipView

router = DefaultRouter(trailing_slash=False)

router.register(r'tickets', TicketViewSet)
router.register(r'updates', UpdateViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'subscribers', TicketSubscriberViewSet)

ticket_update_router = NestedSimpleRouter(router, r'tickets', lookup='ticket', trailing_slash=False)
ticket_update_router.register(r'updates', UpdateViewSet, base_name='ticket-updates')

update_note_router = NestedSimpleRouter(router, r'updates', lookup='update', trailing_slash=False)
update_note_router.register(r'notes', NoteViewSet, base_name='update-notes')

team_router = NestedSimpleRouter(router, r'teams', lookup='team', trailing_slash=False)
team_router.register(r'departments', DepartmentViewSet, base_name='team-departments')

urlpatterns = (router.urls + ticket_update_router.urls + update_note_router.urls +
               team_router.urls + [
                   url(r'tickets/(?P<pk>[^/.]+)/close$', CloseTicketView.as_view(), name='ticket-close'),
                   url('updates/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
                       UpdateRelationshipView.as_view(), name='update-relationships'),
                   url('tickets/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
                       UpdateRelationshipView.as_view(), name='ticket-relationships'),
                   url(r'teams/(?P<pk>[^/.]+)/relationships/(?P<related_field>[^/.]+)$',
                       TeamRelationshipView.as_view(), name='team-relationships'),
               ])
