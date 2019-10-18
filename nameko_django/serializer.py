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

from datetime import datetime, date, time, timedelta
from decimal import Decimal, ROUND_HALF_EVEN, Context, Overflow, DivisionByZero, InvalidOperation
from aenum import Enum, IntEnum, Constant
from django.db.models import Model, QuerySet
from django.db.models.base import ModelBase
from django.db.models.sql.query import Query
from django.utils import dateparse
from msgpack import packb, unpackb, ExtType
from six import string_types, ensure_str, ensure_binary
import re

try:
    import cPickle as pickle
except ImportError:
    import pickle

import logging

logger = logging.getLogger(__name__)

DEFAULT_DATE_STRING_FORMAT = "%Y-%m-%d"
DEFAULT_TIME_STRING_FORMAT = "%H:%M:%S.%f"
DEFAULT_DATETIME_TIMEZONE_STRING_FORMAT = "%Y-%m-%d %H:%M:%S.%f%z"
DEFAULT_DECIMAL_CONTEXT = Context(prec=28, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
                                  capitals=1, flags=[], traps=[Overflow, DivisionByZero,
                                                               InvalidOperation])


def pack(s):
    return packb(s, use_bin_type=True)


def unpack(s):
    return unpackb(s, raw=False)


class ExternalType(IntEnum):
    DECIMAL = 42
    ORM_INSTANCE = 43
    ORM_QUERYSET = 44


def encode_nondefault_object(obj):
    """ Encode an object by make it compatible with default msgpack encoder or using ExtType

    :param obj: any objet
    :return:
    """
    if obj is None:
        return
    if hasattr(obj, '_asdict') and callable(obj._asdict):
        return dict(obj._asdict())
    elif isinstance(obj, Enum) and hasattr(obj, 'value'):
        return obj.value
    elif isinstance(obj, Constant) and hasattr(obj, '_value_'):
        return obj._value_
    elif isinstance(obj, Decimal):
        return ExtType(ExternalType.DECIMAL, ensure_binary(str(obj)))
    elif isinstance(obj, datetime):
        return obj.strftime(DEFAULT_DATETIME_TIMEZONE_STRING_FORMAT)
    elif isinstance(obj, date):
        return obj.strftime(DEFAULT_DATE_STRING_FORMAT)
    elif isinstance(obj, time):
        return obj.strftime(DEFAULT_TIME_STRING_FORMAT)
    elif isinstance(obj, timedelta):
        if 0 <= obj.total_seconds() < 86400:
            return '+{}'.format(obj)
        return str(obj)
    else:
        if isinstance(obj, Model):
            return ExtType(ExternalType.ORM_INSTANCE, pickle.dumps(obj, -1))
        elif isinstance(obj, QuerySet):
            return ExtType(ExternalType.ORM_QUERYSET, pickle.dumps((obj.model, obj.query), -1))
    logger.debug("unknown type obj=%s", obj)
    return obj


def django_ext_hook(code, data):
    if code == ExternalType.DECIMAL:
        return Decimal(ensure_str(data, encoding='utf-8'), context=DEFAULT_DECIMAL_CONTEXT)
    elif code == ExternalType.ORM_INSTANCE:
        return pickle.loads(data)
    elif code == ExternalType.ORM_QUERYSET:
        # untouched queryset case
        model, query = pickle.loads(data)
        if isinstance(model, ModelBase) and isinstance(query, Query):
            qs = model.objects.all()
            qs.query = query
            return qs
    # unable to decode external type then return as it is
    return ExtType(code, data)


def decode_dict_object(dict_obj):
    logger.debug("decode dict obj=%s", dict_obj)
    return {
        key: decode_single_object(value)
        for key, value in dict_obj.items()
    }


def decode_list_object(list_obj):
    logger.debug("decode list obj=%s", list_obj)
    return [decode_single_object(value) for value in list_obj]


datetime_test_re = re.compile(
    r'[-+.:0123456789]*:[-+.:0123456789]+'  # datetime
    r'|\d+\-\d+\-\d+'  # date
    r'|[-+]?\d+\s+days?,?\s*[.:0123456789]*'  # duration
    r'|[-+]?P\d*D?T\d*H?\d*M?\d*S?'  # duration ISO_8601
)


def decode_single_object(obj):
    if obj is None:
        return
    logger.debug("decode single obj=%s", obj)
    if isinstance(obj, string_types):
        datetime_obj = None
        lenobj = len(obj)
        if lenobj <= 33 and datetime_test_re.match(obj):
            if lenobj == 33:
                datetime_obj = dateparse.parse_datetime(obj.replace(' +', '+'))
            elif 31 <= lenobj <= 32 or 21 <= lenobj <= 26:
                datetime_obj = dateparse.parse_datetime(obj)
            elif lenobj == 10:
                datetime_obj = dateparse.parse_date(obj)
                if not datetime_obj:  # there is an over lapse case
                    datetime_obj = dateparse.parse_time(obj)
            elif lenobj == 5 or lenobj == 8 or 10 <= lenobj <= 15:
                datetime_obj = dateparse.parse_time(obj)
            if datetime_obj is None:  # a time object is also maybe a valid duration object
                datetime_obj = dateparse.parse_duration(re.sub(r'^(\-?)\+?:?(\d)', r'\1\2', obj))
        # if there is a datetime_obj can be decoded from string then return it
        if datetime_obj is not None:
            return datetime_obj
    return obj


def dumps(o):
    # logger.debug("dumps obj=%s", o)
    return packb(o, strict_types=True, default=encode_nondefault_object, use_bin_type=True)


def loads(s):
    if not isinstance(s, string_types):
        s = bytes(s)
    return unpackb(s, ext_hook=django_ext_hook, object_hook=decode_dict_object, list_hook=decode_list_object, raw=False)


register_args = (dumps, loads, 'application/x-django-msgpackpickle', 'binary')
