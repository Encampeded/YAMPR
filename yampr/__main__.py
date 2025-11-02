from .rpc import MPresence
import asyncio

async def main():
    rpc = MPresence()

    try:
        await rpc.setup()
        await rpc.loop()

    except asyncio.CancelledError:
        print("Exiting...")

    finally:
        await rpc.clear()

if __name__ == "__main__":
    asyncio.run(main())