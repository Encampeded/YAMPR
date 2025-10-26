import time
import atexit
from urllib.parse import unquote
from pydbus import SessionBus
from pypresence import Presence
from pypresence import ActivityType, StatusDisplayType
from tinytag import TinyTag
from image_cache import ImageCache

class RichMPresenceV:

    def __init__(self):
        self._image_cache = ImageCache()
        self._bus = SessionBus()
        self._player = None

        self._RPC = Presence(1427764951690252308)
        self._RPC.connect()
        self._RPC.clear()

        self.playing = False
        self.position = 0.0
        self.large_image = ""
        self.song = TinyTag()

    # --------------------------------------------------------------------------------------------------------- #

    def scan_for_player(self) -> bool:
        players = self._bus.get("org.freedesktop.DBus", "/org/freedesktop/DBus").ListNames()
        self._player = None

        for player_name in players:

            if not player_name.startswith("org.mpris.MediaPlayer2.mpv"):
                continue

            player = self._bus.get(player_name, "/org/mpris/MediaPlayer2")

            if player.PlaybackStatus == "Paused":
                continue

            self._player = player
            return True

        return False

    # --------------------------------------------------------------------------------------------------------- #

    def set_song_info(self):
        path = unquote(self._player.Metadata["xesam:url"])[7:]

        if not TinyTag.is_supported(path) or not path.startswith(""):
            return

        self.song = TinyTag.get(path, image=True)
        for attr in ["title", "artist"]:
            if getattr(self.song, attr) is None:
                return

        self.playing = True

        self.position = self._player.Position / 1000000
        self.large_image = self._image_cache.get(self.song)

    # --------------------------------------------------------------------------------------------------------- #

    def update(self):
        self._RPC.update(
            activity_type = ActivityType.LISTENING,
            status_display_type = StatusDisplayType.NAME,

            details = self.song.title,
            state = self.song.artist,

            start = time.time() - self.position,
            end   = time.time() - self.position + self.song.duration,

            large_image = self.large_image,
            large_text = self.song.album,
        )

    # --------------------------------------------------------------------------------------------------------- #

    def refresh(self) -> float:
        sleep_time = 15
        self.scan_for_player()

        if self._player is None:
            self.playing = False
            return sleep_time

        self.set_song_info()

        if not self.playing:
            return sleep_time

        self.update()
        print("Cycle completed!\n")

        return min(15.0, self.song.duration - self.position)

    # --------------------------------------------------------------------------------------------------------- #

    def _exit_rpc(self):
        self._RPC.clear()
        self._RPC.close()

    def loop(self):
        atexit.register(rpc._exit_rpc)

        try:
            while True:
                sleep_time = rpc.refresh()

                if not self.playing:
                    self._RPC.clear()
                    print("Waiting for playback...")

                time.sleep(sleep_time)

        finally:
            self._exit_rpc()

if __name__ == "__main__":
    rpc = RichMPresenceV()
    rpc.loop()


