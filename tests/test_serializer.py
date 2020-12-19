#!/usr/bin/python
# -*- coding: utf-8 -*-   
#
#  test_serializer.py
#  
#
#  Created by vincenttran on 10/17/19.
#  Copyright (c) 2019 nameko-django. All rights reserved.
from __future__ import unicode_literals
import logging

logger = logging.getLogger(__name__)

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings
from mock import call, patch
import pytest
from nameko_django.serializer import dumps, loads, DEFAULT_DATETIME_TIMEZONE_STRING_FORMAT
from nameko_django.helper import DjangoORM, DjangoQS
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from aenum import Enum, IntEnum, Constant
from collections import namedtuple, defaultdict, OrderedDict

try:
    # this only available in python3
    from datetime import timezone as py3timezone

    FixedOffset = (lambda d, name: py3timezone(timedelta(d), name=name))
except ImportError:
    from django.utils.timezone import FixedOffset

from django.utils import timezone
from nose import tools
from django.db.models import ObjectDoesNotExist
from box import Box, BoxList


def test_simple_list():
    test_data = [
        [0, 1, 127, 128, 255, 256, 65535, 65536, 4294967295, 4294967296],
        [-1, -32, -33, -128, -129, -32768, -32769, -4294967296, -4294967297],
        1.0,
        b"", b"a", b"a" * 31, b"a" * 32,
        None, True, False,
        [], [[], ], [[], None, ],
        {0: None},
        (1 << 23),
    ]
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert test_data == dec_data


def test_simple_tuple():
    test_data = (
        [0, 1, 127, 128, 255, 256, 65535, 65536, 4294967295, 4294967296],
        (-1, -32, -33, -128, -129, -32768, -32769, -4294967296, -4294967297),
        1.0,
        b"", b"a", b"a" * 31, b"a" * 32,
        None, True, False,
        [], [[], ], [[], None, ],
        {0: None},
        (1 << 23),
    )
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert [list(e) if isinstance(e, tuple) else e for e in test_data] == dec_data


def test_simple_boxlist():
    test_data = [{'a': 1}, {'b': 2}, {'c': 3}, 'd', 0]
    enc_data = dumps(BoxList(test_data))
    dec_data = loads(enc_data)
    assert test_data == dec_data


def test_unicode():
    test_data = ["", "abcd", ["defgh"], "Русский текст"]
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert test_data == dec_data


def test_namedtuple():
    T = namedtuple('T', "foo bar")
    enc_data = dumps(T(foo=1, bar=42))
    dec_data = loads(enc_data)
    assert dec_data == {'foo': 1, 'bar': 42}


def test_simple_dictionary():
    test_data = {
        "Type": 'Mount',
        "Path": {"Source": "/goalinvest/account_files",
                 "Destination": "/var/account_files",
                 "Mode": 1},
        "Modes": [1, 2, 3],
        "RW": True,
        "Propagation": "rprivate",
        "Level": 1.5
    }
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert test_data == dec_data


def test_default_dictionary():
    test_data = defaultdict(
        type='Mount',
        modes=1,
        rw=True,
        level=1.5
    )
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert dict(test_data) == dec_data


def test_orderred_dictionary():
    test_data = OrderedDict(
        type='Mount',
        rw=True,
        level=1.5
    )
    test_data['modes'] = 1
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert dict(test_data) == dec_data


def test_simple_boxdict():
    test_data = {'a': 1, 'b': 2, 'c': 3, 'd': '', 'e': {'e0': 0, 'e1': -1, 'ee': ['e', 'e']}}
    enc_data = dumps(Box(test_data))
    dec_data = loads(enc_data)
    assert test_data == dec_data


def test_datetime_simple():
    d0 = datetime(2019, 9, 26, 9, 16, 35, 881134, tzinfo=FixedOffset(0, name="UTC"))
    d1 = datetime(2019, 10, 16, 9, 32, 20, 555204, tzinfo=FixedOffset(0, name="UTC"))
    test_data = ["2019-09-26 09:16:35.881134 +00:00", d1]
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert [d0, d1] == dec_data


