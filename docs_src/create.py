import asyncio

from factories import HeroFactory, TeamFactory, engine, session
from sqlmodel import SQLModel


async def main() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    team = await TeamFactory.create()
    print(team.id, team.name)

    preventers = await TeamFactory.create(name="Preventers")
    print(preventers.id, preventers.name)

    heroes = await HeroFactory.create_batch(2, age=30)
    print([(hero.name, hero.age) for hero in heroes])

    rusty = await HeroFactory.create(name="Rusty-Man", team__name="Avengers")
    print(rusty.secret_name, rusty.team.name)

    await session.close()
    await engine.dispose()


asyncio.run(main())
