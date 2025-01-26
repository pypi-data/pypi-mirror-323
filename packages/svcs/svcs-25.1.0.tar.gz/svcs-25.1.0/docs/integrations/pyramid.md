# Pyramid

*svcs*'s [Pyramid](https://trypyramid.com) integration uses Pyramid's {class}`pyramid.registry.Registry` to store its own {class}`svcs.Registry` (yes, unfortunate name clash) and a {term}`tween` that attaches a fresh {class}`svcs.Container` to every request and closes it afterwards.


## Initialization

The most important integration API for Pyramid is {func}`svcs.pyramid.init()` that takes an {class}`pyramid.config.Configurator` and optionally the positions where to put its {term}`tween` using the *tween_under* and *tween_over* arguments.

You can use {func}`svcs.pyramid.register_factory()` and {func}`svcs.pyramid.register_value()` that work like their {class}`svcs.Registry` counterparts but take a {class}`pyramid.config.Configurator` as the first option (or any other object that has a `registry: dict` field, really).

So you application factory is going to look something like this:

```python
def make_app():
    ...

    with Configurator(settings=settings) as config:
        svcs.pyramid.init(config)
        svcs.pyramid.register_factory(config, Database, db_factory)

        ...

        return config.make_wsgi_app()
```


## Service Acquisition

You can use {func}`svcs.pyramid.svcs_from()` to access a request-scoped {class}`svcs.Container` from a request object:

```python
from svcs.pyramid import svcs_from

def view(request):
    db = svcs_from(request).get(Database)
```

Or you can use {func}`svcs.pyramid.get()` to access a service from the current request directly:

```python
import svcs

def view(request):
    db = svcs.pyramid.get(request, Database)
```


### Thread Locals

Despite being [discouraged](<inv:#narr/threadlocals>), you can use Pyramid's thread locals to access the active container.

So this:

```python
def view(request):
    registry = svcs.pyramid.get_registry()
    container = svcs.pyramid.svcs_from()
```

is equivalent to this:

```python
def view(request):
    registry = svcs.pyramid.get_registry(request)
    container = svcs.pyramid.svcs_from(request)
```

::: {caution}
These functions only work from within **active** Pyramid requests.
:::


(pyramid-health)=

## Health Checks

As with services, you have the option to either {func}`svcs.pyramid.svcs_from` on the request or go straight for {func}`svcs.pyramid.get_pings`.

A health endpoint could look like this:

```{literalinclude} ../examples/pyramid/health_check.py
```


## Testing

Assuming you have an application factory `your_app.make_app()`[^factory] that initializes and configures *svcs* using {func}`svcs.pyramid.init()`, you can use the following fixtures to get a [WebTest application](https://docs.pylonsproject.org/projects/pyramid/en/latest/quick_tutorial/functional_testing.html) and its registry for overrides:

[^factory]: The one that returns {meth}`pyramid.config.Configurator.make_wsgi_app`.

% skip: next

```python
from your_app import make_app

import pytest
import svcs
import webtest

@pytest.fixture
def app():
    app = make_app()

    with svcs.pyramid.get_registry(app):
        yield webtest.TestApp(app)


@pytest.fixture
def registry(app):
    return svcs.pyramid.get_registry(app)
```

Now you can write a test like this:

```python
from sqlalchemy import Engine

def test_broken_database(app, registry):
    boom = Mock(spec_set=Engine)
    boom.execute.side_effect = RuntimeError("Boom!")

    registry.register_value(Engine, boom)  # ← override the database

    resp = app.get("/some-url")

    assert 500 == resp.status_code
```

Since {func}`~svcs.pyramid.init()` takes a *registry* keyword argument, you can also go the other way around and pass a (potentially pre-configured) {class}`svcs.Registry` *into* your application factory.


## Cleanup

You can use {func}`svcs.pyramid.close_registry()` to close the registry that is attached to the {class}`pyramid.registry.Registry` of the config or app object that you pass as the only parameter.


## API Reference

### Application Life Cycle

```{eval-rst}
.. module:: svcs.pyramid

.. autofunction:: init
.. autofunction:: close_registry

.. autofunction:: svcs_from
.. autofunction:: get_registry

.. autoclass:: PyramidRegistryHaver()
```


### Registering Services

```{eval-rst}
.. autofunction:: register_factory
.. autofunction:: register_value
```


### Service Acquisition

```{eval-rst}
.. function:: get(request, *svc_types)

   Same as :meth:`svcs.Container.get()`, but uses the container from *request*.

.. autofunction:: get_abstract
.. autofunction:: get_pings
```
