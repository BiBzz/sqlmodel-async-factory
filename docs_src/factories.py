import factory
from models import Hero, Team
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlmodel_async_factory import AsyncSQLModelFactory

engine = create_async_engine("sqlite+aiosqlite:///:memory:")
session = AsyncSession(engine, expire_on_commit=False)


class TeamFactory(AsyncSQLModelFactory):
    class Meta:
        model = Team
        sqlalchemy_session = session
        sqlalchemy_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"team-{n}")
    headquarters = factory.Faker("city")


class HeroFactory(AsyncSQLModelFactory):
    class Meta:
        model = Hero
        sqlalchemy_session = session

    name = factory.Sequence(lambda n: f"hero-{n}")
    secret_name = factory.LazyAttribute(lambda hero: f"{hero.name} in disguise")
    team = factory.SubFactory(TeamFactory)
