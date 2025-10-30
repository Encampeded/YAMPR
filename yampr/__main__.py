from rpc import RichPresence
import asyncio

async def main():
    rpc = RichPresence()
    try:
        await rpc.setup()
        await rpc.loop()

    except asyncio.CancelledError:
        print("Exiting...")

    finally:
        await rpc.takedown()

if __name__ == "__main__":
    asyncio.run(main())