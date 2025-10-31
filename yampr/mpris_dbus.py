import asyncio
import dbus_fast.aio
import dbus_fast.introspection
from .song import Song

class DBusConnection:
    DBUS_NAME = "org.freedesktop.DBus"
    DBUS_PATH = "/org/freedesktop/DBus"

    MPRIS_NAME = "org.mpris.MediaPlayer2"
    MPRIS_PATH = "/org/mpris/MediaPlayer2"
    MPRIS_PLAYER = "org.mpris.MediaPlayer2.Player"

    def __init__(self):
        self._bus = None
        self._dbus = None
        self._player = None
        self._properties = None

        self.player_playing = True
        self.properties_change = asyncio.Event()

    async def get_proxy(self, name, path):
        return self._bus.get_proxy_object(
            name,
            path,
            await self._bus.introspect(
                name,
                path
            )
        )

    async def setup(self):
        self._bus = await dbus_fast.aio.MessageBus().connect()

        dbus_proxy = await self.get_proxy(
            self.DBUS_NAME,
            self.DBUS_PATH
        )

        self._dbus = dbus_proxy.get_interface(self.DBUS_NAME)


    def _check_playing (self, _, changed_properties, __):
        self.properties_change.set()

        if "PlaybackStatus" in changed_properties:
            self.player_playing = False


    async def find_player(self):
        while True:
            names = await self._dbus.call_list_names()
            mpris_names = [ name for name in names if name.startswith(self.MPRIS_NAME) ]

            for name in mpris_names:

                player_object = await self.get_proxy(
                    name,
                    self.MPRIS_PATH
                )

                player = player_object.get_interface("org.mpris.MediaPlayer2.Player")

                if await player.get_playback_status() != "Playing":
                    continue

                self._player = player
                self._properties = player_object.get_interface("org.freedesktop.DBus.Properties")
                self._properties.on_properties_changed(self._check_playing)
                self.player_playing = True

                return

            await asyncio.sleep(10)


    async def get_song(self) -> Song:
        metadata = await self._player.get_metadata()
        return Song(metadata)

    async def get_position(self) -> float:
        return await self._player.get_position() / 1000000