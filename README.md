# OpenEmuRPC

A simple application that provides your current OpenEmu game as an RPC state in Discord via [PyPresence](https://github.com/qwertyquerty/pypresence). Only available for MacOS, as is [OpenEmu](https://openemu.org/).

## 🚀 New Features (Zard Studios Fork)
Unlike the original project, this version includes:
- **Automatic Game Recognition**: Detects the game title directly from OpenEmu's window.
- **Automated Box Art**: Automatically fetches high-quality cover art from the [Libretro Thumbnail Database](https://thumbnails.libretro.com/) (RetroArch). No more manual uploads!
- **Smart Matching**: Handles regional variants (USA, Europe, Japan, World) to ensure the correct cover art is always found.
- **Apple Silicon Support**: Builds and runs natively on M1/M2/M3 Macs.


## How to use
Unzip and open the latest x86_64 version from the [releases tab](https://github.com/MCMi460/OpenEmuRPC/releases)
## How to build
Download the repository and run [build.sh](scripts/build.sh).

### If the app displays a Launch Error, give it permission like so:

** -> System Preferences -> Security and Privacy -> Screen Recording -> +**  
...and choose the app's location.

---
If you have any issues, [please create an issue here](https://github.com/MCMi460/OpenEmuRPC/issues/new).

### Credits
<a href="https://github.com/MCMi460"><img src="https://img.shields.io/static/v1?label=MCMi460&amp;message=Github&amp;color=c331d4"></a>

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

<!--- You found an easter egg! Here's a cookie UwU :totallyrealcookie.png: -->
