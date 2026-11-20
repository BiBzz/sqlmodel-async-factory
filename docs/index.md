---
description: "factory_boy factories that build and persist SQLModel objects through an async SQLAlchemy session: awaitable create and create_batch, SubFactory and get_or_create included."
---

<style>
.md-content .md-typeset h1 { display: none; }
</style>

# sqlmodel-async-factory

<p align="center">
  <a href="https://sqlmodel-async-factory.businessagile.eu"><img src="img/logo.svg" alt="sqlmodel-async-factory" width="560"></a>
</p>
<p align="center">
    <em>factory_boy factories that build and persist SQLModel objects through an async session.</em>
</p>
<p align="center">
<a href="https://github.com/BiBzz/sqlmodel-async-factory/blob/development/LICENSE" target="_blank"><img src="img/badges/license.svg" alt="License: MIT"></a>
<img src="img/badges/status.svg" alt="Status: beta">
<img src="img/badges/python.svg" alt="Python 3.10+">
</p>

---

**Documentation**: <a href="https://sqlmodel-async-factory.businessagile.eu" target="_blank">https://sqlmodel-async-factory.businessagile.eu</a>

**Source Code**: <a href="https://github.com/BiBzz/sqlmodel-async-factory" target="_blank">https://github.com/BiBzz/sqlmodel-async-factory</a>

**Created by**: <a href="https://businessagile.eu/en/about" target="_blank">Alexandre BERREBI</a>, maintained by <a href="https://businessagile.eu" target="_blank">Business Agile</a>

---

sqlmodel-async-factory gives you <a href="https://factoryboy.readthedocs.io" target="_blank">factory_boy</a> factories for <a href="https://sqlmodel.tiangolo.com" target="_blank">SQLModel</a> models that are saved through an **async** SQLAlchemy session, for test suites whose database access is async from end to end.

`factory_boy` ships `SQLAlchemyModelFactory`, which calls `session.add()` and `session.commit()` synchronously. Against an `AsyncSession` those calls either raise `MissingGreenlet` or silently never flush. `AsyncSQLModelFactory` keeps the whole `factory_boy` declaration language and makes the create step awaitable.

The key features are:

* **Awaitable create**: `await HeroFactory.create()` and `await HeroFactory.create_batch(3)` return saved, committed instances.
* **The factory_boy you know**: `Sequence`, `LazyAttribute`, `Faker`, traits and keyword overrides work unchanged.
* **SubFactory, handled once**: a hero's team is created, committed and awaited before the hero is built, so the model receives an instance, never a pending task.
* **get_or_create**: `sqlalchemy_get_or_create` reuses the existing row, looked up through `AsyncSession.exec()` so it returns model instances rather than rows.
* **Build without a database**: `build()` and `build_batch()` stay synchronous and never touch the session.
* **Typed**: the package ships its type information (`py.typed`).

## Requirements

A currently supported <a href="https://www.python.org/downloads/" target="_blank">version of Python</a>: 3.10 or later.

**factory_boy** 3, **SQLAlchemy** 2 with its `asyncio` extra and **SQLModel** 0.0.25 or later. They are installed with it.

An async database driver for your database, such as <a href="https://pypi.org/project/asyncpg/" target="_blank">asyncpg</a> for PostgreSQL or <a href="https://pypi.org/project/aiosqlite/" target="_blank">aiosqlite</a> for SQLite.

## Installation

```console
$ pip install sqlmodel-async-factory
```

or, with <a href="https://docs.astral.sh/uv/" target="_blank">uv</a>:

```console
$ uv add --dev sqlmodel-async-factory
```

## Example

### The models

Two SQLModel tables, a team and its heroes, in `models.py`:

```python
--8<-- "models.py"
```

The relationship a test reads back is loaded with `selectin`: under asyncio, an attribute cannot load itself lazily on first access. See [session settings](features.md#session-settings).

### The factories

The factories, in `factories.py`, declare how to fill each field. Here the database is an in memory SQLite one; any async engine works the same.

```python hl_lines="9 12 15 16 29"
--8<-- "factories.py"
```

`TeamFactory` reuses a team that already has the same name, and `HeroFactory` creates a new team for each hero unless one is given.

### Create, await, use

```python hl_lines="11 14 17 18"
--8<-- "quickstart.py"
```

It prints:

```text
hero-0 hero-0 in disguise team-0
[1, 1, 1]
True
```

* `HeroFactory.create()` created `team-0` first, committed it, then created the hero with it.
* The three teammates share the team passed explicitly, so no other team was created.
* The second `Preventers` team is the first one, found by name.

The same factories in a pytest suite, one fresh database per test: [using it with pytest](features.md#using-it-with-pytest).

## Why it exists

It was extracted from the test suite of a production FastAPI application whose database access is async end to end. Every attempt to reuse the stock SQLAlchemy factory ended in a copy of the same glue in each project, so the glue became a package, with the `SubFactory` case handled once and properly. How it works is described in the [design](design.md) page.

## License

This project is licensed under the terms of the [MIT license](https://github.com/BiBzz/sqlmodel-async-factory/blob/development/LICENSE).
