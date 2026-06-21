# GestureHub CV

**Disciplina:** Processamento de Imagens e Visão Computacional  
**Professor:** Prof. Dr. Rafael Rieder  
**Alunos:** Rafael e Richardson

---

## 💻 Sobre o Projeto

O **GestureHub CV** é uma solução computacional de reconhecimento de padrões e processamento de imagens que permite o controle de funções do computador (como passador de apresentações) utilizando gestos das mãos capturados por uma câmera.

O projeto foi desenvolvido em Python e combina **Visão Computacional** (MediaPipe Hand Landmarker, para extração dos pontos de referência da mão) com **Aprendizado de Máquina** (SVM do OpenCV, treinado sobre o dataset HaGRID com 12 classes de gestos estáticos), atendendo aos requisitos obrigatórios do trabalho prático.

## 🚀 Funcionalidades Implementadas

A arquitetura e as funções do projeto estão divididas nos seguintes módulos dentro do diretório `gesturehub-cv/`:

- **Interface Gráfica (GUI):** Construída com `PySide6` (`src/gui/`), fornecendo um painel para iniciar o rastreamento, configurar atalhos e visualizar o processamento de imagens em tempo real.
- **Visão Computacional e Classificação de Gestos:** Uso do MediaPipe Hand Landmarker (`src/vision/`) para extrair os landmarks da mão e de um SVM (OpenCV ML) para classificar gestos estáticos (ex: "Mão aberta", "Punho fechado", "Joinha"), além de um detector de gestos dinâmicos de arrastar (`swipe_detector.py`) que reconhece **Swipe Esquerda/Direita** a partir do deslocamento horizontal do pulso enquanto a mão está aberta.
- **Mapeamento e Execução de Comandos:** Módulos em `src/integrations/` que mapeiam os gestos reconhecidos em atalhos de teclado (ex: Seta para Direita/Esquerda) ou teclas de mídia (ex: Play/Pause, Próxima Faixa), com perfis de integração pré-configurados (apresentações, mídia/Spotify).
- **Múltiplas Fontes de Entrada:** Suporte para captura tanto via **Webcam ao vivo** quanto por **Arquivos de Vídeo** (`.mp4`, `.avi`, etc.), permitindo que diferentes arquivos de entrada sejam testados (conforme exigido pelo escopo). Os vídeos carregados rodam em loop, aplicando o FPS original e sem espelhamento incorreto da câmera.
- **Realce de Imagem em Baixa Luminosidade:** Filtro opcional baseado em CLAHE (Contrast Limited Adaptive Histogram Equalization), aplicado sobre o frame antes da detecção para melhorar o contraste em ambientes com pouca luz.

## 🎥 Vídeo Demonstrativo

[Assista à demonstração do GestureHub CV no YouTube](https://www.youtube.com/watch?v=SEU_LINK_AQUI)

## ⚙️ Pré-requisitos

- Python 3.10+ instalado
- Webcam (para o modo de captura ao vivo) e/ou um arquivo de vídeo (`.mp4`, `.avi`, etc.) para teste

## 📦 Como Executar

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd "Trabalho PPIV/gesturehub-cv"
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   python main.py
   ```

5. Na interface, escolha a fonte de entrada (webcam ou arquivo de vídeo), inicie o rastreamento e faça os gestos suportados na frente da câmera.
