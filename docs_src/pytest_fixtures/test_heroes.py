from models import Hero, Team
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlmodel_async_factory import AsyncSQLModelFactory


async def test_hero_belongs_to_a_team(
    hero_factory: type[AsyncSQLModelFactory],
) -> None:
    hero = await hero_factory.create()
    assert hero.team.name.startswith("team-")

    heroes = await hero_factory.create_batch(3, team=hero.team)
    assert all(other.team_id == hero.team_id for other in heroes)


async def test_each_test_starts_from_an_empty_database(
    session: AsyncSession, hero_factory: type[AsyncSQLModelFactory]
) -> None:
    await hero_factory.create()

    assert len((await session.exec(select(Hero))).all()) == 1
    assert len((await session.exec(select(Team))).all()) == 1
