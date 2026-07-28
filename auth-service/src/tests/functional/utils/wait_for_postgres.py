import asyncio

import asyncpg

from src.core.config import settings


async def wait():

    while True:

        try:

            conn = await asyncpg.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
            )

            await conn.close()

            print("Postgres is ready")

            return

        except Exception:

            print("Waiting Postgres...")

            await asyncio.sleep(1)


asyncio.run(wait())