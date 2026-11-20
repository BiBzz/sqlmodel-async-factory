---
description: "API reference of sqlmodel-async-factory: AsyncSQLModelFactory, its class Meta options, and which factory_boy methods are coroutines."
---

# Reference

The package exports one class.

```python
from sqlmodel_async_factory import AsyncSQLModelFactory
```

## AsyncSQLModelFactory

A `factory.Factory` subclass for SQLModel table models, saved through a `sqlmodel.ext.asyncio.session.AsyncSession`. Subclass it, declare the fields, and set `class Meta`.

### class Meta

| Option | Required | Meaning |
|---|---|---|
| `model` | yes | The SQLModel table class to build, such as `Hero`. |
| `sqlalchemy_session` | yes, to create | The `AsyncSession` every `create()` adds to and commits. Create it with `expire_on_commit=False`. |
| `sqlalchemy_get_or_create` | no | A tuple of field names. When set, `create()` first looks for a row with the same values for these fields and returns it if there is one. See [get or create](features.md#get-or-create). |

The other options of `factory_boy`, such as `abstract`, `exclude` or `rename`, are handled by `factory_boy` itself. `sqlalchemy_session_factory` and `sqlalchemy_session_persistence` are accepted but not read: see [limits](design.md#limits).

### Methods

| Method | Returns | Database |
|---|---|---|
| `await Factory.create(**kwargs)` | the saved instance | one insert, or a lookup with get or create, then commit |
| `await Factory.create_batch(size, **kwargs)` | a list of `size` saved instances | `size` creates, one after the other |
| `Factory.build(**kwargs)` | an unsaved instance | none |
| `Factory.build_batch(size, **kwargs)` | a list of unsaved instances | none |
| `Factory.stub(**kwargs)` | a `factory.base.StubObject` | none |

`create()` and `create_batch()` are coroutines: forgetting `await` gives a coroutine instead of an instance, and nothing is saved.

Keyword arguments override declarations, and `field__subfield=value` reaches into a `SubFactory`, as in plain `factory_boy`. A field value that is awaitable, such as the coroutine of another factory's `create()`, is awaited before the model is built.

Calling the class itself, `HeroFactory()`, uses the create strategy and returns a coroutine as well, but type checkers see a `HeroFactory` instance there. Prefer `await HeroFactory.create()`.

### Errors

* `factory.FactoryError`, from `create()`, when a field named in `sqlalchemy_get_or_create` has no value.
* `sqlalchemy.exc.IntegrityError`, from `create()`, when the insert breaks a constraint. With get or create, only when the conflicting row cannot be found: see [get or create](features.md#get-or-create).
