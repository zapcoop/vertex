from collections import OrderedDict
import re
from django.conf import settings

try:
    from django.apps import apps
except ImportError:
    apps = False

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Info(object):
    """
    Info is a class that generates information to be consumed by an API endpoint
    It allows for multiple named information containers, which can be accessed using the get_dict helper function.
    Information loaded from the INSTALLED_APPS, inside a file named info.py.
    This file should import the Info & InfoItem classes and then call add_item:
        Info.add_item("main", InfoItem("My item",
                                       "My item data"))
    """
    items = {}
    sorted = {}
    loaded = False

    @classmethod
    def add_item(cls, name, item):
        """
        add_item adds InfoItems to the info identified by 'name'
        """
        if isinstance(item, InfoItem):
            if name not in cls.items:
                cls.items[name] = []
            cls.items[name].append(item)
            cls.sorted[name] = False

    @classmethod
    def load_info(cls):
        """
        load_info loops through INSTALLED_APPS and loads the info.py
        files from them.
        """

        # we don't need to do this more than once
        if cls.loaded:
            return

        # Fetch all installed app names
        app_names = settings.INSTALLED_APPS
        if apps:
            app_names = [app_config.name for app_config in apps.get_app_configs()]

        # loop through our INSTALLED_APPS
        for app in app_names:
            # skip any django apps
            if app.startswith("django."):
                continue

            info_module = '%s.info' % app
            try:
                __import__(info_module, fromlist=["info", ])
            except ImportError:
                logger.warning("Couldn't import '%s'" % info_module)

        cls.loaded = True

    @classmethod
    def sort_info(cls):
        """
        sort_info goes through the items and sorts them based on
        their title
        """
        for name in cls.items:
            if not cls.sorted[name]:
                cls.items[name].sort(key=lambda x: x.title)
                cls.sorted[name] = True

    @classmethod
    def process(cls, context, name=None):
        """
        process uses the current context to determine which info
        should be visible, etc.
        """
        # make sure we're loaded & sorted
        cls.load_info()
        cls.sort_info()

        if name is None:
            # special case, process all info
            items = {}
            for name in cls.items:
                items[name] = cls.process(context, name)
            return items

        if name not in cls.items:
            return []

        for item in cls.items[name]:
            item.process(context)

        # return only visible items
        return [item for item in cls.items[name] if item.visible]

    @classmethod
    def get_dict(cls, context, name=None):
        menus = cls.process(context, name)

        def process(items):
            process_result = dict()
            for item in items:
                if item.children:
                    process_result[item.title] = process(item.children)
                else:
                    process_result[item.title] = item.data
            return process_result

        if name is None:
            # special case, process all info
            result = dict()
            for name in menus:
                result[name] = process(menus[name])
            return result
        elif name not in cls.items:
            return {}
        else:
            return process(menus)


class InfoItem(object):
    """
    InfoItem represents an item in a information container, possibly one that has sub-
    information (children).
    """

    def __init__(self, title, data=None, children=[], check=None,
                 visible=True, **kwargs):
        """
        InfoItem constructor
        title       either a string or a callable to be used for the title
        data        the data of the item or a callable to be used for the data
        children    an array of InfoItems that are sub informations to this item
                    this can also be a callable that generates an array
        check       a callable to determine if this item is visible

        All other keyword arguments passed into the InfoItem constructor are
        assigned to the InfoItem object as attributes so that they may be used.
        This allows you to attach arbitrary data and use it in which ever way suits your needs the best.
        """

        self.title = title
        self._title = None
        self.data = data
        self._data = None
        self.visible = visible
        self.children = children
        self.check = check
        self.parent = None

        # merge our kwargs into our self
        for k in kwargs:
            setattr(self, k, kwargs[k])

        # if title is a callable store a reference to it for later
        # then we'll process it at runtime
        if callable(title):
            self.title = ""
            self._title = title

        # if data is a callable store a reference to it for later
        # then we'll process it at runtime
        if callable(data):
            self.data = ""
            self._data = data

    def process(self, context):
        """
        process determines if this item should visible, if its selected, etc...
        """
        self.check_check(context)
        if not self.visible:
            return

        # evaluate title
        self.check_title(context)

        # evaluate data
        self.check_data(context)

        # evaluate children
        visible_children = []
        self.check_children(context)
        for child in self.children:
            child.process(context)
            if child.visible:
                visible_children.append(child)

        hide_empty = getattr(settings, 'HIDE_EMPTY_INFO_CONTAINER', False)
        if hide_empty and not self.check and not len(visible_children):
            self.visible = False
            return

    def check_children(self, context):
        if hasattr(self, '_children'):
            self.children = self._children(context)
        if callable(self.children):
            children = self.children(context)
            self._children = self.children
            self.children = children

        for child in self.children:
            child.parent = self

    def check_check(self, context):
        if callable(self.check):
            self.visible = self.check(context)

    def check_title(self, context):
        if callable(self._title):
            self.title = self._title(context)

    def check_data(self, context):
        if callable(self._data):
            self.data = self._data(context)
