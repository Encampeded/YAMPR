import urllib.parse

class Song:
    """
    Represents a song as seen via MPRIS

    Attributes:
        title: str
        artist: list[str]
        length: int
        file_path: str

        album: str | None
        album_artist: list[str] | None
        track_number: int | None
        disc_number: int | None
        composer: list[str] | None
        lyricist: list[str] | None
        genre: list[str] | None
        release_date: str | None
        image: str | None
    """

    def __init__(self, raw_metadata: dict):
        metadata = {}
        for key, value in raw_metadata.items():
            metadata[key.split(':')[1]] = value.value

        self.title = metadata["title"]
        self.artist = ','.join(metadata["artist"])
        self.length = metadata["length"] / 1000000
        self.file_path = urllib.parse.unquote(metadata["url"])

        self.album = metadata.get("album")
        self.album_artist = metadata.get("albumArtist")
        self.track_number = metadata.get("trackNumber")
        self.disc_number = metadata.get("discNumber")
        self.composer = metadata.get("composer")
        self.lyricist = metadata.get("lyricist")
        self.genre = metadata.get("genre")
        self.release_date = metadata.get("releaseDate")
        self.image = metadata.get("image")