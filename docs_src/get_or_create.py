import asyncio

from factories import TeamFactory, engine, session
from models import Team
from sqlmodel import SQLModel, select


async def main() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    first = await TeamFactory.create(name="Preventers", headquarters="Sharp Tower")
    second = await TeamFactory.create(name="Preventers", headquarters="Elsewhere")
    print(first.id == second.id, second.headquarters)

    teams = (await session.exec(select(Team))).all()
    print(len(teams))

    await session.close()
    await engine.dispose()


asyncio.run(main())
