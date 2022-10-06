# RHEL Cloud image locator

This project is a work in progress with a goal of making it easier to find Red
Hat Enterprise Linux™ at various public cloud providers.


## Development guide

[Poetry] is used for dependency management and centralized configuration for testing and
linting tools. Start by [installing poetry] and then clone the repository.

After cloning, run the following:

```console
poetry install
```

Pre-commit hooks are used to ensure that code passes the linter checks before you push.
Prepare the pre-commit hooks on your computer by running some commands:

```console
poetry run pre-commit install
poetry run pre-commit run --all-files
```

You can quickly run tests with `poetry run pytest` or run the full pre-commit suite with
`poetry run pre-commit run --all-files`. Or, simply start a commit (such as `git commit -m "Fixed the bug"`) and the pre-commit checks run automatically.

If you need to add more Python packages to poetry, run the following:

```console
# For packages that this project requires in production
poetry add foo

# For packages that are only needed for linting, testing, or development work
poetry add --group dev bar
```

## Running tests

Use poetry to run pytest:

```commandline
# Run all tests, including end-to-end tests that call out to cloud APIs:
poetry run pytest

# Skip any tests that communicate remotely:
poetry run pytest -m "not e2e"
```

[Poetry]: https://python-poetry.org/
[installing poetry]: https://python-poetry.org/docs/#installation
