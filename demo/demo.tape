# Record with:  vhs demo/demo.tape   (run from the repo root, after `uv sync`)
# Runs in a throwaway folder with its own download history; your files are untouched.
Output demo/pydown.gif

Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 720
Set Padding 16
Set Theme "Catppuccin Mocha"
Set TypingSpeed 55ms
Set Framerate 24
Set WaitTimeout 60s

Hide
Type `R=$PWD; export XDG_CACHE_HOME=/tmp/pydown-demo-cache PS1='$ '; rm -rf /tmp/pydown-demo /tmp/pydown-demo-cache; mkdir -p /tmp/pydown-demo && cd /tmp/pydown-demo && alias pydown="$R/.venv/bin/python $R/pyplayer.py" && clear`
Enter
Sleep 500ms
Show

# 1. Search YouTube and pick a result with fzf
Type "pydown" Sleep 300ms Enter
Wait+Screen /Enter YouTube search/
Sleep 1s
Type "me at the zoo" Sleep 400ms Enter
Wait+Screen /\d+\/\d+/
Sleep 1.2s
Type "zoo jNQXAC" Sleep 1.2s
Enter

# 2. Download the video
Wait+Screen /audio or video/
Sleep 600ms
Type "v" Sleep 300ms Enter
Sleep 500ms
Type "d" Sleep 300ms Enter
Sleep 500ms
Enter
Sleep 500ms
Type "n" Sleep 300ms Enter
Wait+Screen /Download complete/
Sleep 1.5s

# 3. Paste a link and grab just the audio
Type "https://youtu.be/jNQXAC9IVRw" Sleep 400ms Enter
Sleep 2.5s
Type "a" Sleep 300ms Enter
Sleep 7s

# 4. Quit and look at what we got
Ctrl+C
Sleep 800ms
Type "ls -1" Sleep 300ms Enter
Sleep 2.5s
