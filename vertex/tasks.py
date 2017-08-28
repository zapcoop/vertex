import json

import amqp
from celery import Task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.conf import settings
from rest_framework.serializers import ModelSerializer

from noss.celery import app
from rest_framework_json_api import utils
from rest_framework_json_api.renderers import JSONRenderer

logger = get_task_logger(__name__)


class AMQPTask(Task):
    abstract = True
    _conn = None
    _exchange = None

    @property
    def connection(self):
        if self._conn is None:
            logger.info('No AMQP connection found, establishing connection...')
            self._conn = amqp.Connection(**settings.WS_AMQP_CONNECTION)
            logger.info('Connection to AMQP established!')
        return self._conn


@app.task(bind=True, base=AMQPTask, ignore_result=True)
def amqp_queue_bind(self, kwargs):
    channel = amqp.Channel(self.connection)
    try:
        channel.queue_bind(**kwargs)
    except amqp.IrrecoverableChannelError as e:
        logger.error(e)
    channel.close()


@app.task(bind=True, base=AMQPTask, ignore_result=True)
def amqp_queue_declare(self, kwargs):
    channel = amqp.Channel(self.connection)
    try:
        channel.queue_declare(**kwargs)
    except amqp.IrrecoverableChannelError as e:
        logger.error(e)
    channel.close()


@app.task(bind=True, base=AMQPTask, ignore_result=True)
def amqp_basic_publish(self, kwargs):
    if isinstance(kwargs['msg'], str):
        kwargs['msg'] = amqp.Message(body=kwargs['msg'], content_type='application/vnd+api.json')
    channel = amqp.Channel(self.connection)
    channel.basic_publish(**kwargs)
    channel.close()


@app.task()
def prepare_model_instance_data(pointer):
    ModelClass = apps.get_model(*pointer[0])
    instance = ModelClass.objects.get(pk=pointer[1])

    class SerializerFactory(ModelSerializer):
        class Meta:
            model = ModelClass

    serializer_class = SerializerFactory
    serialized_model_instance = serializer_class(instance)
    fields = utils.get_serializer_fields(serialized_model_instance)
    data = serialized_model_instance.data
    resource_instance = instance
    resource_name = utils.get_resource_type_from_instance(instance)
    json_api_data = JSONRenderer.build_json_resource_obj(fields, data, resource_instance, resource_name)
    return json_api_data


@app.task
def prepare_serialized_update(data, update_type):
    routing_key = '{type}.{id}'.format(
        type=data.get('type'),
        id=data.get('id')
    )
    meta = ({utils.format_keys("update_type"): update_type})
    kwargs = {'msg': json.dumps({'data': data, 'meta': meta}),
              'exchange': settings.WS_EXCHANGE,
              'routing_key': routing_key}
    return kwargs
