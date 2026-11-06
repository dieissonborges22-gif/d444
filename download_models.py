#!/usr/bin/env python3
"""Download only the checkpoints required by the official distilled Wan-Animate-2 config."""
from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-dir", default="../Wan-Animate-2")
    parser.add_argument("--token", default=os.getenv("HF_TOKEN"))
    args = parser.parse_args()

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise SystemExit("Instale huggingface_hub: pip install -U huggingface_hub") from exc

    upstream = Path(args.upstream_dir).expanduser().resolve()
    ckpt_dir = upstream / "ckpts"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    patterns = [
        "videomodel/Wan-AI/**",
        "wan_animate_2/wan_animate_2_bf16_distillation.safetensors",
    ]
    print("Baixando o modelo destilado e seus encoders auxiliares.")
    print("A transferência pode ocupar aproximadamente 50 GB ou mais.")
    snapshot_download(
        repo_id="Wan-AI/Wan2.2-Animate-2-14B",
        local_dir=str(ckpt_dir),
        allow_patterns=patterns,
        token=args.token,
    )
    print(f"Arquivos baixados em: {ckpt_dir}")


if __name__ == "__main__":
    main()
