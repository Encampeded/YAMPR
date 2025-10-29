import pypresence
import time
import asyncio
from dbus import DBusConnection
from image_cache import ImageCache
from song import Song
import config

async def main():

    #------- Initializing/Setup -------#

    image_cache = ImageCache()
    rpc = pypresence.AioPresence(
        client_id = 1427764951690252308,  # this doesn't actually seem necessary. hmmm.
        loop = asyncio.get_running_loop()
    )

    dbus_connection = DBusConnection()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(dbus_connection.setup())
        tg.create_task(rpc.connect())
        if config.VERIFY_IMAGES:
            tg.create_task(image_cache.verify_images())


    while True: # ------- Main Loop -------#

        try:
            print("Waiting for player...")
            await dbus_connection.find_player()
            print("Found!")

            while dbus_connection.player_playing:

                print("Getting info...")
                async with asyncio.TaskGroup() as tg:
                    get_song = tg.create_task(dbus_connection.get_song())
                    get_position = tg.create_task(dbus_connection.get_position())

                song = get_song.result()
                position = get_position.result()

                def try_get(value: str) -> str:
                    return getattr(song, value, value)

                print("Updating and waiting...")
                async with asyncio.TaskGroup() as tg:

                    tg.create_task(rpc.update(
                        activity_type=pypresence.ActivityType.LISTENING,
                        name=try_get(config.LISTENING_TO),

                        details=try_get(config.TITLE),
                        state=try_get(config.SUBTITLE),

                        start=round(time.time() - position),
                        end=round(time.time() - position + song.length),

                        large_image= await image_cache.get(song),
                        large_text=try_get(config.IMAGE_LABEL)
                    ))

                    tg.create_task(dbus_connection.properties_change.wait())
                print("Properties Changed!")

        finally:
            await dbus_connection.close()
            #asyncio.get_running_loop().close()
            rpc.close()

if __name__ == "__main__":
    asyncio.run(main())