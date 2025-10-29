import json
import httpx
import pathlib
import os.path
import config

class ImageCache:
    # just a picture of the mpv logo
    DEFAULT_IMAGE = "https://pomf2.lain.la/f/68f8d9nl.png"

    def __init__(self):
        self._client = httpx.AsyncClient()

        self._image_cache_path = pathlib.Path(__file__).with_name('image_cache.json')

        if not os.path.exists(self._image_cache_path):
            open(self._image_cache_path, "w").write("{}")

        with self._image_cache_path.open('r') as f:
            self._image_cache = json.load(f)

    def _export_cache(self):
        with self._image_cache_path.open('w', encoding="utf-8") as f:
            json.dump(self._image_cache, f, ensure_ascii=False, indent=4)

    async def _upload(self, image_data: str) -> str:
        print("Uploading...")

        link = ""
        match config.UPLOAD_SERVICE:
            case "pomf.lain.la":
                # Without "~/cover.jpg" it just doesn't upload
                # Not sure why
                files = {"files[]": ('~/cover.jpg', image_data)}

                response = await self._client.post(f"https://pomf2.lain.la/upload.php", files=files)

                if response.status_code == 200:
                    link = response.json()["files"][0]["url"]
                else:
                    raise ConnectionError("Failed to Upload Cover:", response.text)

            case _:
                raise ValueError("Invalid upload service! Check config.py")

        print("Uploaded!\n")
        return link

    async def get(self, song) -> str:
        """Gets a link to the provided song's image. Gets from cache or uploads and adds to cache if not present."""
        cache_key = (song.artist + ' - ' + song.album) if song.album is not None else song.file_path

        if cache_key not in self._image_cache:
            link = self.DEFAULT_IMAGE if song.image is None else await self._upload(song.image)
            self._image_cache[cache_key] = link
            self._export_cache()

        return self._image_cache[cache_key]

    async def verify_images(self):
        for i, (key, link) in enumerate(self._image_cache.copy().items()):
            print(f"{i:02d}/{len(self._image_cache)}", end=" ")

            response = await self._client.get(link)

            if response.status_code == 404:
                print(key + " doesn't exist! Removing...")
                self._image_cache.pop(key)

            print("", end = '\r')

        self._export_cache()