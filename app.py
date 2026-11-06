#!/usr/bin/env python3
"""Interface em português para o backend oficial Wan-Animate-2 Distilled."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import gradio as gr


def gpu_report() -> tuple[str, bool]:
    try:
        import torch
    except Exception as exc:
        return f"Falha ao importar PyTorch: {exc}", False
    if not torch.cuda.is_available():
        return "Nenhuma GPU NVIDIA/CUDA detectada.", False
    lines = []
    memories = []
    for i in range(torch.cuda.device_count()):
        prop = torch.cuda.get_device_properties(i)
        memory = prop.total_memory / (1024**3)
        memories.append(memory)
        lines.append(f"GPU {i}: {prop.name} — {memory:.1f} GB VRAM")
    lines.append(f"VRAM total: {sum(memories):.1f} GB")
    if len(memories) < 2 or sum(memories) < 80:
        lines.append(
            "AVISO: abaixo do ambiente de referência. O repositório oficial relata testes "
            "com 2×A800 em 480p e configuração padrão de 8×A800 em 720p. A geração pode falhar."
        )
    return "\n".join(lines), True


def make_backend(repo_dir: Path, config: Path, output_dir: Path):
    infer_dir = repo_dir / "infer"
    if not infer_dir.is_dir():
        raise FileNotFoundError(f"Backend oficial não encontrado: {infer_dir}")
    if not config.is_file():
        raise FileNotFoundError(f"Configuração não encontrada: {config}")
    sys.path.insert(0, str(repo_dir))
    sys.path.insert(0, str(infer_dir))
    os.chdir(infer_dir)  # caminhos ckpts do YAML oficial são relativos a infer/
    try:
        from wan_animate_2_gradio_distillation import WanAnimate2App
    except Exception as exc:
        raise RuntimeError(f"Falha ao importar o backend oficial: {exc}") from exc
    return WanAnimate2App(str(config), str(output_dir))


def video_path(value):
    if isinstance(value, dict):
        return value.get("path") or value.get("name")
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", default=os.getenv("WAN_ANIMATE_REPO", "../Wan-Animate-2"))
    parser.add_argument("--config", default=None)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--share", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo_dir).expanduser().resolve()
    config = Path(args.config).expanduser().resolve() if args.config else repo / "infer" / "wan_animate_2_distillation.yaml"
    output = Path(args.output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)

    report, cuda_ok = gpu_report()
    print(report, flush=True)
    if not cuda_ok:
        raise SystemExit("O modelo oficial precisa de GPU CUDA; não vou tentar executá-lo em CPU.")

    engine = make_backend(repo, config, output)

    def generate(image, video, prompt, prompt_ref, width, height, fps, frames, steps, cfg, seed):
        if image is None:
            raise gr.Error("Envie uma imagem da pessoa/personagem.")
        path = video_path(video)
        if not path or not Path(path).is_file():
            raise gr.Error("Envie um vídeo de movimento válido.")
        result, status = engine.process_video(
            refer_img=image,
            tpl_video_path=path,
            width=int(width),
            height=int(height),
            fps=int(fps),
            seed=int(seed),
            clip_len=int(frames),
            sample_guide_scale=float(cfg),
            step=int(steps),
            prompt=prompt or "Pessoa em movimento, preservando a aparência da imagem de referência.",
            prompt_ref=prompt_ref or "Uma pessoa executando os movimentos do vídeo de referência.",
        )
        if result is None:
            raise gr.Error(status or "A geração falhou. Consulte o log do terminal.")
        return result, status

    css = """.gradio-container{max-width:1180px!important} #hero{padding:22px;border-radius:16px;background:linear-gradient(120deg,#171d37,#111827);border:1px solid #334155} #hero p{color:#cbd5e1} #warning{padding:12px;border:1px solid #8a6d2e;border-radius:10px;background:#211b10;color:#f5deb0}"""
    with gr.Blocks(title="MotionFlow AI | Wan-Animate-2", css=css, theme=gr.themes.Soft()) as demo:
        gr.HTML("<div id='hero'><h1>✨ MotionFlow AI</h1><p>Anime uma pessoa com imagem de referência + vídeo de movimento usando Wan-Animate-2.</p></div>")
        gr.Markdown("Envie a imagem da pessoa e o vídeo que contém o movimento. Ajuste os parâmetros avançados quando necessário.")
        gr.HTML("<div id='warning'>⚠️ Esta interface não fornece GPU nem hospeda os pesos. O modelo ocupa dezenas de GB; uma GPU de 15 GB normalmente não é suficiente para a implementação oficial.</div>")
        with gr.Row():
            with gr.Column():
                image = gr.Image(label="1. Imagem da pessoa", type="pil")
                video = gr.Video(label="2. Vídeo de movimento", sources=["upload"])
                prompt = gr.Textbox(label="Descrição da aparência e do cenário", lines=3, placeholder="Ex.: mulher com roupa esportiva preta, em um quarto iluminado...")
                prompt_ref = gr.Textbox(label="Descrição do movimento", lines=2, value="Uma pessoa executando os movimentos do vídeo de referência.")
                with gr.Accordion("Configurações avançadas", open=False):
                    with gr.Row():
                        width = gr.Number(label="Largura", value=640, precision=0)
                        height = gr.Number(label="Altura", value=800, precision=0)
                    with gr.Row():
                        fps = gr.Number(label="FPS", value=16, precision=0)
                        frames = gr.Number(label="Quadros", value=37, precision=0)
                    with gr.Row():
                        steps = gr.Number(label="Passos", value=10, precision=0)
                        cfg = gr.Number(label="CFG", value=1.0)
                    seed = gr.Number(label="Seed (-1 = aleatória)", value=-1, precision=0)
                button = gr.Button("Gerar vídeo", variant="primary", size="lg")
            with gr.Column():
                result = gr.Video(label="Resultado")
                status = gr.Textbox(label="Status", interactive=False)
                gpu = gr.Textbox(label="Diagnóstico da GPU", value=report, lines=6, interactive=False)
        button.click(generate, [image, video, prompt, prompt_ref, width, height, fps, frames, steps, cfg, seed], [result, status])

    demo.queue().launch(server_name="0.0.0.0", server_port=args.port, share=args.share)


if __name__ == "__main__":
    main()