def test_datetime_simple2():
    d0 = datetime(2019, 9, 26, 9, 16, 35, 881134, tzinfo=FixedOffset(0, name="UTC"))
    d1 = datetime(2019, 10, 16, 9, 32, 20, 555204, tzinfo=FixedOffset(0, name="UTC"))
    d2_notz = datetime(2019, 9, 26, 9, 16, 35, 880000)
    test_data = {"d0": "2019-09-26 09:16:35.881134+00:00",
                 "d1": d1, "dx": ["2019-09-26 09:16:35.880000", d2_notz, "2019-09-26 09:16:35.88"]}
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert dict(d0=d0, d1=d1, dx=[d2_notz, d2_notz, d2_notz]) == dec_data


def test_date_simple():
    d0 = date(2019, 9, 26)
    d1 = date(2019, 10, 16)
    test_data = ["2019-09-26", d1]
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert [d0, d1] == dec_data


def test_time_simple():
    t0 = time(9, 16, 35, 881134)
    t1 = time(9, 32, 20, 555204)
    t1a = time(9, 32, 20)
    t1b = time(9, 32, 20, 600000)
    t1c = time(9, 32, 20, 66)
    test_data = ["09:16:35.881134", t1, {
        't1a': "09:32:20",
        't1b': "09:32:20.6",
        't1c': t1c
    }]
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert [t0, t1, {'t1a': t1a, 't1b': t1b, 't1c': t1c}] == dec_data


def test_duration_simple():
    td0 = timedelta(9, 16, 35, 881134)
    td1 = timedelta(1, 1, 13, 123)
    td2 = timedelta(-2, 86398, 876987)
    td3 = timedelta(10, 9004)
    td4 = timedelta(0, 50398, 876987)
    td5 = timedelta(0, 50398, 800000)
    td6 = timedelta(0, 50398)
    td7 = timedelta(0, 839)
    td8 = timedelta(0, 13)
    test_data = [td0, td1, td2, td3,
                 td4, td5, td6, td7, td8,
                 "9 days, 0:14:57.134035", "1 day, 0:00:01.123013", "-2 days, 23:59:58.876987", "P10DT2H30M4S",
                 "+13:59:58.876987", "+13:59:58.8", "+13:59:58", "+13:59", "+:13",
                 "13", "-13", "14.15", "-15.14"]
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert [td0, td1, td2, td3, td4, td5, td6, td7, td8, td0, td1, td2, td3, td4, td5, td6, td7, td8,
            "13", "-13", "14.15", "-15.14"] == dec_data


def test_aenum():
    class TypeEnum(Enum):
        Mount = 'Mount'
        Link = 'Link'

    class ModeEnum(IntEnum):
        R = 1
        W = 2
        X = 3

    class PathConstant(Constant):
        Src = "/goalinvest/account_files"
        Dest = "/var/account_files"

    test_data = {
        "Type": TypeEnum.Mount,
        "Path": {"Source": PathConstant.Src,
                 "Destination": PathConstant.Dest,
                 "Mode": ModeEnum.R},
        "Modes": [ModeEnum.R, ModeEnum.W, ModeEnum.X],
        "RW": True,
        "Propagation": "rprivate",
        "Level": 1.5
    }
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    out_data = {
        "Type": 'Mount',
        "Path": {"Source": "/goalinvest/account_files",
                 "Destination": "/var/account_files",
                 "Mode": 1},
        "Modes": [1, 2, 3],
        "RW": True,
        "Propagation": "rprivate",
        "Level": 1.5
    }
    assert out_data == dec_data


def test_decimal():
    test_data = [Decimal(1.5545), Decimal("1.4555"), Decimal("1.99"), Decimal(1.0 / 3), 1, 0]
    enc_data = dumps(test_data)
    dec_data = loads(enc_data)
    assert test_data == dec_data
    assert sum(test_data) == sum(dec_data)


DJANGO_DEFAULT_SETTING = dict(
    INSTALLED_APPS=('django.contrib.auth', 'django.contrib.contenttypes',),
    DATABASES=dict(default={'ENGINE': 'django.db.backends.sqlite3'}),
    DEFAULT_INDEX_TABLESPACE='indexes',
    LOGGING={},
    USE_TZ=True,
    TIME_ZONE='UTC'
)

settings.configure(**DJANGO_DEFAULT_SETTING)


def test_django_timezone():
    now = timezone.now()
    enc_data = dumps(now)
    dec_data = loads(enc_data)
    assert now == dec_data
    today = timezone.localdate()
    enc_data = dumps(today)
    dec_data = loads(enc_data)
    assert today == dec_data


