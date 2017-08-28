from rest_framework.serializers import ModelSerializer

from service.models import TicketChange


class TicketChangeSerializer(ModelSerializer):
    class Meta:
        model = TicketChange
