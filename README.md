# PyDown

Search, stream and download YouTube videos from your terminal.

![PyDown demo](demo/pydown.gif)

Type a search (or paste a link), pick a result with fuzzy search, then download
the video, just the audio, or play it straight away in mpv or VLC. No browser needed.

## Features

- **Fuzzy search** through YouTube results with [fzf](https://github.com/junegunn/fzf)
- **Download video** at the resolution you choose (720p by default), optionally with English subtitles embedded
- **Download audio only**
- **Stream** in mpv or VLC without downloading
- **Remembers downloads**, so you don't fetch the same video twice
- Paste a YouTube link instead of searching, or pass a search on the command line

## Requirements

- Python 3.14+ and [uv](https://docs.astral.sh/uv/)
- [fzf](https://github.com/junegunn/fzf) for picking results
- [FFmpeg](https://ffmpeg.org/) for merging video and audio
- [mpv](https://mpv.io/) or [VLC](https://www.videolan.org/) to stream (PyDown offers to install it if missing)

On Arch Linux: `sudo pacman -S fzf ffmpeg mpv`. On Debian/Ubuntu: `sudo apt install fzf ffmpeg mpv`.

## Install

```sh
git clone https://github.com/Ericode254/PyDown.git
cd PyDown
uv sync
```

## Usage

```sh
uv run pyplayer.py                 # interactive: keep searching until Ctrl+C
uv run pyplayer.py "lofi hip hop"  # one search, then exit
```

Then answer the prompts:

1. Pick a result in fzf (type to filter, Enter to select).
2. `a` for audio or `v` for video.
3. For video, `d` to download or `p` to play, then the resolution and whether you want subtitles.

Files are saved in the current folder. The download history lives in
`~/.cache/ytdl_cache.json` (or under `$XDG_CACHE_HOME`).

## Recording the demo

The GIF is recorded with [VHS](https://github.com/charmbracelet/vhs) in a throwaway folder:

```sh
uv sync && vhs demo/demo.tape
```
