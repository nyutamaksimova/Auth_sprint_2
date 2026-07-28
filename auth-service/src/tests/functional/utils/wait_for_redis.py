import asyncio

from redis.asyncio import Redis

TIMEOUT = 60

async def wait_for_redis():
    redis_client = Redis(
        host='redis',
        port=6379,
    )

    start_time = asyncio.get_running_loop().time()

    while True:
        try:
            if await redis_client.ping():
                break
        except Exception:
            pass

        if asyncio.get_running_loop().time() - start_time > TIMEOUT:
            raise TimeoutError(
                f'Redis did not become ready within {TIMEOUT} seconds'
            )

        await asyncio.sleep(1)

    await redis_client.aclose()


if __name__ == '__main__':
    asyncio.run(wait_for_redis())