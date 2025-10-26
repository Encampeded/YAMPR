from requests import post

class Uploader:

    @staticmethod
    def _pomf_upload(image_data: str, domain: str):
        files = {"files[]": ('~/cover.jpg', image_data)}

        response = post(f"https://{domain}/upload.php", files=files)

        if response.status_code == 200:
            return response.json()["files"][0]["url"]
        else:
            raise ConnectionError("Failed to Upload Cover:", response.text)

    def upload(self, image_data):
        return self._pomf_upload(image_data, "pomf.lain.la")