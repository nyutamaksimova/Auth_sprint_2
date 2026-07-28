import asyncio

import httpx


async def wait():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://auth-service:8000/docs")

                if response.status_code == 200:
                    print("API is ready")
                    return

        except Exception:
            pass

        print("Waiting API...")
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(wait())