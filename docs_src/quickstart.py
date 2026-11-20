import asyncio

from factories import HeroFactory, TeamFactory, engine, session
from sqlmodel import SQLModel


async def main() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    hero = await HeroFactory.create()
    print(hero.name, hero.secret_name, hero.team.name)

    teammates = await HeroFactory.create_batch(3, team=hero.team)
    print([teammate.team_id for teammate in teammates])

    preventers = await TeamFactory.create(name="Preventers")
    same_team = await TeamFactory.create(name="Preventers")
    print(preventers.id == same_team.id)

    await session.close()
    await engine.dispose()


asyncio.run(main())
