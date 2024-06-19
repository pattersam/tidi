# Usage

There are a few main ways it's intended to be used.

## Examples of usage

### Inject a dependency that has been put in a registry

``` py
import tidi

@tidi.inject
def run(auth: tidi.Injected[AuthService] = tidi.UNSET):
    if auth.is_super_user():
        logger.info(f"Running with elevated permissions.")
    ...

if __name__ == "__main__":
    tidi.register(AuthService())

    ...

    run()  # 🪄 `AuthService` injected into `run` ✨
```

### Objects can be registered & retrieved via their abstractions

``` py
import tidi

@tidi.inject
def watch(content: tidi.Injected[MediaABC] = tidi.UNSET):
    content.play()  # `MediaABC` interface used by type checkers 🤝
    ...

if __name__ == "__main__":
    # register a `Film` object to be accessed as an abstract `MediaABC` type
    django_unchained = Film(isan="0000-0003-6795-0000-O-0000-0000-2")
    tidi.register(django_unchained, type_=MediaABC)

    ...

    watch()  # 🪄 `django_unchained` injected into `watch` ✨
```


### Inject a dependency provided by a function

``` py
import tidi

def get_secret() -> str:
    return "wshwshwhswhs"

@tidi.inject
def run(secret: tidi.Injected[str] = tidi.Provider(get_secret)):
    logger.info(f"don't tell anyone this but, {secret}")

if __name__ == "__main__":
    run()  # 🪄 result from `get_secret()` injected into `run` ✨
```

### Inject a dependency provided by a context manager

``` py
import contextlib
import typing as t

import tidi

@contextlib.contextmanager
def open_sesame() -> t.Iterator[str]:
    logger.info("abracadabra")
    try:
        yield "please"
    finally:
        logger.info("alakazam")

@tidi.inject
def run(magic_word: tidi.Injected[str] = tidi.Provider(open_sesame)):
    logger.info(f"the magic word is {magic_word}")

if __name__ == "__main__":
    run()  # 🪄 result from `open_sesame()` injected into `run` ✨
```

### Or provided by instantiating a class

``` py
import tidi

class SnackRepo():
    def __init__(self, db_string = "fridge"):
        self.db_string = db_string

    def get_snack(self):
        return f"snack, out of the {self.db_string}"

@tidi.inject
def eat_snack(repo: tidi.Injected[SnackRepo] = tidi.Provider(SnackRepo)):
    logger.info(f"eating {repo.get_snack()}")

if __name__ == "__main__":
    eat_snack()  # 🪄 a new `SnackRepo` injected into `run` ✨
```

### The injection also works with classes, either into the constructor

``` py
import tidi

@tidi.inject
class Algorithm:
    def __init__(self, config: tidi.Injected[Config] = tidi.UNSET):
        self.tolerance = config.tolerance

    def run(self, input_value: float) -> float:
        return input_value - input_value * self.tolerance

if __name__ == "__main__":
    tidi.register(Config(tolerance=0.1))
    alg = Algorithm()  # 🪄 `Config` injected into new `Algorithm` instance ✨
    alg.run(10.0)
```

### Or into their methods

``` py
import tidi

class Job:
    def __init__(self, name):
        self.name = name

    @tidi.inject
    def run(self, db: tidi.Injected[DBConnection] = tidi.Provider(get_db_conn)):
        logger.info(f"run job {self.name} using database {db.name}")

if __name__ == "__main__":
    job = Job("new job")
    job.run()  # 🪄 `DBConnection` injected into `job.run` ✨
```

### And to inject dependencies into a dataclass, use the field_factory

``` py
from dataclasses import dataclass, field

import tidi

@dataclass
class Output:
    value: float
    created_by: User = field(default_factory=tidi.field_factory(User))

def process_next_job():
    return Output(value=1)  # 🪄 `User` injected into `Output.created_by` ✨

if __name__ == "__main__":
    current_user = User.from_env_credentials()
    tidi.register(current_user)
    output = process_next_job()
```
