# Home

Welcome to the [Tidi](https://github.com/pattersam/tidi) documentation.

Tidi is a small dependency injection Python library.

It's aim, apart from being a learning outcome of the author, is to provide a
clean, type checker compliant, API for medium sized projects to benefit from
Inversion of Control (IoC) through applying Dependency Injection (DI) without
having to adopt a large DI framework.

## Installation

``` sh
pip install tidi
```

## Usage

### Example usage

``` py
import tidi

from my_package.auth import AuthError, AuthService
from my_package.db import DBSession, QueuedJob, create_db_session
from my_package.job import Job, JobQueue

@tidi.inject
def process_job(
  job: Job,
  db_session: tidi.Injected[DBSession] = tidi.Provider(create_db_session)
  auth_service: tidi.Injected[AuthService] = tidi.UNSET,
):
  if not auth_service.is_logged_in_user_authorised_for_job(job.name):
    raise AuthError("Unauthorised to run this job :(")
  job.run(db_session=db_session)

@tidi.inject
class JobQueue:
  def __init__(
    self,
    db_session: tidi.Injected[DBSession] = tidi.Provider(create_db_session)
  ):
  self.jobs = db_session.query(QueuedJob).all()

def init_app():
  auth_service = AuthService()
  auth_service.log_in_user()
  tidi.register(auth_service)

def main():
  init_app()
  for job in JobQueue().jobs:  # 🪄 `DBSession` injected into `JobQueue` ✨
    process_job(job)  # 🪄 `DBSession` and `AuthService` injected into `process_job` ✨

if __name__ == "__main__":
  main()
```

Or see more examples in the [`demo/`](https://github.com/pattersam/tidi/tree/main/demo)
directory of the repo.

### Further documentation of use

See the [Usage](/usage) guide for more details

## Motivation

I found myself wanting to learn more about how DI can be done in a _pythonic_
way, with type-hinting, so had the itch to develop (yet another) library for it
and share it as open source 🧑‍💻✌️

My main inspiration was [Kent Tong's disl](https://github.com/freemant2000/disl/tree/main)
and [FastAPI's `Depends`](https://fastapi.tiangolo.com/tutorial/dependencies/).

## Contribution guide

If you'd like to contribute to the development of Tidi, please clone the
[repo](https://github.com/pattersam/tidi) and read the
[CONTRIBUTING.md](https://github.com/pattersam/tidi/blob/main/CONTRIBUTING.md)
