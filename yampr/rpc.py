import pypresence
import time
from song import Song
from image_cache import ImageCache
from dbus import DBusConnection
import asyncio
from .song import Song
from .image_cache import ImageCache
from .mpris_dbus import DBusConnection
from . import config

class RichPresence:

    def __init__(self):
        self._image_cache = ImageCache()
        self._rpc = pypresence.AioPresence(
            client_id = 1427764951690252308,  # this doesn't actually seem necessary. hmmm.
            loop = asyncio.get_running_loop()
        )
        self._dbus_connection = DBusConnection()

        self.song: Song | None = None
        self.position = 0.0
        self.image = ""


    async def setup(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._dbus_connection.setup())
            tg.create_task(self._rpc.connect())
            if config.VERIFY_IMAGES:
                tg.create_task(self._image_cache.verify_images())

    async def get_song(self):
        self.song = await self._dbus_connection.get_song()
        self.image = await self._image_cache.get(self.song)

    async def get_position(self):
        self.position = await self._dbus_connection.get_position()

    async def update(self):

        def try_get(value: str):
            return getattr(self.song, value, value)

        await self._rpc.update(
            activity_type=pypresence.ActivityType.LISTENING,
            name=try_get(config.LISTENING_TO),

            details=try_get(config.TITLE),
            state=try_get(config.SUBTITLE),

            start=round(time.time() - self.position),
            end=round(time.time() - self.position + self.song.length),

            large_image=self.image,
            large_text=try_get(config.IMAGE_LABEL)
        )

    async def cycle(self):
        print("\nFinding Player...")
        await self._dbus_connection.find_player()

        while self._dbus_connection.player_playing:

            print("Getting info...")
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.get_song()) # noqa
                tg.create_task(self.get_position())

            print("Updating and awaiting properties change...")
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.update())
                tg.create_task(self._dbus_connection.properties_change.wait())

            print("Properties changed!")
            await self._rpc.clear()
            self._dbus_connection.properties_change.clear()

    async def loop(self):
        while True:
            await self.cycle()

    async def takedown(self):
        await self._rpc.clear()


