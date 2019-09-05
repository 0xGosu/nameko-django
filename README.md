# nameko-django
Django intergration for nameko microservice framework

## Custom Kombu Serializer for django Object using msgpack and pickle

This serializer is fully compatible with msgpack so it can be used like this:

```yaml
serializer: 'django_msgpackpickle'
ACCEPT: ['msgpack', 'django_msgpackpickle']
SERIALIZERS:
  msgpack:
    encoder: 'msgpack.dumps'
    decoder: 'nameko_django.serializer.loads'
    content_type: 'application/x-msgpack'
    content_encoding: 'binary'
```

In order to migrate an existing microservices stack to use this new serializer first install and setup all project
```yaml
serializer: 'msgpack'
ACCEPT: ['msgpack', 'django_msgpackpickle']
SERIALIZERS:
  msgpack:
    encoder: 'msgpack.dumps'
    decoder: 'nameko_django.serializer.loads'
    content_type: 'application/x-msgpack'
    content_encoding: 'binary'
```
This will accept both of the `msgpack` and `django_msgpackpickle` but only output of result portfolio using `msgpack`
Once all service migrated, then switch to the first configuration
