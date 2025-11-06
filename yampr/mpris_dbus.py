import asyncio
import time
import dbus_fast.aio
import dbus_fast.introspection
from .song import Song
from .config import REQUIRED_PATH

class DBusConnection:

    DBUS_NAME = "org.freedesktop.DBus"
    DBUS_PATH = "/org/freedesktop/DBus"

    MPRIS_NAME = "org.mpris.MediaPlayer2"
    MPRIS_PATH = "/org/mpris/MediaPlayer2"
    MPRIS_PLAYER = "org.mpris.MediaPlayer2.Player"

    def __init__(self):
        self._bus = dbus_fast.aio.MessageBus()
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
        await self._bus.connect()

        dbus_proxy = await self._get_proxy(
            self.DBUS_NAME,
            self.DBUS_PATH
        )

        self._dbus = dbus_proxy.get_interface(self.DBUS_NAME)


    def _update_song(self, _, changed_properties: dict, __):
        print("Received PropertiesChanged!")

        if "PlaybackStatus" in changed_properties:
            self.player_playing = False

        elif "Metadata" in changed_properties:
            metadata = changed_properties["Metadata"].value
            self.song.update_from_metadata(metadata)
            self._update_position(0)
            # If the metadata changes, it implies we've moved onto a new song,
            # meaning we can just set the position to 0.

        else:
            # Otherwise, we don't care about stuff like shuffling being enabled. So just return.
            return

        self.properties_changed.set()

    def _update_position(self, position: int):
        print("Received Seeked! (or PropertiesChange)")
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

                # Only allow music in a certain folder
                if not metadata["xesam:url"].value[7:].startswith(REQUIRED_PATH):
                    continue

                # Only allow music with actual metadata
                if not all(key in metadata for key in ("xesam:title", "xesam:artist", "mpris:length")):
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
                self.song.update_from_metadata(metadata)
                self.player_playing = True

                return

            await asyncio.sleep(5)