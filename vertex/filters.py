import rest_framework_filters as filters


class IdListFilterSet(filters.FilterSet):
    id__in = filters.InSetNumberFilter(name='pk__in')

    class Meta:
        fields = ['pk']


def generate_id_list_filterset_for_model(model_class):

    name = model_class.__name__ + 'FilterSet'
    meta = type('Meta', (), {'model': model_class})
    return type(name, (IdListFilterSet, object,), {'Meta': meta})
