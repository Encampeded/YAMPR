import pypresence
#import pydbus
import dasbus.connection
import time
import urllib.parse
from tinytag import TinyTag
from image_cache import ImageCache
import config

class RichPresence:

    def __init__(self):
        self._image_cache = ImageCache()
        self._bus = dasbus.connection.SessionMessageBus()
        self._player = None
        self._player_metadata = {}

        self._RPC = pypresence.Presence(1427764951690252308)
        self._RPC.connect()
        self._RPC.clear()

        self.position = 0.0
        self.large_image = ""
        self.song = TinyTag()

    def scan_for_player(self) -> bool:

        names = self._bus.get_proxy("org.freedesktop.DBus",
                                "/org/freedesktop/DBus").ListNames()

        players = [ name[23:] for name in names if name.startswith("org.mpris.MediaPlayer2") ]

        self._player = None

        for player_name in players:

            player = self._bus.get_proxy(
                "org.mpris.MediaPlayer2." + player_name,
                "/org/mpris/MediaPlayer2",
                "org.freedesktop.DBus.Properties"
            )

            playback_status = player.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus").unpack()

            if playback_status == "Stopped":
                continue

            self._player_metadata = player.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            self._player = player

            return True

        return False

    def get_song_info(self) -> bool:

        #print(self._player.Metadata)

        # I theorize this is necessary if the user is streaming music through vlc
        # Untested theory, but shush
        raw_path = self._player_metadata["xesam:url"]
        if not raw_path.startswith("file://"):
            return False

        path = urllib.parse.unquote(raw_path[7:])

        if not TinyTag.is_supported(path) or not path.startswith(config.REQUIRED_PATH):
            return False

        self.song = TinyTag.get(path, image=True)
        for attr in ["title", "artist"]:
            if getattr(self.song, attr) is None:
                return False

        self.position = self._player.Get("org.mpris.MediaPlayer2.Player", "Position").unpack() // 1000000
        self.large_image = self._image_cache.get(self.song)

        return True

    def update(self):

        def try_get(value: str) -> str:
            return getattr(self.song, value, value)

        self._RPC.update(
            activity_type = pypresence.ActivityType.LISTENING,
            name = try_get(config.LISTENING_TO),

            details = try_get(config.TITLE),
            state = try_get(config.SUBTITLE),

            start = time.time() - self.position,
            end   = time.time() - self.position + self.song.duration,

            large_image = self.large_image,
            large_text = try_get(config.IMAGE_LABEL)
        )

    def refresh(self) -> float:
        default_sleep = 15.0

        if not self.scan_for_player() or not self.get_song_info():
            self._RPC.clear()
            return default_sleep

        self.update()

        return min(default_sleep, self.song.duration - self.position)

    def _exit_rpc(self):
        self._RPC.clear()
        self._RPC.close()

    def loop(self):
        try:
            while True:
                sleep_time = self.refresh()
                time.sleep(sleep_time)

        finally:
            self._exit_rpc()
