# async-factory-boy

[factory_boy](https://factoryboy.readthedocs.io/) factories that build and
persist [SQLModel](https://sqlmodel.tiangolo.com/) objects through an async
SQLAlchemy session.

`factory_boy` ships `SQLAlchemyModelFactory`, which calls `session.add()` and
`session.commit()` synchronously. Against an `AsyncSession` those calls either
raise `MissingGreenlet` or silently never flush. `AsyncSQLModelFactory` keeps
the whole `factory_boy` declaration language (`Sequence`, `LazyAttribute`,
`Faker`, `SubFactory`, `sqlalchemy_get_or_create`) and makes the create step
awaitable.

## Why it exists

It was extracted from the test suite of a production FastAPI application whose
database access is async end to end. Every attempt to reuse the stock
SQLAlchemy factory ended in a copy of the same twenty lines of glue in each
project, so the glue became a package, with the `SubFactory` case handled once
and properly: a sub-factory returns an `asyncio.Task` rather than an instance,
and the parent factory has to await it before passing it to the model
constructor.

## Installation

```bash
uv add async-factory-boy
```

or:

```bash
pip install async-factory-boy
```

## Usage

```python
import factory
from async_factory_boy import AsyncSQLModelFactory
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, Relationship, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    heroes: list["Hero"] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")

    team: Team | None = Relationship(
        back_populates="heroes", sa_relationship_kwargs={"lazy": "selectin"}
    )


engine = create_async_engine("postgresql+asyncpg://localhost/heroes")
session = AsyncSession(engine, expire_on_commit=False)


class TeamFactory(AsyncSQLModelFactory):
    class Meta:
        model = Team
        sqlalchemy_session = session
        sqlalchemy_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"team-{n}")


class HeroFactory(AsyncSQLModelFactory):
    class Meta:
        model = Hero
        sqlalchemy_session = session

    name = factory.Sequence(lambda n: f"hero-{n}")
    team = factory.SubFactory(TeamFactory)
```

Then, in a test:

```python
async def test_hero_belongs_to_a_team():
    hero = await HeroFactory.create()
    assert hero.team.name.startswith("team-")

    heroes = await HeroFactory.create_batch(3, team=hero.team)
    assert all(other.team_id == hero.team_id for other in heroes)
```

`create` and `create_batch` are coroutines and must be awaited. The rest of the
`factory_boy` API is unchanged.

## Session settings

Two session settings matter:

- `expire_on_commit=False`. `create` commits, and an expired instance reloads
  itself lazily on the next attribute access, which cannot work under asyncio.
- `sa_relationship_kwargs={"lazy": "selectin"}` on any relationship a test
  reads back, for the same reason.

The factory commits once per `create`, so objects are visible to other
connections immediately. That is deliberate: a test that paginates or queries
through a second session sees the fixtures.

## Compatibility

| | |
|---|---|
| Python | 3.10, 3.11, 3.12, 3.13 |
| factory_boy | >= 3 |
| SQLAlchemy | >= 2, async engine |
| SQLModel | >= 0.0.25 |

The factory calls `AsyncSession.exec()`, which is SQLModel's addition to
SQLAlchemy's `AsyncSession`, so it targets SQLModel rather than plain
SQLAlchemy models.

## Licence

MIT. See [LICENSE](LICENSE).
