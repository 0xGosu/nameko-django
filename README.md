# django-nameko

## Travis-CI  [![Coverage Status](https://coveralls.io/repos/github/tranvietanh1991/nameko-django/badge.svg)](https://coveralls.io/github/tranvietanh1991/nameko-django)
| Branch  | Build status                             |
| ------- | ---------------------------------------- |
| master  | [![Build Status](https://travis-ci.org/tranvietanh1991/nameko-django.svg?branch=master)](https://travis-ci.org/tranvietanh1991/nameko-django) |
| develop | [![Build Status](https://travis-ci.org/tranvietanh1991/nameko-django.svg?branch=develop)](https://travis-ci.org/tranvietanh1991/nameko-django) |

# nameko-django
Django intergration for nameko microservice framework

## Custom Kombu Serializer for django Object using msgpack and pickle

This serializer is fully compatible with msgpack so it can be used like this:

```yaml
serializer: 'django_msgpackpickle'
ACCEPT: ['msgpack', 'django_msgpackpickle']
SERIALIZERS:
  msgpack:
    encoder: 'nameko_django.serializer.dumps'
    decoder: 'nameko_django.serializer.loads'
    content_type: 'application/x-msgpack'
    content_encoding: 'binary'
```

In order to migrate an existing microservices stack (that use `msgpack` serializer) to use this new serializer 
first install and setup all project
```yaml
serializer: 'msgpack'
ACCEPT: ['msgpack', 'django_msgpackpickle']
SERIALIZERS:
  msgpack:
    encoder: 'nameko_django.serializer.pack'
    decoder: 'nameko_django.serializer.loads'
    content_type: 'application/x-msgpack'
    content_encoding: 'binary'
```
This will accept both of the `msgpack` and `django_msgpackpickle` but only output of result portfolio using `msgpack`
Once all service migrated, then switch to the first configuration

## Features
### This serializer will automatically encode and decode: 
- DateTime, Date, Time, Duration: 
    object will be converted to string representation compatible with django.utils.dateparse 
    and convert back using django.utils.dateparse()
- Decimal:
    object will be converted to byte string and then recover back to Decimal
- Django ORM instance:
    object will be pickled using python cPickle/pickle library and depickled back to ORM Model instance
- Django ORM queryset:
    object will be deform to Model + Query then pickled to avoid sending a list of instance

### String evaluation
This serializer can evaluate string that is compatible with `django.utils.dateparse` format 
and auto convert the string to either `DateTime`, `Date`, `Time`, `Duration` object.

Also it can evaluate string with format like this:
`"<app_name.model_name.ID>"`  this will be converted to an ORM instance: using `Model.objects.get(pk=ID)`
For example: `<auth.User.1>`

`"(app_name.model_name: RAW_QUERY_WITHOUT_SELECT_FROM)"` this will be converted to an ORM queryset
For example: `(auth.User: id >= 1 and date_joined > '2018-11-22 00:47:14.263837')`
