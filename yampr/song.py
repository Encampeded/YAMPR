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
        album_artist: str | None
        track_number: int | None
        disc_number: int | None
        composer: str | None
        lyricist: str | None
        genre: str | None
        release_date: str | None
        image: str | None
    """

    def __init__(self, raw_metadata: dict):
        metadata = {}
        for key, value in raw_metadata.items():
            metadata[key.split(':')[1]] = value.value

        def list_get(attribute):
            """Converts list of strings to string representation if exists."""
            value = metadata.get(attribute)
            return None if value is None else ', '.join(value)

        self.title = metadata["title"]
        self.artist = list_get("artist")
        self.length = metadata["length"] / 1000000
        self.file_path = urllib.parse.unquote(metadata["url"])

        self.album = metadata.get("album")
        self.album_artist = list_get("albumArtist")
        self.track_number = metadata.get("trackNumber")
        self.disc_number = metadata.get("discNumber")
        self.composer = list_get("composer")
        self.lyricist = list_get("lyricist")
        self.genre = list_get("genre")
        self.release_date = metadata.get("releaseDate")
        self.image = metadata.get("artUrl")