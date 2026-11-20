from collections.abc import AsyncIterator

import factory
import pytest_asyncio
from models import Hero, Team
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlmodel_async_factory import AsyncSQLModelFactory


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
        headquarters = factory.Faker("city")

    return TeamFactory


@pytest_asyncio.fixture
async def hero_factory(
    session: AsyncSession, team_factory: type[AsyncSQLModelFactory]
) -> type[AsyncSQLModelFactory]:
    class HeroFactory(AsyncSQLModelFactory):
        class Meta:
            model = Hero
            sqlalchemy_session = session

        name = factory.Sequence(lambda n: f"hero-{n}")
        secret_name = factory.LazyAttribute(lambda hero: f"{hero.name} in disguise")
        team = factory.SubFactory(team_factory)

    return HeroFactory
