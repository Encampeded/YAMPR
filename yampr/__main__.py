from rpc import RichPresence
import asyncio

async def main():
    rpc = RichPresence()
    try:
        await rpc.setup()

        while True:
            await rpc.cycle()

    finally:
        rpc.takedown()
        asyncio.get_running_loop().close()

if __name__ == "__main__":
    asyncio.run(main())