# MotionFlow AI — plano técnico da versão 2

## Objetivo

Manter a experiência simples do MotionFlow AI:

1. Enviar uma imagem da pessoa/personagem.
2. Enviar um vídeo de referência com o movimento.
3. Gerar e baixar um MP4 com a pessoa/personagem acompanhando o movimento.

A interface deve funcionar no navegador. O processamento será separado da interface para que o projeto não dependa da placa de vídeo do computador que está apenas abrindo a página.

## Decisão técnica inicial

A versão atual usa Wan-Animate-2 14B. Esse backend é mantido como opção de alta qualidade, mas não deve ser o caminho padrão para hardware limitado.

O candidato para o primeiro backend alternativo é **Motion Mirror com Wan2.1-VACE 1.3B**:

- O projeto de referência oferece CLI, API Python e interface web.
- O fluxo recebe uma imagem e um vídeo de movimento.
- A documentação do projeto informa cerca de 9 GB de VRAM livre, 32 GB de RAM e aproximadamente 20 GB de armazenamento de modelos para o backend 1.3B.
- O projeto informa que geração real em CPU não é suportada; o backend mock serve apenas para testes de interface.

Referência: https://github.com/halli75/motion-mirror

## Compatibilidade realista

| Ambiente | Situação |
|---|---|
| PC com Radeon Vega 3 integrada e 8 GB de RAM | Não é adequado para geração local com os modelos atuais. |
| GPU de nuvem com 15 GB de VRAM | Pode atender ao requisito de VRAM do backend 1.3B, mas é necessário confirmar também RAM do sistema, espaço em disco e compatibilidade CUDA. |
| GPU NVIDIA com pelo menos 9 GB livres e 32 GB de RAM | É o perfil mínimo publicado pelo projeto Motion Mirror para o backend 1.3B; desempenho varia. |
| Wan-Animate-2 14B | Continua sendo opção pesada e não será requisito para testar a interface. |

Não será prometido uso gratuito ilimitado. Colab e outros serviços podem limitar sessões, memória, GPU e tempo de execução.

## Arquitetura proposta

- **Interface:** Gradio em português, com upload da imagem e do vídeo, opções simples e visualização do MP4.
- **Camada de execução:** adaptador Python independente do modelo, para trocar o backend sem refazer a interface.
- **Backend inicial a validar:** Motion Mirror / Wan2.1-VACE 1.3B.
- **Backend avançado:** Wan-Animate-2, opcional e separado.
- **Execução:** primeiro em ambiente GPU temporário (por exemplo, Colab com recursos compatíveis); depois avaliar hospedagem própria.
- **Arquivos:** entradas e saídas temporárias, sem armazenar mídia do usuário por padrão.

## Etapas de desenvolvimento

1. Criar a interface e validar uploads, pré-visualização e exportação com arquivos de teste.
2. Integrar o backend Motion Mirror por subprocesso ou API Python, seguindo a CLI documentada pelo projeto.
3. Validar a instalação em Python 3.11 e uma GPU compatível, registrando versões e erros.
4. Adicionar barra de progresso, cancelamento, limpeza de arquivos temporários e mensagens claras para falta de VRAM/RAM.
5. Criar notebook de execução em nuvem somente depois de validar a instalação e a inferência em uma sessão GPU real.

## Critérios para considerar a versão pronta

- O aplicativo não pode apresentar um vídeo de demonstração como se fosse uma geração real.
- Se não houver GPU compatível, deve explicar o motivo e não iniciar uma inferência que certamente falhará.
- Deve validar imagem, vídeo, duração e parâmetros antes de iniciar.
- Deve mostrar o caminho/arquivo do resultado real e permitir baixá-lo.
- Deve informar claramente quando o ambiente gratuito não disponibilizar recursos suficientes.

## Licenças e atribuição

MotionFlow AI é um projeto independente. Antes de distribuir pesos, empacotar modelos ou oferecer geração como serviço, verificar a licença do código, dos pesos e de cada dependência. Não copiar pesos de modelos para este repositório.
