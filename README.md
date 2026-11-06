# MotionFlow AI — Wan-Animate-2

Interface em português para executar o **modelo oficial Wan-Animate-2 (distilled)** a partir de uma imagem de referência e um vídeo que contém o movimento.

> **Atenção: este repositório contém a interface e os scripts de instalação, não os pesos do modelo.** Os pesos são grandes e precisam ser baixados separadamente do Hugging Face. Esta interface não fornece GPU na nuvem.

## O que o aplicativo faz

- Recebe uma imagem da pessoa/personagem.
- Recebe um vídeo com o movimento que será transferido.
- Permite informar descrição visual e descrição do movimento.
- Permite ajustar resolução, FPS, quadros, seed, passos e CFG.
- Mostra o vídeo gerado e o status do processamento.
- Usa a implementação oficial do Wan-Animate-2 como backend, sem redistribuir seus pesos.

## Requisito de hardware — leia antes de instalar

O Wan-Animate-2 é um modelo 14B. O repositório oficial informa que a configuração padrão foi ajustada para **8 GPUs A800** em 720p e que foram feitos testes em 480p com **2 GPUs A800**. O checkpoint destilado sozinho ocupa aproximadamente **32,8 GB**; os encoders e demais arquivos elevam o download total para dezenas de GB.

Portanto:

- Um computador sem GPU NVIDIA não executa este backend localmente.
- Uma GPU de aproximadamente 15 GB (como a sessão de Colab que você usou antes) não é uma configuração adequada para esta implementação oficial e provavelmente falhará por falta de memória.
- O GitHub hospeda o código, não o processamento. Para gerar vídeos, é necessário ter acesso a uma máquina GPU compatível. O Colab gratuito não garante esse tipo de GPU nem uso ilimitado.

## Instalação em uma máquina GPU compatível

O projeto oficial recomenda Python 3.11 e PyTorch com CUDA 12.6. Em um terminal Linux com GPU NVIDIA compatível:

```bash
git clone https://github.com/dieissonborges22-gif/d444.git MotionFlow-WanAnimate2
cd MotionFlow-WanAnimate2
chmod +x setup.sh
./setup.sh
```

O script clona o backend oficial em uma pasta vizinha, instala as dependências e pergunta antes de iniciar um download de aproximadamente 50 GB ou mais. Para informar um diretório diferente do backend:

```bash
WAN_REPO_DIR=/caminho/Wan-Animate-2 ./setup.sh
```

## Iniciar a interface

Depois da instalação e do download dos pesos:

```bash
WAN_ANIMATE_REPO="../Wan-Animate-2" python3.11 app.py --share
```

`--share` cria um endereço temporário do Gradio para abrir a interface no navegador. Não é hospedagem permanente.

## Baixar os pesos manualmente

```bash
python3.11 download_models.py --upstream-dir ../Wan-Animate-2
```

O script baixa somente o checkpoint destilado e a pasta de encoders/VAEs usada pelo YAML oficial destilado, evitando baixar também o checkpoint Base de 32,8 GB.

## Estrutura

```text
MotionFlow-WanAnimate2/
├── app.py
├── download_models.py
├── requirements-ui.txt
├── setup.sh
├── README.md
└── .gitignore
```

## Fontes e licenças

- Código e instruções oficiais: https://github.com/Wan-Video/Wan-Animate-2
- Pesos oficiais: https://huggingface.co/Wan-AI/Wan2.2-Animate-2-14B
- O projeto original e os pesos publicados indicam licença Apache-2.0. Consulte os termos e avisos originais antes de redistribuir ou oferecer o serviço.

Este repositório é uma interface comunitária independente e não é afiliado à equipe Wan-AI.
