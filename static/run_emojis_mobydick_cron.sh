#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/knut/code/git/_my/python_stuff/find-emoji-dik"
LOGFILE="/var/tmp/logfile-cron.log"
PYTHON="python"

cd "$REPO_DIR"
source ".venv/bin/activate"

action() {
  #printf "%s Starting emoji job\n" "$(date -Is)"
  python ./src/emojis-mobydick.py >> "$LOGFILE" 2>&1
  #printf "%s Emoji job finished\n" "$(date -Is)"
}

action
