import dbus

from image_cache import ImageCache
from song import Song
from dbus import DBusConnection
import pypresence
import asyncio
import config
import time

def get_song_info() -> Song:
    pass

async def main():

    #------- Initializing/Setup -------#

    image_cache = ImageCache()
    rpc = pypresence.AioPresence(
        client_id = 1427764951690252308,  # this doesn't actually seem necessary. hmmm.
        loop = asyncio.get_running_loop()
    )

    dbus_connection = dbus.DBusConnection()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(dbus_connection.setup())
        tg.create_task(rpc.connect())
        if config.VERIFY_IMAGES:
            tg.create_task(image_cache.verify_images())

    # ------- Main Loop -------#
    #
    # When properties change...
    #

    while True:
        found_player = asyncio.Event()

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
            rpc.close()




"""
    def on_properties_changed(interface_name, changed_properties, invalidated_properties):
        for changed, variant in changed_properties.items():
            print(f'property changed: {changed} - {variant.value}')

    properties.on_properties_changed(on_properties_changed)

# Listen to signals by defining a callback that takes the args
# specified by the signal definition and registering it on the
# interface with on_[SIGNAL] in snake case.

def changed_notify(new_value):
    print(f'The new value is: {new_value}')

interface.on_changed(changed_notify)
"""

if __name__ == "__main__":
    asyncio.run(main())