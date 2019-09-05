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
