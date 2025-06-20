import subprocess
import sys
from pytube import Search
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

CACHE_FILE = os.path.expanduser("~/.cache/ytdl_cache.json")

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def is_package_installed(package_name):
    return subprocess.call(["which", package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def detect_package_manager():
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

def install_package(package_name):
    if is_package_installed(package_name):
        print(f"{package_name} is already installed.")
        return
    manager, command = detect_package_manager()
    if manager:
        print(f"{Fore.YELLOW}Installing {package_name} using {manager}...")
        os.system(f"{command} {package_name}")
    else:
        print(f"{Fore.RED}No supported package manager found.")

def is_valid_url(url):
    regex = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/[^\s]+'
    return bool(re.match(regex, url))

def search_youtube(query, max_results=50):
    try:
        search = Search(query)
        print(f"{Fore.YELLOW}Searching YouTube...")
        if search.results is not None:
            return [(v.title, v.watch_url) for v in search.results[:max_results]] 
        return []
    except Exception as e:
        print(f"{Fore.RED}Search error: {e}")
        return []

def choose_video(videos):
    options = [f"{title} | {url}" for title, url in videos]
    result = subprocess.run(["fzf"], input="\n".join(options), text=True, capture_output=True).stdout.strip()
    for title, url in videos:
        if title in result:
            return url
    return None

def yt_dlp_progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
        percent = d.get('downloaded_bytes', 0) * 100 // total
        pbar.n = percent
        pbar.refresh()
    elif d['status'] == 'finished':
        pbar.n = 100
        pbar.refresh()
        print(f"\n{Fore.GREEN}Download complete!")

def download_video(url, resolution="720"):
    print(f"{Fore.YELLOW}Downloading video...")
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [yt_dlp_progress_hook]
    }
    with tqdm(total=100, desc=f"{Fore.GREEN}Downloading", ncols=100, ascii=" █▒░") as bar:
        global pbar
        pbar = bar
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

def download_audio(url):
    print(f"{Fore.YELLOW}Downloading audio...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [yt_dlp_progress_hook]
    }
    with tqdm(total=100, desc=f"{Fore.GREEN}Downloading", ncols=100, ascii=" █▒░") as bar:
        global pbar
        pbar = bar
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

def play_video(url, player):
    print(f"{Fore.YELLOW}Playing with {player}...")
    subprocess.run([player, url])

def main():
    print(BANNER)
    cache = load_cache()

    query = sys.argv[1] if len(sys.argv) > 1 else input(f"{Fore.CYAN}Enter YouTube search or URL: {Style.RESET_ALL}").strip()

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
    choice = input(f"{Fore.CYAN}Download audio or video? (a/v): ").strip().lower()
    if choice == 'a':
        download_audio(selected_url)
        cache[selected_url] = "audio"
    else:
        act = input(f"{Fore.CYAN}Download or play the video? (d/p): ").strip().lower()
        if act == 'd':
            res = input(f"{Fore.CYAN}Resolution? (default 720): ").strip() or "720"
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

if __name__ == "__main__":
    main()
