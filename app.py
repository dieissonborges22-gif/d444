#!/usr/bin/env python3
"""MotionFlow AI — Portuguese Gradio front-end for the official Wan-Animate-2 backend."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

import gradio as gr


TITLE = "MotionFlow AI | Wan-Animate-2"
CUSTOM_CSS = r"""
:root { --mf-bg: #0b1020; --mf-panel: #121a2d; --mf-accent: #8b5cf6; }
.gradio-container { max-width: 1180px !important; margin: auto !important; }
#mf-hero { padding: 24px 26px; border: 1px solid #2a3653; border-radius: 18px;
  background: linear-gradient(120deg, #171d37, #111827 70%); margin-bottom: 16px; }
#mf-hero h1 { margin: 0 0 8px 0; font-size: 30px; }
#mf-hero p { color: #cbd5e1; margin: 0; }
#mf-note { border: 1px solid #66531f; border-radius: 12px; padding: 12px 16px;
  background: #211b10; color: #f5deb0; }
footer { display: none !important; }
"""


def gpu_report() -> tuple[str, list[float]]:
    try:
        import torch
    except Exception as exc:  # pragma: no cover - environment-specific
        return f"Não consegui importar PyTorch: {exc}", []

    if not torch.cuda.is_available():
        return "Nenhuma GPU NVIDIA/CUDA foi detectada. O backend oficial precisa de CUDA.", []

    details: list[str] = []
    memories: list[float] = []
    for index in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(index)
        vram_gb = props.total_memory / (1024**3)
        memories.append(vram_gb)
        details.append(f"GPU {index}: {props.name} — {vram_gb:.1f} GB VRAM")
    total = sum(memories)
    details.append(f"VRAM total detectada: {total:.1f} GB")
    if len(memories) < 2 or total < 80:
        details.append(
            "ATENÇÃO: esta máquina está abaixo do ambiente de referência publicado. "
            "O projeto oficial relata testes em 2×A800 para 480p e configuração padrão "
            "de 8×A800 para 720p. A geração pode falhar por falta de memória."
        )
    return "\n".join(details), memories


def build_backend(repo_dir: Path, config_path: Path, output_dir: Path) -> Any:
    if not repo_dir.exists():
        raise FileNotFoundError(
            f"Repositório oficial não encontrado: {repo_dir}. Execute setup.sh primeiro."
        )
    infer_dir = repo_dir / "infer"
    if not infer_dir.is_dir():
        raise FileNotFoundError(f"Pasta infer não encontrada em {repo_dir}.")
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuração não encontrada: {config_path}")

    # O projeto oficial resolve os caminhos ckpts relativos à pasta infer.
    sys.path.insert(0, str(repo_dir))
    sys.path.insert(0, str(infer_dir))
    os.chdir(infer_dir)

    try:
        from wan_animate_2_gradio_distillation import WanAnimate2App as OfficialWanApp
    except Exception as exc:
        raise RuntimeError(
            "Não consegui importar o backend oficial do Wan-Animate-2. "
            "Confirme que as dependências e o repositório oficial foram instalados. "
            f"Detalhe: {exc}"
        ) from exc

    return OfficialWanApp(str(config_path), str(output_dir))


def normalize_video_path(video: Any) -> str | None:
    if video is None:
        return None
    if isinstance(video, str):
        return video
    if isinstance(video, dict):
        return video.get("path") or video.get("name")
    return str(video)


def main() -> None:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--repo-dir", default=os.getenv("WAN_ANIMATE_REPO", "../Wan-Animate-2"))
    parser.add_argument(
        "--config",
        default=None,
        help="YAML do backend oficial; por padrão usa wan_animate_2_distillation.yaml.",
    )
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--share", action="store_true", help="Cria link público temporário do Gradio.")
    args = parser.parse_args()

    repo_dir = Path(args.repo_dir).expanduser().resolve()
    config_path = (
        Path(args.config).expanduser().resolve()
        if args.config
        else repo_dir / "infer" / "wan_animate_2_distillation.yaml"
    )
    output_dir = Path(args.output_dir).expanduse().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    gpu_text, memories = gpu_report()
    print(gpu_text, flush=True)
    if not memories:
        raise SystemExit(
            "GPU CUDA não detectada. Não vou carregar o modelo porque esta versão oficial "
            "nato executa em CPU de forma prática."
        )

    print("Carregando o backend oficial Wan-Animate-2...", flush=True)
    backend = build_backend(repo_dir, config_path, output_dir)

    def generate(
        reference_image,
        driving_video,
        prompt,
        prompt_ref,
        width,
        height,
        fps,
        seed,
        frames,
        steps,
        guidance,
    ):
        if reference_image is None:
            raise gr.Error("Envie uma imagem da pessoa/personagem.")
        video_path = normalize_video_path(driving_video)
        if not video_path or not Path(video_path).is_file():
            raise gr.Error("Envie um vídeo de movimento em MP4 ou outro formato compaível.")
        try:
            result, status = backend.process_video(
                refer_img=reference_image,
                tpl_video_path=video_path,
                width=int(width),
                height=int(height),
                fps=int(fps),
                seed=int(seed),
                clip_len=int(frames),
                sample_guide_scale=float(guidance),
                step=int(steps),
                prompt=(prompt or "Pessoa em movimento, preservando a aparência da imagem de referência."),
                prompt_ref=(prompt_ref or "Uma pessoa executando os movimentos do vídeo de referência."),
            )
            if result is None:
                raise gr.Error(status or "A geração falhou. Consulte o log do terminal.")
            return result, status
        except gr.Error:
            raise
        except Exception as exc:
            raise gr.Error(f"Erro durante a geração: {exc}") from exc

    with gr.Blocks(title=TITLE, css=CUSTOM_CSS, theme=gr.themes.Soft()) as demo:
        gr.HTML(
            """<div id="mf-hero">
              <h1>✪ MotionFlow AI</h1>
              <p>Anime uma pessoa usando uma imagem de referência e um |ídeo de movimento —"
              powered by Wan-Animate-2.</p>
            </div>"""
        )
        gr.Markdown(
            "**Como funciona:** envie uma imagem da pessoa que deseja animar e um vídeo com o movimento. "
            "O modelo tenta preservar a identidade visual enquanto transfere o movimento."
        )
        gr.Markdown(
            "<div id='mf-note'>⚠️ <b>Requisito importante:</b> esta interface nao fornece GPU nem hospeda os pesos. "
            "O Wan-Animate-2 é um modelo de dezenas de GB; uma GPU de 15 GB normalmente não é suficiente "
            "para esta implementação oficial.</div>"
        )
        with gr.Row():
            with gr.Column(scale=1):
                reference_image = gr.Image(label="1. Imagem da pessoa", type="pil")
                driving_video = gr.Video(label="2. Yídeo de movimento", sources=["upload"])
                prompt = gr.Textbox(
                    label="Descrição da aparência e do cenário",
                    placeholder="Ex.: Mulher com roupa esportiva preta, em um quarto iluminado...",
                    lines=3,
                )
                prompt_ref = gr.Textbox(
                    label="Descricção do movimento do vídeo",
                    value="Uma pessoa executando os movimentos do vídeo de referência.",
                    lines=2,
                )
                with gr.Accordion("Configurações avançadas", open=False):
                    with gr.Row():
                        width = gr.Number(label="Largura", value=640, precision=0)
                        height = gr.Number(label="Altura", value=800, precision=0)
                    with gr.Row():
                        fps = gr.Number(label="FPS", value=16, precision=0)
                        frames = gr.Number(label="Quadros", value=37, precision=0)
                    with gr.Row():
                        steps = gr.Number(label="Passos", value=10, precision=0)
                        guidance = gr.Number(label="CFG", value=1.0)
                    seed = gr.Number(label="Seed (-1 = aleatória)", value=-1, precision=0)
                generate_button = gr.Button("Gerar vídeo", variant="primary", size="lg")
            with gr.Column(scale=1):
                output_video = gr.Video(label="Resultado")
                status = gr.Textbox(label="Status da geração", interactive=False)
                gpu_status = gr.Textbox(label="Diagnóstico da GPU", value=gpu_text, interactive=False, lines=5)
                gr.Markdown(
                    "O vídeo gerado fica na pasta `outputs/`. A qualidade, o tempo e a estabilidade "
                    "dependem da GPU disponível e das configurações do modelo."
                )
        generate_button.click(
            fn=generate,
            inputs=[reference_image, driving_video, prompt, prompt_ref, width, height, fps, seed, frames, steps, guidance],
            outputs=[output_video, status],
        )

    demo.queue().launch(server_name=args.host, server_port=args.port, share=args.share)


if __name__ == "__main__":
    main()
