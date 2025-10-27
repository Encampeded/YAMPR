import json
import os.path
from requests import post
from pathlib import Path
from tinytag import TinyTag
import config

class ImageCache:
    # just a picture of the mpv logo
    DEFAULT_IMAGE = "https://pomf2.lain.la/f/68f8d9nl.png"

    def __init__(self):
        self._image_cache_path = Path(__file__).with_name('image_cache.json')

        if not os.path.exists(self._image_cache_path):
            open(self._image_cache_path, "w").write("{}")

        with self._image_cache_path.open('r') as f:
            self._image_cache = json.load(f)

    @staticmethod
    def _upload(image_data: str):
        match config.UPLOAD_SERVICE:
            case "pomf.lain.la":
                files = {"files[]": ('~/cover.jpg', image_data)}

                print("Uploading...")
                response = post(f"https://pomf2.lain.la/upload.php", files=files)
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

        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        image = song.images.any

        if image is None:
            self._update_cache(cache_key, self.DEFAULT_IMAGE)
            return self.DEFAULT_IMAGE

        print("Uploading...")
        link = self._upload(image.data)
        print("Uploaded Successfully!")

        self._update_cache(cache_key, link)

        return link