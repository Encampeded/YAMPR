# YAMPR
**Y**et **A**nother **MP**RIS Discord **R**PC Client

"What a great acronym!"\
\- Satisfied YAMPR user

Features I haven't seen elsewhere:
- Configurability: Customize the appearance of your rich presence to your liking. The possibilities are endless! (not really, but still)
- Custom Covers: Your local album covers get uploaded to a service of your choosing, meaning all your obscure, undocumented-online albums actually display their covers!
  - Currently, only pomf.lain.la is supported, but adding new services is (theoretically) extremely straight forward.
- Instant Updating: Your rich presence will update as soon as your music ends; no more getting stuck at the end of a song! ~~is this an actual feature or~~

## Setup
If you're on Arch:
```commandline
sudo pacman -S python-pypresence python-pydbus python-requests
yay -S python-tinytag
```
Alternatively, make a venv and install requirements with pip
```commandline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Ensure your music player, or its backend, supports MPRIS. For example, mpv requires the mpv-mpris plugin.
# Usage
Just run rpc.py!
```commandline
$ python rpc.py
```
You can configure the appearance of your rich presence in config.py
See reference.png for what the variables affect.