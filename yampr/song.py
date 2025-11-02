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

    @classmethod
    def to_object_dict(cls, raw_metadata: dict):
        return { key.split(':')[1]: value.value for key, value in raw_metadata.items() }

    def __init__(self):
        self.metadata = {}

        self.title = ""
        self.artist = ""
        self.length = 0
        self.file_path = ""

        self.album = None
        self.album_artist = None
        self.track_number = None
        self.disc_number = None
        self.composer = None
        self.lyricist = None
        self.genre = None
        self.release_date = None
        self.image = None

    def list_get(self, attribute):
        value = self.metadata.get(attribute)
        return None if value is None else ', '.join(value)

    def update_from_properties(self, raw_metadata: dict):
        self.metadata.update(self.to_object_dict(raw_metadata))

        self.title = self.metadata["title"]
        self.artist = self.list_get("artist")
        self.length = self.metadata["length"] / 1000000
        self.file_path = urllib.parse.unquote(self.metadata["url"])

        self.album = self.metadata.get("album")
        self.album_artist = self.list_get("albumArtist")
        self.track_number = self.metadata.get("trackNumber")
        self.disc_number = self.metadata.get("discNumber")
        self.composer = self.list_get("composer")
        self.lyricist = self.list_get("lyricist")
        self.genre = self.list_get("genre")
        self.release_date = self.metadata.get("releaseDate")
        self.image = self.metadata.get("artUrl")

    def __repr__(self):
        return ", ".join([self.title, self.album, self.artist])