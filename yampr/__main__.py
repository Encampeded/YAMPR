from .rpc import MPresence
import asyncio

async def main():
    rpc = MPresence()

    try:
        await rpc.setup()

        while True:
            await rpc.cycle()

    except asyncio.CancelledError:
        print("Exiting...")

    finally:
        await rpc.clear()


if __name__ == "__main__":
    asyncio.run(main())