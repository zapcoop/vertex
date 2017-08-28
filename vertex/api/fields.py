from rest_framework import fields

from noss.rules import perm_exists


class PermissionsField(fields.Field):
    """
    This is a field that can be used on a DRF model serializer class.
    Often a user interface needs to know what permissions a user has so that it can change the interface accordingly.
    This field will check for all permissions defined against `django-rules`  and create a dictionary
    of all permissions defined and whether the request's user currently has access or not.
    
    Other parameters:
    permissions: Add a list of strings here to specifically identify the permissions this looks up. If left as None
        then it will return the default CRUD permissions along with list and read and write.
    additional_permissions: Add a list of strings here to add on to the default permissions, without having to repeat them.
    
    The format for the permissions is the following: {app_label}.{permission}_{model_name}
    """

    default_permissions = ['view', 'add', 'change', 'delete']

    def __init__(self, permissions=None, additional_permissions=None, **kwargs):
        """See class description for parameters and usage"""

        self.permissions_map = {}
        self.permissions = self.default_permissions if (permissions is None) else permissions
        if additional_permissions is not None:
            self.permissions = self.permissions + additional_permissions

        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super(PermissionsField, self).__init__(**kwargs)

    def bind(self, field_name, parent):
        """
        Check the model attached to the serializer to see what permissions are defined and save them.
        """
        assert parent.Meta.model is not None, (
            "PermissionsField is used on '%s' without a model" % parent.__class__.__name__
        )

        for permission in self.permissions:
            permission_name = '{app_label}.{permission}_{model_name}'.format(
                app_label=parent.Meta.model._meta.app_label,
                permission=permission,
                model_name=parent.Meta.model._meta.model_name
            )
            assert perm_exists(permission_name), (
                "Permissions '%s' does not exist" % permission
            )
            self.permissions_map[permission] = permission_name

        super(PermissionsField, self).bind(field_name, parent)

    def to_representation(self, value):
        """
        Calls has_perm to defined permissions and formats the results into a dictionary.
        """
        results = {}
        request = self.context.get('request')
        if request is not None:
            user = request.user
            for permission, rule_name in self.permissions_map.items():
                results[permission] = user.has_perm(rule_name, value)

        return results
