#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  helper.py
#
#
#  Created by vincenttran on 2020-12-18.
#  Copyright (c) 2020 vincenttran. All rights reserved.
#
from __future__ import unicode_literals

from django.db.models import QuerySet
from django.db.models.base import ModelBase
from six import string_types
import re


def DjangoORM(ORM_Model, pk):
    if not isinstance(ORM_Model, ModelBase):
        raise TypeError('%s must be a Django ORM Class of type django.db.models.base.ModelBase')
    return "<{}.{}.{}>".format(ORM_Model._meta.app_label, ORM_Model._meta.model.__name__, pk)


def DjangoQS(ORM_Model, raw_query):
    if not isinstance(ORM_Model, ModelBase):
        raise TypeError('%s must be a Django ORM Class of type django.db.models.base.ModelBase')
    if isinstance(raw_query, string_types):
        if len(raw_query) == 0 or re.search(r'^\s*SELECT\s+$', raw_query, re.I):
            raise ValueError('raw_query must not be empty nor start with SELECT')
    else:
        raise TypeError('raw_query must be a string type')
    return "({}.{}: {})".format(ORM_Model._meta.app_label, ORM_Model._meta.model.__name__, raw_query)
