#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  serializer.py
#
#
#  Created by vincenttran on 2019-09-02.
#  Copyright (c) 2019 bentodatabase. All rights reserved.
#
from __future__ import unicode_literals

import os
from datetime import datetime
from decimal import Decimal
from io import BytesIO

from aenum import Enum
from django.db.models import Model, QuerySet
from django.db.models.base import ModelBase
from django.db.models.sql.query import Query
from django.utils import dateparse
from msgpack import packb, unpackb
from six import string_types

try:
    import cPickle as pickle
except ImportError:
    import pickle

DEFAULT_DATETIME_TIMEZONE_STRING_FORMAT = os.getenv("DEFAULT_DATETIME_TIMEZONE_STRING_FORMAT", "%Y-%m-%d %H:%M:%S.%f%z")


def serializable(obj):
    """ Make an object serializable for JSON, msgpack

    :param obj: Namedtuple instance
    :return:
    """
    if obj is None:
        return
    if hasattr(obj, '_asdict') and callable(obj._asdict):
        result_obj = dict(obj._asdict())
    elif isinstance(obj, Enum) and hasattr(obj, 'value'):
        return obj.value
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.strftime(DEFAULT_DATETIME_TIMEZONE_STRING_FORMAT)
    else:
        dump_obj = django_pickle_dumps(obj)
        if dump_obj is not None:
            return dump_obj
        else:
            result_obj = obj

    if isinstance(result_obj, dict):
        return {
            key: serializable(value)
            for key, value in result_obj.items()
        }
    elif isinstance(result_obj, list) or isinstance(result_obj, set) or isinstance(result_obj, tuple):
        return [serializable(value) for value in result_obj]
    else:
        return result_obj


def django_is_pickable(s):
    if isinstance(s, string_types) and len(s) > 255 and s[:2] == b'\x80\x02' and s[-1] == b'.':
        return True
    return False


def django_pickle_dumps(obj):
    if isinstance(obj, Model):
        return pickle.dumps(obj, -1)
    elif isinstance(obj, QuerySet):
        return pickle.dumps((obj.model, obj.query), -1)
    else:
        return None


def django_pickle_loads(obj_string):
    objs = pickle.loads(obj_string)
    if isinstance(objs, tuple) and len(objs) == 2:
        # untouched queryset case
        model, query = objs
        if isinstance(model, ModelBase) and isinstance(query, Query):
            qs = model.objects.all()
            qs.query = query
            return qs
    # normal case
    return objs


def deserializable(obj):
    """ Make an object serializable for JSON, msgpack

    :param obj: Namedtuple instance
    :return:
    """
    if obj is None:
        return
    if isinstance(obj, string_types):
        if django_is_pickable(obj):
            dump_obj = django_pickle_loads(obj)
        else:
            dump_obj = dateparse.parse_datetime(obj)
        if dump_obj is not None:
            return dump_obj
        else:
            result_obj = obj
    else:
        result_obj = obj

    if isinstance(result_obj, dict):
        return {
            key: deserializable(value)
            for key, value in result_obj.items()
        }
    elif isinstance(result_obj, list) or isinstance(result_obj, set) or isinstance(result_obj, tuple):
        return [deserializable(value) for value in result_obj]
    else:
        return result_obj


def pack(s):
    return packb(s, use_bin_type=True)


def unpack(s):
    return unpackb(s, raw=False)


def dumps(o):
    return pack(serializable(o))


def loads(s):
    if not isinstance(s, string_types):
        s = BytesIO(s)
    return deserializable(unpack(s))


register_args = (dumps, loads, 'application/x-django-msgpackpickle', 'binary')
