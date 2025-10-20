from requests import post

# Ideally I would revise this to support more uploaders.
# However, pomf.lain.la works and idrc lol. Sorry.
# Vague plan if i change course though:
#  - Support temp uploads, mainly uguu (which is also pomf)

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

    # ABOUT:
    # This program originally used catbox as the upload service.
    # However, I'm preeeetty sure that doing so was against catbox's
    # TOS, so I'm no longer doing so. Leaving this here in case catbox
    # TOS violating is a future necessary evil, and the fact that catbox
    # uses different uploading than pomfs (like uguu or pomf.lain.la)
    @staticmethod
    def upload_catbox(self, image):
        data = {
            "reqtype": "fileupload",
        }

        files = {
            # Commented out because I removed BytesIO import
            #'fileToUpload': BytesIO(image.data)
        }

        response = post("https://catbox.moe/user/api.php", data=data, files=files)

        if response.status_code == 200:
            return response.text.strip()
        else:
            raise ConnectionError("Failed to Upload Cover:", response.status_code, response.text)