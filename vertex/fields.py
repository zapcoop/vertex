from autoslug import AutoSlugField, utils

from vertex.utils import generate_unique_slug


class AutoReferenceField(AutoSlugField):
    def pre_save(self, instance, add):

        # get currently entered slug
        value = self.value_from_object(instance)

        manager = self.manager

        # autopopulate
        if self.always_update or (self.populate_from and not value):
            value = utils.get_prepopulated_value(self, instance)

            # pragma: nocover
            if __debug__ and not value and not self.blank:
                print('Failed to populate slug %s.%s from %s' % \
                      (instance._meta.object_name, self.name, self.populate_from))

        if value:
            slug = self.slugify(value)
        else:
            slug = None

            if not self.blank:
                slug = instance._meta.model_name
            elif not self.null:
                slug = ''

        if not self.blank:
            assert slug, 'slug is defined before trying to ensure uniqueness'

        if slug:
            slug = utils.crop_slug(self, slug)

            # ensure the slug is unique (if required)
            if self.unique or self.unique_with:
                slug = generate_unique_slug(self, instance, slug, manager)

            assert slug, 'value is filled before saving'

        # make the updated slug available as instance attribute
        setattr(instance, self.name, slug)

        return slug