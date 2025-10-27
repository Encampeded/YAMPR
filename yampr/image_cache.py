import json
import os.path
import requests
import pathlib
from tinytag import TinyTag
import config

class ImageCache:
    # just a picture of the mpv logo
    DEFAULT_IMAGE = "https://pomf2.lain.la/f/68f8d9nl.png"

    def __init__(self):
        self._image_cache_path = pathlib.Path(__file__).with_name('image_cache.json')

        if not os.path.exists(self._image_cache_path):
            open(self._image_cache_path, "w").write("{}")

        with self._image_cache_path.open('r') as f:
            self._image_cache = json.load(f)

    @staticmethod
    def _upload(image_data: str):
        match config.UPLOAD_SERVICE:
            case "pomf.lain.la":
                # idk why it needs "~/cover.jpg", but it just doesn't work
                # without it :shrug:
                files = {"files[]": ('~/cover.jpg', image_data)}

                print("Uploading...")
                response = requests.post(f"https://pomf2.lain.la/upload.php", files=files)
                print("Done!\n")

                if response.status_code == 200:
                    return response.json()["files"][0]["url"]
                else:
                    raise ConnectionError("Failed to Upload Cover:", response.text)

            case _:
                raise ValueError("Invalid upload service! Check config.py")

    def _export_cache(self):
        with self._image_cache_path.open('w', encoding="utf-8") as f:
            json.dump(self._image_cache, f, ensure_ascii=False, indent=4)

    def _update_cache(self, value, key):
        self._image_cache[value] = key
        self._export_cache()

    def get(self, song: TinyTag) -> str:
        """Gets a link to the provided song's image. Gets from cache or uploads and adds to cache if not present."""
        cache_key = (song.artist + ' - ' + song.album) if song.album is not None else song.filename

        if cache_key not in self._image_cache:
            image = song.images.any
            link = self.DEFAULT_IMAGE if image is None else self._upload(image.data)
            self._update_cache(cache_key, link)

        return self._image_cache[cache_key]