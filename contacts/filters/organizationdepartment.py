from noss.filters import IdListFilterSet
from ..models import OrganizationDepartment


class OrganizationDepartmentFilterSet(IdListFilterSet):

    class Meta:
        model = OrganizationDepartment
