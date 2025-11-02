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
            client_id = 1427764951690252308,  # this doesn't actually seem necessary. hmmm.
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
        position = self._dbus_connection.position
        song = self._dbus_connection.song
        image_link = await self._image_cache.get(song)

        def try_get(value: str):
            return getattr(song, value, value)

        await self._rpc.update(
            activity_type=pypresence.ActivityType.LISTENING,
            name=try_get(config.LISTENING_TO),

            details=try_get(config.TITLE),
            state=try_get(config.SUBTITLE),

            start=round(time.time() - position),
            end=round(time.time() - position + song.length),

            large_image=image_link,
            large_text=try_get(config.IMAGE_LABEL)
        )

    async def cycle(self):
        # To give dbus_connection time to update song
        await asyncio.sleep(1)

        while True:

            if not self._dbus_connection.player_stopped.is_set():
                print("Updating...")
                await self.update()
            else:
                print("No player!")
                await self._rpc.clear()

            print("Waiting 15s...\n")
            await asyncio.sleep(15)

    async def loop(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._dbus_connection.cycle())
            tg.create_task(self.cycle())

    async def clear(self):
        await self._rpc.clear()


