import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from async_factory_boy import AsyncSQLModelFactory
from tests.conftest import Hero, Team


async def test_create_returns_a_persisted_instance(
    session: AsyncSession, team_factory: type[AsyncSQLModelFactory]
) -> None:
    team = await team_factory.create()

    assert isinstance(team, Team)
    assert team.id is not None

    stored = (await session.exec(select(Team))).all()
    assert [row.id for row in stored] == [team.id]


async def test_declarations_are_evaluated(
    team_factory: type[AsyncSQLModelFactory],
) -> None:
    first = await team_factory.create()
    second = await team_factory.create()

    assert first.name != second.name
    assert first.name.startswith("team-")


async def test_explicit_kwargs_override_declarations(
    team_factory: type[AsyncSQLModelFactory],
) -> None:
    team = await team_factory.create(name="Preventers")

    assert team.name == "Preventers"


async def test_create_batch_persists_every_object(
    session: AsyncSession, team_factory: type[AsyncSQLModelFactory]
) -> None:
    teams = await team_factory.create_batch(3)

    assert len(teams) == 3
    assert len({team.id for team in teams}) == 3

    stored = (await session.exec(select(Team))).all()
    assert len(stored) == 3


async def test_subfactory_yields_a_model_instance_not_a_task(
    session: AsyncSession, hero_factory: type[AsyncSQLModelFactory]
) -> None:
    hero = await hero_factory.create()

    assert isinstance(hero, Hero)
    assert isinstance(hero.team, Team)
    assert hero.team_id == hero.team.id

    stored_teams = (await session.exec(select(Team))).all()
    assert len(stored_teams) == 1


async def test_subfactory_accepts_an_already_built_parent(
    hero_factory: type[AsyncSQLModelFactory],
    team_factory: type[AsyncSQLModelFactory],
) -> None:
    team = await team_factory.create()
    hero = await hero_factory.create(team=team)

    assert hero.team_id == team.id


async def test_get_or_create_reuses_the_existing_row(
    session: AsyncSession, get_or_create_team_factory: type[AsyncSQLModelFactory]
) -> None:
    first = await get_or_create_team_factory.create()
    second = await get_or_create_team_factory.create()

    assert first.id == second.id

    stored = (await session.exec(select(Team))).all()
    assert len(stored) == 1


async def test_get_or_create_without_the_key_field_is_an_error(
    session: AsyncSession,
) -> None:
    class BrokenFactory(AsyncSQLModelFactory):
        class Meta:
            model = Team
            sqlalchemy_session = session
            sqlalchemy_get_or_create = ("name",)

    with pytest.raises(Exception, match="sqlalchemy_get_or_create"):
        await BrokenFactory.create()
