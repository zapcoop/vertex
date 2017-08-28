from rest_framework_json_api import serializers


class FilterRelatedMixin(object):
    def __init__(self, *args, **kwargs):
        super(FilterRelatedMixin, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, serializers.RelatedField) or isinstance(field, serializers.ManyRelatedField):
                method_name = 'filter_%s' % name
                try:
                    func = getattr(self, method_name)
                except AttributeError:
                    pass
                else:
                    if not isinstance(field, serializers.ManyRelatedField):
                        field.queryset = func(field.queryset)
                    else:
                        field.child_relation.queryset = func(field.child_relation.queryset)


class ValidationMixin(object):
    def validate(self, attributes):
        instance = self.Meta.model(**attributes)
        instance.clean()
        return attributes
