from vertex.models import AbstractDatedModel
from netfields import MACAddressField



class MACAddress(AbstractDatedModel):

    address = MACAddressField()