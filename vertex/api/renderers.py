from django.conf import settings
from django.utils import encoding

from vertex import tasks
from rest_framework_json_api.renderers import JSONRenderer


class BindingJSONAPIRenderer(JSONRenderer):
    format = 'jsonapi'

    def __init__(self):
        super(BindingJSONAPIRenderer, self).__init__()
        self.request_wsid = None

    def render(self, data, accepted_media_type=None, renderer_context=None):
        try:
            payload = renderer_context.get("request", None).user.jwt_payload
        except AttributeError:
            pass
        else:
            self.request_wsid = payload.get('wsid')
        return super(BindingJSONAPIRenderer, self).render(data, accepted_media_type, renderer_context)

    def build_json_resource_obj(self, fields, resource, resource_instance, resource_name):
        if self.request_wsid:
            routing_key = '{type}.{id}'.format(
                type=resource_name,
                id=encoding.force_text(resource_instance.pk)
            )
            queue = 'ws.' + encoding.force_text(self.request_wsid)
            kwargs = {'queue': queue, 'exchange': settings.WS_EXCHANGE, 'routing_key': routing_key}
            tasks.amqp_queue_bind.delay(kwargs)

        return JSONRenderer.build_json_resource_obj(fields, resource, resource_instance, resource_name)
