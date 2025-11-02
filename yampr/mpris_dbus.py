import asyncio
import dbus_fast.aio
import dbus_fast.introspection
from .song import Song
from pprint import pprint

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

        self.song = Song()
        self.position: float | None = 0.0
        self.player_stopped = asyncio.Event()

    async def _get_proxy(self, name, path):
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

        dbus_proxy = await self._get_proxy(
            self.DBUS_NAME,
            self.DBUS_PATH
        )

        self._dbus = dbus_proxy.get_interface(self.DBUS_NAME)


    def _update_song(self, _, changed_properties: dict, invalidate_properties):
        #  and \
        #             changed_properties["PlaybackStatus"].value != "Playing"
        if "PlaybackStatus" in changed_properties:
            self.player_stopped.set()

        else:
            metadata = changed_properties["Metadata"].value

            self.song.update_from_properties(metadata)
            self.position = 0.0
            # I wonder if we actually can assume ChangedProperties always means
            # a new song, in the case it's not PlaybackStatus... Whelp!

    def _update_position(self, position):
        self.position = position / 1000000


    async def find_player(self):
        while True:
            names = await self._dbus.call_list_names()
            mpris_names = [ name for name in names if name.startswith(self.MPRIS_NAME) ]

            for name in mpris_names:

                player_object = await self._get_proxy(
                    name,
                    self.MPRIS_PATH
                )

                player = player_object.get_interface("org.mpris.MediaPlayer2.Player")

                if await player.get_playback_status() != "Playing":
                    continue

                metadata = await player.get_metadata()
                if not metadata["xesam:url"].value.startswith("file://"):
                    continue

                self.song.update_from_properties(metadata)

                self._player = player
                self._player.on_seeked(self._update_position)
                self._update_position(await self._player.get_position())

                self._properties = player_object.get_interface("org.freedesktop.DBus.Properties")
                self._properties.on_properties_changed(self._update_song)

                return

            await asyncio.sleep(5)

    async def cycle(self):
        while True:
            print("Finding Player...")
            await self.find_player()
            print("Found player! Awaiting player_stopped()")
            await self.player_stopped.wait()

            self.player_stopped.clear()