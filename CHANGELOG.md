# Changelog

Notable changes to this project, newest first.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-28

First version published on PyPI.

### Added

- `AsyncSQLModelFactory`, a `factory_boy` factory whose `create` and
  `create_batch` are coroutines and which persists through
  `sqlmodel.ext.asyncio.session.AsyncSession`.
- Support for `SubFactory`: a sub-factory returns an `asyncio.Task`, which the
  parent factory awaits before passing the instance to the model constructor.
- Support for `sqlalchemy_get_or_create`, whose lookup goes through
  `AsyncSession.exec()` so it returns model instances rather than rows.
- The rest of the `factory_boy` declaration language, `Sequence`,
  `LazyAttribute`, `Faker` and `SubFactory`, unchanged.
- Type information shipped with the package (`py.typed`).

[Unreleased]: https://github.com/BiBzz/sqlmodel-async-factory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/BiBzz/sqlmodel-async-factory/releases/tag/v0.1.0
