---
description: "What sqlmodel-async-factory does: awaitable create and create_batch, factory_boy declarations, SubFactory, get_or_create, build without a database, pytest fixtures."
---

# Features

Every example on this page uses the [models](index.md#the-models) and the [factories](index.md#the-factories) of the home page. Each one is a script run by the test suite, and the outputs shown are the ones it checks.

## Create and await

`create()` builds the instance, adds it to the session, commits, and returns it. It is a coroutine: await it.

```python hl_lines="11 14 17 20"
--8<-- "create.py"
```

```text
1 team-0
2 Preventers
[('hero-0', 30), ('hero-1', 30)]
Rusty-Man in disguise Avengers
```

* A keyword argument overrides the declaration of its field, as in plain `factory_boy`: `name="Preventers"`.
* `create_batch(size, **kwargs)` awaits `create()` `size` times, one after the other, and returns the list.
* `team__name="Avengers"` reaches into the sub-factory, with the usual `factory_boy` double underscore.

When the instance comes back, its primary key is set and the row is committed, so a second session or an HTTP client in the same test sees it.

## factory_boy declarations

Declarations are evaluated by `factory_boy` itself, before the instance is created, so they work as documented in the <a href="https://factoryboy.readthedocs.io/en/stable/reference.html" target="_blank">factory_boy reference</a>:

* `factory.Sequence` for unique values, such as `team-0`, `team-1`;
* `factory.Faker` for realistic ones, such as the team's `headquarters`;
* `factory.LazyAttribute` for a value computed from the other fields of the same object, such as the hero's `secret_name`;
* `class Params` with `factory.Trait` for named groups of overrides.

A declaration that reads the result of a sub-factory is the exception: see [limits](design.md#limits).

## Related objects with SubFactory

A `SubFactory` field creates the related object first, waits for it, and passes the instance to the model.

```python hl_lines="11 14 15 18"
--8<-- "subfactory.py"
```

```text
['team-0', 'team-1']
True
Z-Force
```

* Without an argument, each hero gets a new team.
* An instance passed explicitly, `team=preventers`, is used as is.
* Any awaitable passed as a field value is awaited first, so `team=TeamFactory.create(name="Z-Force")` works without awaiting it yourself.

## Get or create

`sqlalchemy_get_or_create` in `class Meta` names the fields that identify a row. Before inserting, the factory looks for a row with the same values for those fields, and returns it if there is one.

```python hl_lines="12 13"
--8<-- "get_or_create.py"
```

```text
True Sharp Tower
1
```

The existing row is returned as it is: the other values given to `create()`, here `headquarters="Elsewhere"`, are not applied to it.

If the insert fails on an `IntegrityError`, for instance because another connection inserted the same key in between, the session is rolled back and the row is looked up again with the values passed explicitly to `create()`. When none of the get or create fields was passed explicitly, or when that second lookup finds nothing, the `IntegrityError` is raised.

Every field named in `sqlalchemy_get_or_create` needs a value, from a declaration or from the call. Otherwise `create()` raises `factory.errors.FactoryError`, whose message starts with `sqlalchemy_get_or_create`.

## Build without a database

`build()`, `build_batch()` and `stub()` are untouched `factory_boy` strategies: they are synchronous, and they never reach the session.

```python hl_lines="3 6"
--8<-- "build.py"
```

```text
None hero-0 team-0
[('hero-1', 48), ('hero-2', 48)]
```

The hero has no primary key, since nothing was inserted, and its sub-factory was built the same way, so `hero.team` is a `Team` instance. It suits unit tests of code that only reads the models.

## Session settings

Two settings matter, both for the same reason: under asyncio, an attribute cannot load itself from the database on first access.

* **`expire_on_commit=False`** on the session. `create()` commits, and an expired instance would reload itself lazily on the next attribute access.
* **`sa_relationship_kwargs={"lazy": "selectin"}`** on any relationship a test reads back, such as `Hero.team`.

The factory commits once per `create()`, sub-factories included. That is deliberate: a test that queries or paginates through a second session sees the objects it created.

## Using it with pytest

The session is read from `class Meta` when the factory is used. For a fresh database in each test, the tests of this library define the factories inside fixtures, on top of a session fixture. With <a href="https://pypi.org/project/pytest-asyncio/" target="_blank">pytest-asyncio</a> in auto mode, a `conftest.py`:

```python
--8<-- "pytest_fixtures/conftest.py"
```

The tests ask for the factories they need:

```python
--8<-- "pytest_fixtures/test_heroes.py"
```

Auto mode is set in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```
