import pypresence
import time
import asyncio
from .image_cache import ImageCache
from .mpris_dbus import DBusConnection
from . import config

class MPresence:

    def __init__(self):
        self._image_cache = ImageCache()
        self._rpc = pypresence.AioPresence(
            client_id = 1427764951690252308,
            loop = asyncio.get_running_loop()
        )
        self._dbus_connection = DBusConnection()

    async def setup(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._dbus_connection.setup())
            tg.create_task(self._rpc.connect())
            if config.VERIFY_IMAGES:
                tg.create_task(self._image_cache.verify_images())

    async def update(self):
        song = self._dbus_connection.song
        image_link = await self._image_cache.get(song)
        position = self._dbus_connection.get_position()

        def try_format(string: str):
            return getattr(song, string, string)

        await self._rpc.update(
            activity_type=pypresence.ActivityType.LISTENING,
            name=try_format(config.LISTENING_TO),

            details=try_format(config.TITLE),
            state=try_format(config.SUBTITLE),

            start=round(time.time() - position),
            end=round(time.time() - position + song.length),

            large_image=image_link,
            large_text=try_format(config.IMAGE_LABEL)
        )

    async def cycle(self):
        print("Awaiting player...")
        await self._dbus_connection.find_player()
        print("    Found Player!")

        while self._dbus_connection.player_playing:
            print("\nAwaiting MPRIS Update...")
            await self._dbus_connection.properties_changed.wait()
            self._dbus_connection.properties_changed.clear()
            print("    MPRIS Updated!")

            print("Updating Rich Presence...")
            await self.update()
            print("    Rich Presence Updated!")

            print("Sleeping...")
            await asyncio.sleep(15)

        await self._rpc.clear()

    async def teardown(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._rpc.clear())
            tg.create_task(self._image_cache.close())