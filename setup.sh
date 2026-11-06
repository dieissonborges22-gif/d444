#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAN_REPO_DIR="${WAN_REPO_DIR:-$(dirname "$PROJECT_DIR")/Wan-Animate-2}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3.11 não encontrado. O projeto oficial recomenda Python 3.11."
  exit 1
fi

if [[ ! -d "$WAN_REPO_DIR/.git" ]]; then
  git clone --recursive https://github.com/Wan-Video/Wan-Animate-2.git "$WAN_REPO_DIR"
else
  echo "Repositório oficial já existe em $WAN_REPO_DIR"
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu126
"$PYTHON_BIN" -m pip install -r "$WAN_REPO_DIR/requirements.txt"
"$PYTHON_BIN" -m pip install flash-attn --no-build-isolation
"$PYTHON_BIN" -m pip install -e "$WAN_REPO_DIR"
"$PYTHON_BIN" -m pip install -r "$PROJECT_DIR/requirements-ui.txt"

read -r -p "Baixar os pesos destilados (aprox. 50 GB ou mais)? [s/N] " answer
if [[ "$answer" =~ ^[sS]$ ]]; then
  "$PYTHON_BIN" "$PROJECT_DIR/download_models.py" --upstream-dir "$WAN_REPO_DIR"
fi

echo
echo "Instalação concluída. Para iniciar:"
echo "  WAN_ANIMATE_REPO=\"$WAN_REPO_DIR\" $PYTHON_BIN \"$PROJECT_DIR/app.py\" --share"
