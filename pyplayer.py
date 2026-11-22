import subprocess
import sys
import yt_dlp
from tqdm import tqdm
import re
from colorama import Fore, Style, init
import os
import json

# Initialize colorama
init(autoreset=True)

# ASCII Art Banner
BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}
░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░         ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░         ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░         ░▒▓█▓▒░   ░▒▓███████▓▒░ ░▒▓██████▓▒░ ░▒▓█████████████▓▒░░▒▓█▓▒░░▒▓█▓▒░ 
                                                                                       
{Style.RESET_ALL}
"""

CACHE_DIR = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
CACHE_FILE = os.path.join(CACHE_DIR, "ytdl_cache.json")

def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache: dict[str, str]) -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def is_package_installed(package_name: str) -> bool:
    return subprocess.call(["which", package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def detect_package_manager() -> tuple:
    managers = {
        "apt": "sudo apt update && sudo apt install -y",
        "dnf": "sudo dnf install -y",
        "yum": "sudo yum install -y",
        "pacman": "sudo pacman -S --noconfirm",
        "zypper": "sudo zypper install -y",
        "emerge": "sudo emerge"
    }
    for mgr, cmd in managers.items():
        if is_package_installed(mgr):
            return mgr, cmd
    return None, None

def install_package(package_name: str) -> None:
    if is_package_installed(package_name):
        print(f"{package_name} is already installed.")
        return
    manager, command = detect_package_manager()
    if manager:
        print(f"{Fore.YELLOW}Installing {package_name} using {manager}...")
        os.system(f"{command} {package_name}")
    else:
        print(f"{Fore.RED}No supported package manager found.")

def is_valid_url(url: str) -> bool:
    regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/[^\s]+'
    return bool(re.match(regex, url))

# Shared yt-dlp options: hide its own log lines so only our progress bar shows.
QUIET = {"quiet": True, "no_warnings": True, "noprogress": True}

def search_youtube(query: str, max_results=30) -> list:
    print(f"{Fore.YELLOW}Searching YouTube...")
    try:
        with yt_dlp.YoutubeDL({**QUIET, "extract_flat": True}) as ydl:
            info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
    except yt_dlp.utils.DownloadError as e:
        print(f"{Fore.RED}Search error: {e}")
        return []
    return [
        (e["title"], f"https://www.youtube.com/watch?v={e['id']}")
        for e in (info or {}).get("entries", [])
        if e and e.get("id") and e.get("title")
    ]

def choose_video(videos: list[tuple[str,str]]) -> str | None:
    options = [f"{title} | {url}" for title, url in videos]
    result = subprocess.run(["fzf"], input="\n".join(options), text=True, capture_output=True).stdout.strip()
    for title, url in videos:
        if title in result:
            return url
    return None

pbar = None
def yt_dlp_progress_hook(d) -> None:
    global pbar

    if d["status"] == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        downloaded = d.get("downloaded_bytes", 0)

        if total:
            if pbar is None:
                pbar = tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    desc=f"{Fore.GREEN}Downloading",
                    ncols=100
                )

            pbar.n = downloaded
            pbar.refresh()

    elif d["status"] == "finished":
        if pbar:
            pbar.close()
            pbar = None         
            print(f"\n{Fore.GREEN}Download complete!")

def download_video_with_subtitle(url: str, resolution="720") -> None:
    print(f"{Fore.YELLOW}Downloading video...")
    ydl_opts = {
        **QUIET,
        "outtmpl": "%(title)s.%(ext)s",
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'progress_hooks': [yt_dlp_progress_hook],

        # Subtitle options
        "writesubtitles": True,          # download subtitles
        "writeautomaticsub": True,       # fallback to auto subtitles
        "subtitleslangs": ["en"],        # language(s)
        "subtitlesformat": "srt",        # convert to srt

        # Embedding
        "embedsubtitles": True,
        "merge_output_format": "mkv",    # strongly recommended

        # FFmpeg
        "postprocessors": [
            {
                "key": "FFmpegEmbedSubtitle",
            }
        ],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError:
        # YouTube often rate-limits subtitle requests; still get the video.
        print(f"{Fore.YELLOW}Subtitles aren't available right now; downloading the video without them.")
        download_video(url, resolution)


def download_video(url: str, resolution="720") -> None:
    print(f"{Fore.YELLOW}Downloading video...")
    ydl_opts = {
        **QUIET,
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [yt_dlp_progress_hook]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_audio(url: str) -> None:
    print(f"{Fore.YELLOW}Downloading audio...")
    ydl_opts = {
        **QUIET,
        'format': 'bestaudio/best',
        # A separate name so it never collides with the same video's file.
        'outtmpl': '%(title)s (audio).%(ext)s',
        'progress_hooks': [yt_dlp_progress_hook]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def play_video(url: str, player: str) -> None:
    print(f"{Fore.YELLOW}Playing with {player}...")
    subprocess.run([player, url])

def main():
    print(BANNER)
    cache = load_cache()

    # A search passed on the command line runs once; otherwise keep prompting.
    one_shot = " ".join(sys.argv[1:]).strip()
    while True:
        query = one_shot or input(f"{Fore.CYAN}Enter YouTube search or URL: {Style.RESET_ALL}").strip()
        if not query:
            continue

        if is_valid_url(query):
            selected_url = query
        else:
            videos = search_youtube(query)
            if not videos:
                print(f"{Fore.RED}No results found.")
                return
            selected_url = choose_video(videos)
            if not selected_url:
                print(f"{Fore.RED}No video selected.")
                return

        if selected_url in cache:
            print(f"{Fore.GREEN}Already downloaded: {cache[selected_url]}")
            return

        print(f"{Fore.GREEN}Selected: {selected_url}")
        choice = input(f"{Fore.CYAN}Download audio or video? (a/v): ").strip().lower() or "v"
        if choice == 'a':
            download_audio(selected_url)
            cache[selected_url] = "audio"
        else:
            act = input(f"{Fore.CYAN}Download or play the video? (d/p): ").strip().lower()
            if act == 'd' or act == '':
                res = input(f"{Fore.CYAN}Resolution? (default 720): ").strip() or "720"
                subtitle = input(f"{Fore.CYAN}Do you want to have subtitles too (y/n): ").lower() or "n"
                if subtitle == "n":
                    download_video(selected_url, res)
                elif subtitle == "y":
                    download_video_with_subtitle(selected_url, res)
                else:
                    download_video(selected_url, res)
                cache[selected_url] = res
            elif act == 'p':
                player = input(f"{Fore.CYAN}Use vlc or mpv? (v/m): ").strip().lower()
                chosen_player = "vlc" if player == 'v' else "mpv"
                install_package(chosen_player)
                play_video(selected_url, chosen_player)
            else:
                print(f"{Fore.RED}Invalid choice.")
                return

        save_cache(cache)
        if one_shot:
            return


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Fore.CYAN}Bye!")
