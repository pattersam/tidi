# Development guide

## Installing

```bash
poetry install
poetry run pre-commit install
```

## Testing

```bash
poetry run pytest tests/
```

## Type checking

```bash
poetry run pre-commit run mypy --all-files
```

## Releasing

```bash
poetry run cz bump
git push && git push --tags
```

Then make a new release from the
[newly authored version tag](https://github.com/pattersam/tidi/tags).
