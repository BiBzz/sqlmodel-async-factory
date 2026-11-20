import asyncio

from factories import HeroFactory, TeamFactory, engine, session
from sqlmodel import SQLModel


async def main() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    heroes = await HeroFactory.create_batch(2)
    print([hero.team.name for hero in heroes])

    preventers = await TeamFactory.create(name="Preventers")
    deadpond = await HeroFactory.create(team=preventers)
    print(deadpond.team_id == preventers.id)

    spider_boy = await HeroFactory.create(team=TeamFactory.create(name="Z-Force"))
    print(spider_boy.team.name)

    await session.close()
    await engine.dispose()


asyncio.run(main())
