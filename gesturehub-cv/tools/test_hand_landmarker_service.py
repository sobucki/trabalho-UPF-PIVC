import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.vision.hand_landmarker_service import create_default_hand_landmarker_service

def main():
    print("Iniciando teste do HandLandmarkerService...")
    try:
        with create_default_hand_landmarker_service() as detector:
            print("Detector inicializado com sucesso.")
            if detector.is_started:
                print("O status is_started e verdadeiro.")
                
        # Fora do contexto with, o detector deve fechar.
        print("Detector fechado com sucesso.")
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