def test_django_orm():
    from django.contrib.auth.models import User
    test_user = User(username="test_user", email="test_user@gmail.com")
    enc_data = dumps(test_user)
    dec_data = loads(enc_data)
    assert dec_data.username == test_user.username
    assert dec_data.email == test_user.email


def test_django_orm_queryset():
    from django.contrib.auth.models import User
    test_user_qs = User.objects.all().filter(last_login__isnull=False, id__gt=1000, date_joined__gt=timezone.now())
    enc_data = dumps(test_user_qs)
    dec_data = loads(enc_data)
    qs1 = test_user_qs.query
    qs2 = dec_data.query
    logger.debug("old_qs=%s", qs1)
    logger.debug("new_qs=%s", qs2)
    assert qs1.model._meta.db_table == qs2.model._meta.db_table
    assert str(qs1) == str(qs2)


@pytest.mark.django_db
def test_django_orm_with_db(admin_user):
    enc_data = dumps(admin_user)
    dec_data = loads(enc_data)
    logger.debug("admin_user=%s", admin_user)
    assert dec_data.username == admin_user.username
    assert dec_data.email == admin_user.email


@pytest.mark.django_db
def test_django_orm_eval_with_db(admin_user):
    enc_data = dumps(['<auth.User.{}>'.format(admin_user.id), admin_user])
    dec_data = loads(enc_data)
    u, u1 = dec_data
    logger.debug("admin_user.id=%s", admin_user.id)
    assert u.username == u1.username == admin_user.username
    assert u.email == u1.email == admin_user.email


@pytest.mark.django_db
def test_django_orm_eval_with_db2():
    enc_data = dumps('<auth.User.2>')
    with tools.assert_raises(ObjectDoesNotExist):
        loads(enc_data)


@pytest.mark.django_db
def test_django_orm_queryset_with_db():
    from django.contrib.auth.models import User
    test_user_qs = User.objects.all().filter(last_login__isnull=False, id__gt=1000, date_joined__gt=timezone.now())
    enc_data = dumps(test_user_qs)
    dec_data = loads(enc_data)
    qs1 = test_user_qs.query
    qs2 = dec_data.query
    assert qs1.model._meta.db_table == qs2.model._meta.db_table
    assert str(qs1) == str(qs2)


@pytest.mark.django_db
def test_django_orm_queryset_eval_with_db(admin_user):
    from django.contrib.auth.models import User
    test_user_qs = User.objects.all().filter(id__gte=1,  # last_login__isnull=False,
                                             date_joined__gt='2018-11-22 00:47:14.263837+00:00')
    qs_string = '(auth.User: {})'.format("id >= 1 and date_joined > '2018-11-22 00:47:14.263837+00:00'")
    logger.debug(qs_string)
    enc_data = dumps(qs_string)
    dec_data = loads(enc_data)
    qs1 = test_user_qs.query
    qs2 = dec_data.query
    logger.debug("qs1=%s", qs1)
    logger.debug("qs2=%s", qs2)
    assert len(test_user_qs) == 1 == dec_data.count()
    assert list(test_user_qs) == list(dec_data)
    u = dec_data.first()
    assert u.username == admin_user.username
    assert u.email == admin_user.email


@pytest.mark.django_db
def test_django_orm_eval_with_db_using_helper(admin_user):
    from django.contrib.auth.models import User
    enc_data = dumps(DjangoORM(User, admin_user.id))
    dec_data = loads(enc_data)
    u = dec_data
    logger.debug("admin_user.id=%s", admin_user.id)
    assert u.username == admin_user.username
    assert u.email == admin_user.email


@pytest.mark.django_db
def test_django_orm_queryset_with_db_using_helper():
    from django.contrib.auth.models import User
    test_user_qs = User.objects.all().filter(last_login__isnull=False, id__gt=1000,
                                             date_joined__gt='2018-11-22 00:47:14.263837+00:00')
    raw_qs = DjangoQS(User, "last_login notnull and id > 1000 and date_joined > '2018-11-22 00:47:14.263837+00:00'")
    enc_data = dumps(raw_qs)
    dec_data = loads(enc_data)
    qs1 = test_user_qs.query
    qs2 = dec_data.query
    logger.debug("%s <> %s", qs1, qs2)
    assert qs1.model._meta.db_table == qs2.model._meta.db_table
    assert len(test_user_qs) == len(dec_data)
