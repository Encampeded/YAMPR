import asyncio
import json
import httpx
import base64
import os.path
from .config import UPLOAD_SERVICE

class ImageCache:
    # just a picture of the mpv logo
    DEFAULT_IMAGE = "https://pomf2.lain.la/f/68f8d9nl.png"

    def __init__(self):
        self._client: httpx.AsyncClient = httpx.AsyncClient()

        # This feels fucky yucky
        self._path: str = '/'.join(__file__.split('/')[:-1] + ["image_cache.json"])

        if not os.path.exists(self._path):
            open(self._path, "w").write("{}")

        with open(self._path, 'r') as f:
            self._image_cache: dict = json.load(f)

    def _export_cache(self):
        """Saves self._image_cache to the json file"""
        with open(self._path, 'w', encoding="utf-8") as f:
            json.dump(self._image_cache, f, ensure_ascii=False, indent=4)

    async def _upload(self, image_data: str) -> str:
        """Uploads given image data and returns the link."""
        print("Uploading image...")
        image_data = base64.b64decode(image_data[23:])

        link = ""
        # IMPORTANT: If implementing a new upload service, check the rate limiting
        # and adjust verify_images accordingly.
        match UPLOAD_SERVICE:
            case "pomf.lain.la":
                # Without "~/cover.jpg" it just doesn't upload. Not sure why
                files = {"files[]": ('~/cover.jpg', image_data)}

                response = await self._client.post(f"https://pomf2.lain.la/upload.php", files=files)

                if response.status_code == 200:
                    link = response.json()["files"][0]["url"]
                else:
                    raise ConnectionError("Failed to Upload Cover:", response.text)

            case _:
                raise ValueError("Invalid upload service! Check config.py")

        print("    Uploaded!")
        return link

    async def get(self, song) -> str:
        """Returns link to the provided song's image. Gets from cache or uploads and adds to cache if not present."""
        artist = song.album_artist if song.album_artist is not None else song.artist

        cache_key = song.file_path if song.album is None else (artist + ' - ' + song.album)

        if cache_key not in self._image_cache:
            link = self.DEFAULT_IMAGE if song.image is None else await self._upload(song.image)
            self._image_cache[cache_key] = link
            self._export_cache()

        return self._image_cache[cache_key]


    # Supply the number of images. If less than 800, just run it all.
    # If more than 800... Tell the user... Because Yikes...
    async def verify_images(self):
        image_cache_size = len(self._image_cache)

        # pomf.lain.la rate limits at 1 link per second, with a buffer of 800 requests.
        # To play it safe, we limit it 500
        if image_cache_size >= 500:
            print("Image cache has", image_cache_size, "links, which is more than 500")
            print("Verification will not commence, as it would be too slow/you'd get rate limited/im lazy.")
            print("Please clean up your cache, or clear it entirely.")
            return

        responses = {}

        async def get(key: str, link: str) -> None: # noqa
            response = await self._client.get(link) # noqa
            responses[key] = response

        with asyncio.TaskGroup() as tg:
            for key, link in self._image_cache.items():
                tg.create_task(get(key, link))

        for key, response in self._image_cache.copy().items():
            if response.status_code == 404:
                print("Removed", key)
                self._image_cache.pop(key)
            elif response.status_code != 200:
                raise ValueError("Received other response code", response.status_code)

        self._export_cache()