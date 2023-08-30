# tidi

<p>
<a href="https://github.com/pattersam/tidi/actions?query=workflow%3ATest+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://github.com/pattersam/tidi/workflows/Test/badge.svg?event=push&branch=main" alt="Test">
</a>
<a href="https://pypi.org/project/tidi" target="_blank">
    <img src="https://img.shields.io/pypi/v/tidi" alt="Package version">
</a>
<a href="https://pattersam.github.io/tidi/" target="_blank">
    <img src="https://img.shields.io/badge/docs-mkdocs-blue" alt="Documentation">
</a>
<a href="https://pypi.org/project/tidi" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/tidi.svg?" alt="Supported Python versions">
</a>
</p>

_A small dependency injection Python library._

Inspired by [Kent Tong's](https://github.com/freemant2000)
[disl](https://github.com/freemant2000/disl/tree/main) and
[FastAPI's `Depends`](https://fastapi.tiangolo.com/tutorial/dependencies/).

## Motivation

I found myself wanting to learn more about how dependency injection can be done
in a pythonic way, with type-hinting, so had the itch to develop (yet another) 
library for it and share it as open source 🧑‍💻✌️

## Primary API

The top level import of `tidi` provides everything needed it's primary intended
use.

- `@tidi.inject` - a decorator that will replace certain keyword arguments 
  with dependencies, based on their type & if they haven't been passed in
- `tidi.Injected[DependencyClass]` - a type alias, wrapping typing.Annotated,
  that indicates that a keyword argument should be injected
- `tidi.register(dependency_instance)` - a function that registers an object to
  be available for injection as a dependency
- `tidi.Provider(get_dependency_function)` - a wrapper class around a function 
  that will be called to provide a dependency
- `tidi.UNSET` - a sentinel object to indicate that a dependency should be
  loaded from the registry
- `tidi.field_factory(DependencyClass)` - a helper function for injecting 
  dependencies into dataclass fields

## Example of use

Consider a micro-sized interactive CLI that lets a user choose a handbag then
search through it,

``` py
# search-handbag.py

import tidi

from handbags import Handbag, HandbagItem, load_handbag


@tidi.inject
def dig_through_handbag(
    item_type: str,
    handbag: tidi.Injected[Handbag] = tidi.UNSET,
) -> HandbagItem | None:
    return handbag.get_items_by_type(item_type).first(default=None)


def init_handbag():
    selected_handbag = input("Select a handbag: ")
    tidi.register(load_handbag(selected_handbag))


def run_search():
    item_type = input("What are you looking for? ")
    # ⬇️ registered `Handbag` instance gets injected ✨
    item = dig_through_handbag(item_type)
    if item is None:
        print("Uh oh, can't find it 🤷‍♀️, try again")
        run_search()
    else:
        print(f"We're in luck! Here's your {item.name} 😎")


if __name__ == "__main__":
    init_handbag()
    run_search()
```

Running it looks something like this,

```
$ python search-handbag
Select a handbag: BCBGMAXAZRIA
What are you looking for? Nail file
Uh oh, can't find it 🤷‍♀️, try again
What are you looking for? Lip balm
We're in luck! Here's your Blistex 😎
```

We can see Dependency Injection happening hear to achieve Inversion of Control
and obey the Law of Demeter.

* `dig_through_handbag` isn't responsible for creating a `Handbag` and doesn't
  require its caller to know about it, rather a `Handbag` is injected ✨
* `init_handbag` creates the `Handbag`, but doesn't need to return it. An
  example of separating the app initialisation from the main logic.
* `run_search` doesn't need to know about anything that it doesn't use (in this
  case the `Handbag`), obeying the Law of Demeter.

When testing,

* a mock `Handbag` could be passed in as a keyword argument to test 
  `dig_through_handbag`, and
* patching `dig_through_handbag` with a stub could be done to test `run_search`
  with no requirement for a mock `Handbag`.

### More examples

You can find some executable examples in the [demo/](https://github.com/pattersam/tidi/tree/main/demo)
directory of the repo.

Also see the [Usage documentation](https://pattersam.github.io/tidi/usage/) for
more examples.

## Interested in contributing?

Feel free to create an issue or author a PR 😊

For the latter, check out the [CONTRIBUTING](CONTRIBUTING.md) guide for a quick
start on development.
