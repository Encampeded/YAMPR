import json
from time import time
from uploader import Uploader
from pathlib import Path
from tinytag import TinyTag

class ImageCache:
    DEFAULT_IMAGE = "https://pomf2.lain.la/f/68f8d9nl.png"

    def __init__(self):
        self._image_cache_path = Path(__file__).with_name('image_cache.json')
        self._uploader = Uploader()

        with self._image_cache_path.open('r') as f:
            self._image_cache = json.load(f)

    def _export_cache(self):
        with self._image_cache_path.open('w', encoding="utf-8") as f:
            json.dump(self._image_cache, f, ensure_ascii=False, indent=4)

    def _update_cache(self, value, key):
        self._image_cache[value] = key
        self._export_cache()

    def get(self, song: TinyTag) -> str:
        """Gets a link to the provided song's image. Gets from cache or uploads and adds to cache if not in."""
        cache_key = (song.artist + ' ' + song.album) if song.album is not None else song.filename

        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        image = song.images.any

        if image is None:
            self._update_cache(cache_key, self.DEFAULT_IMAGE)
            return self.DEFAULT_IMAGE

        link = self._uploader.upload(image.data)

        self._update_cache(cache_key, link)

        return link