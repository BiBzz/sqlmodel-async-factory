from collections.abc import AsyncIterator

import factory
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, Relationship, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from async_factory_boy import AsyncSQLModelFactory


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


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def team_factory(session: AsyncSession) -> type[AsyncSQLModelFactory]:
    class TeamFactory(AsyncSQLModelFactory):
        class Meta:
            model = Team
            sqlalchemy_session = session

        name = factory.Sequence(lambda n: f"team-{n}")

    return TeamFactory


@pytest_asyncio.fixture
async def get_or_create_team_factory(
    session: AsyncSession,
) -> type[AsyncSQLModelFactory]:
    class UniqueTeamFactory(AsyncSQLModelFactory):
        class Meta:
            model = Team
            sqlalchemy_session = session
            sqlalchemy_get_or_create = ("name",)

        name = "Preventers"

    return UniqueTeamFactory


@pytest_asyncio.fixture
async def hero_factory(
    session: AsyncSession, team_factory: type[AsyncSQLModelFactory]
) -> type[AsyncSQLModelFactory]:
    class HeroFactory(AsyncSQLModelFactory):
        class Meta:
            model = Hero
            sqlalchemy_session = session

        name = factory.Sequence(lambda n: f"hero-{n}")
        team = factory.SubFactory(team_factory)

    return HeroFactory
