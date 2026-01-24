# YAMPR

<img align="right" alt="Example Rich Presence" src="img/example.png" height=150/>

**Y**et **A**nother **MP**RIS Discord **R**PC Client

"What a great acronym!"\
\- Satisfied YAMPR user

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

Features I haven't seen elsewhere:
- **Custom Covers:** Your local album covers are uploaded to a service of your choosing, meaning your obscure, undocumented-online music will display its album art!
    - The links are stored in a json file, so you can easily swap around or add images to songs without them embedded
    - Currently supports pomf.lain.la and catbox.moe, and adding new services is (theoretically) extremely straight forward
- **Configurability:** Customize the appearance of your rich presence to your liking. The possibilities are endless! (not really, but still)
- **Instant Updating:** Thanks to the power of asyncio, your rich presence will respond to seeks, pauses, and song changes instantly (although a rate limit of 15s does apply between changes)

Intentional Limitations:
- Paused music is not displayed. If you forget to close an mpv instance, it will be ignored to prevent your presence from elapsing time unto infinity
- Only local music is displayed. Stuff streamed through your browser, spotify, or otherwise will be ignored.

For something more fully featured, try [mprisence](https://github.com/lazykern/mprisence) or [music-discord-rpc.](https://github.com/patryk-ku/music-discord-rpc) This project is really just meant for local music (hence the custom covers and restrictions)

## Setup
Clone the repository.
```commandline
git clone https://github.com/Encampeded/YAMPR/
```

Install the dependencies; pypresence, dbus-fast, and HTTPX.

If you're on Arch:
```commandline
pacman -S python-pypresence python-dbus-fast python-httpx
```
Alternatively, make a virtual environment and install requirements with pip:
```commandline
python -m venv venv
source venv/bin/activate
pip install .
```
Make sure your music player (or its backend) supports MPRIS. For example, mpv requires the mpv-mpris plugin.
# Usage
Run the module in the repository directory.
```commandline
python -m yampr
```
You can configure the appearance of your rich presence in config.py

<img align="right" alt="Example Rich Presence" src="img/reference.png" height=150/>

```python
LISTENING_TO = "LISTENING_TO"
TITLE = "TITLE"
SUBTITLE = "SUBTITLE"
IMAGE_LABEL = "IMAGE_LABEL"
```
<br>

# Contributing
Not sure why you'd want to contribute to this, but if you want to, keep in mind this was my first time writing async code. If something seems wack or is non-standard, that's probably why lol. Feel free to fix it. Or don't. I don't really care.