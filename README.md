# GestureHub CV

**Disciplina:** Processamento de Imagens e Visão Computacional  
**Professor:** Prof. Dr. Rafael Rieder  
**Alunos:** Rafael e Richardson

---

## 💻 Sobre o Projeto

O **GestureHub CV** é uma solução computacional de reconhecimento de padrões e processamento de imagens que permite o controle de funções do computador (como passador de apresentações) utilizando gestos corporais capturados por uma câmera. 

O projeto foi desenvolvido em Python e faz o uso de **Machine/Deep Learning** por intermédio das bibliotecas **OpenCV** e **MediaPipe** (Hand Landmarker), atendendo aos requisitos obrigatórios do trabalho prático.

## 🚀 Funcionalidades Implementadas

A arquitetura e as funções do projeto estão divididas nos seguintes módulos dentro do diretório `gesturehub-cv/`:

- **Interface Gráfica (GUI):** Construída com `PySide6` (`src/gui/`), fornecendo um painel moderno e robusto para iniciar o rastreamento, configurar atalhos e visualizar o processamento de imagens em tempo real.
- **Visão e Machine Learning:** Integração com o MediaPipe (`src/vision/`) para identificar landmarks de mãos e gerar eventos de gestos (ex: "Swipe direita", "Mão fechada").
- **Mapeamento e Execução de Comandos:** Módulos em `src/integrations/` e controle para mapear os gestos reconhecidos em atalhos de teclado (ex: Seta para Direita, Seta para Esquerda).
- **Múltiplas Fontes de Entrada:** Suporte para captura tanto via **Webcam ao vivo** quanto por **Arquivos de Vídeo** (`.mp4`, `.avi`, etc.), permitindo que diferentes arquivos de entrada sejam testados (conforme exigido pelo escopo). Os vídeos carregados rodam em loop, aplicando o FPS original e sem espelhamento incorreto da câmera.
- **Manipulação de Imagens:** Aplicação de rotinas e filtros sobre os frames capturados antes de exibi-los na tela de processamento.
