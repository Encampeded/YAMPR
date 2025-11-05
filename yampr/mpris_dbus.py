import asyncio
import time
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

        self.song: Song  = Song()
        self.position = 0.0
        self.position_updated = 0.0
        self.player_playing = False
        self.properties_changed = asyncio.Event()

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


    def _set_song(self, metadata: dict):
        self.song.update_from_metadata(metadata)

    def _update_song(self, _, changed_properties: dict, __):
        print("Received PropertiesChanged!")
        if "PlaybackStatus" in changed_properties:
            self.player_playing = False

        else:
            metadata = changed_properties["Metadata"].value
            #print(metadata)
            self._set_song(metadata)
            self._update_position(0)
            # If the properties change, it implies we've moved onto a new song,
            # meaning we can just set the position to 0.

        self.properties_changed.set()

    def _update_position(self, position: int):
        print("Received Seeked!")
        self.position = position / 1000000
        self.position_updated = time.perf_counter()
        self.properties_changed.set()

    def get_position(self) -> float:
        offset = time.perf_counter() - self.position_updated
        return self.position + offset

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

                # Only allow playing music, so we don't get stuck on forgotten paused instances
                if await player.get_playback_status() != "Playing":
                    continue

                # Only allow local music
                metadata = await player.get_metadata()
                if not metadata["xesam:url"].value.startswith("file://"):
                    continue

                if "xesam:artist" not in metadata:
                    continue

                # Set our interfaces
                self._player = player
                self._properties = player_object.get_interface("org.freedesktop.DBus.Properties")

                # Set our signal runners
                self._properties.on_properties_changed(self._update_song)
                self._player.on_seeked(self._update_position)

                # Get/Set our new stuff
                position = await self._player.get_position()
                self._update_position(position)
                metadata = await self._player.get_metadata()
                self._set_song(metadata)
                self.player_playing = True

                return

            await asyncio.sleep(5)