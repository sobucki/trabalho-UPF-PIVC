import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.vision.gesture_stabilizer import GestureStabilizer

def main():
    print("Iniciando teste do GestureStabilizer...")
    stabilizer = GestureStabilizer(frames_required=3, cooldown_seconds=0.5)

    sequence = [None, 2, 2, 2, 2, None, 1, 1, 1]

    for label in sequence:
        result = stabilizer.update(label)
        print(f"Input: {label} -> Status: {result['status']}, Triggered: {result['triggered']}")
        
        # Simula o processamento do vídeo avançando o tempo suavemente para podermos checar cooldown
        if result['triggered']:
            print("--- (Dormindo por 0.6s para expirar cooldown) ---")
            time.sleep(0.6)

if __name__ == "__main__":
    main()
