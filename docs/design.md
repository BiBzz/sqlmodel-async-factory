---
description: "How sqlmodel-async-factory works: why the stock SQLAlchemy factory fails on an AsyncSession, the Task returned by each create, one commit per object, lookups through AsyncSession.exec(), and the limits."
---

# Design

## Why the stock factory fails

`factory_boy` creates an object in a synchronous method, `_create()`, whose return value becomes the instance. Its `SQLAlchemyModelFactory` calls `session.add()` and `session.commit()` there, synchronously. Against an `AsyncSession` those calls either raise `MissingGreenlet` or silently never flush, since `AsyncSession.commit()` is a coroutine that does nothing until awaited. Nothing can be awaited inside a synchronous method, so the create step has to change shape.

## A Task per create

`AsyncSQLModelFactory._create()` does not save anything itself. It wraps the save in a coroutine and returns it as an `asyncio.Task`. The public `create()` is a coroutine that awaits that task, then commits.

The task is what makes `SubFactory` work. When `HeroFactory` is created, `factory_boy` evaluates the `team` declaration first, which runs `TeamFactory._create()` and yields a task, not a team. Before calling `Hero(...)`, the coroutine of the hero awaits every awaitable it receives as a field value, so the model is built with the `Team` instance. A task, unlike a bare coroutine, can be awaited more than once.

`create_batch()` awaits each `create()` in turn rather than gathering them: an `AsyncSession` runs one operation at a time.

## One commit per object

Each object is committed as soon as it is added, and `create()` commits once more when it returns. A test therefore never depends on a pending transaction: what it created is visible from any connection, including the one a web application under test opens for itself.

The cost is one transaction per object, which is fine for test fixtures and not meant for bulk loading.

## SQLModel rather than plain SQLAlchemy

The get or create lookup goes through `AsyncSession.exec()`, which SQLModel adds on top of SQLAlchemy's session and which returns model instances instead of rows. The statement is built with `select(Model).where(Model.field == value)` rather than `filter_by()`, so that SQLModel keeps its scalar typing and `exec()` yields `Team` objects.

## Limits

These follow from the Task returned by `_create()`, and hold for the create strategy only (`build()` returns plain instances):

* **A declaration that reads a sub-factory's result**, such as `factory.LazyAttribute(lambda hero: hero.team.name)`, receives the pending task instead of the team, and fails with `AttributeError`. Compute the value from the fields of the object itself, or pass it explicitly.
* **`factory.post_generation` hooks** receive the pending task of the object as their first argument, not the instance.
* **`sqlalchemy_session_factory` and `sqlalchemy_session_persistence`**, two `class Meta` options of `factory_boy`'s SQLAlchemy factory, are accepted but not read: the session comes from `sqlalchemy_session`, and every `create()` commits.

## Compatibility

| | |
|---|---|
| Python | 3.10, 3.11, 3.12, 3.13 |
| factory_boy | >= 3 |
| SQLAlchemy | >= 2, async engine |
| SQLModel | >= 0.0.25 |

The test suite runs on each of these Python versions, against SQLite through aiosqlite.
