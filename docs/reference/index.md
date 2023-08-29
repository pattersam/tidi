# Reference

## Main API

The top level import of `tidi` provides everything needed it's [primary intended use](/usage).

* `tidi.inject` - a decorator that will replace certain keyword arguments with dependencies, based on their type & if they haven't been passed in
* `tidi.Injected ` - a type alias, wrapping `typing.Annotated`, that indicates that a keyword argument should be injected
* `tidi.register ` - a function that registers an object to be available for injection as a dependency
* `tidi.Provider ` - a wrapper class around a function that will be called to provide a dependency
* `tidi.UNSET ` - a sentinel object to indicate that a dependency should be loaded from the registry
* `tidi.field_factory` - a helper function for injecting dependencies into dataclass fields

### `tidi.inject`, `tidi.Injected`, & `tidi.UNSET`

`@tidi.inject` will injects dependencies into keyword arguments with the `tidi.Injected` type
annotation.

If the default value is `tidi.UNSET`, it will search for that dependency in the
registry.

``` py
@tidi.inject
def get_users(db: tidi.Injected[Database] = tidi.UNSET):
    db.query(Users).all()
```

See the [`tidi.decorator`](./decorator.md) documentation for more detail.

### `tidi.register`

To register a dependency instance, simple call the `tidi.register` function

``` py
database = load_database()
tidi.register(database)
```

This puts it into the _default_ registry which is shared across 

See the [`tidi.registry`](./registry.md) documentation for more detail.


### `tidi.Provider`  

For more control over what instance is injected, use the provider function.

The elected provider function will be called each time the function is called.

``` py
@tidi.inject
def get_users(db: tidi.Injected[Database] = tidi.Provider(load_database)):
    db.query(Users).all()
```

See the [`tidi.decorator`](./decorator.md) documentation for more detail.

### `tidi.field_factory`

When working with dataclasses, the `inject` decorator doesn't work, so use the
`field_factory` convenience function to inject the dependency into a field upon
instance creation.

``` py
from dataclasses import dataclass, field

@dataclass
class UserQuery:
    name: str
    db: Database = field(default_factory=tidi.field_factory(Database))

user_query = UserQuery()
execute_user_query(user_query)
```

## Modules

Tidi's codebase consists of the following four, relatively small modules:

* [`tidi.decorator`](./decorator.md) - provides the main inject decorator, using `tidi.parameters` to determine which parameters of the wrapped function to replace
* [`tidi.parameters`](./parameters.md) - background wrapper of the builtin `inspect.Parameter` class for determining which function parameters are annotated
* [`tidi.registry`](./registry.md) - provides simple registry class for holding dependency instances, stored in a dictionary (map), using their type as the key
* [`tidi.resolver`](./resolver.md) - contains the logic used to either find an object from the registry or from a provider function
