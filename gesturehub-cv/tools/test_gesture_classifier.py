import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.vision.gesture_classifier import create_default_gesture_classifier

def main():
    print("Iniciando teste do GestureClassifier...")
    try:
        classifier = create_default_gesture_classifier()
        
        if classifier.is_loaded:
            print("Modelo SVM carregado com sucesso!")
            
        # Mock de 42 features (zeros absolutos não representarão um gesto real, mas validará a inferência)
        features = np.zeros(42, dtype=np.float32)
        
        label = classifier.predict(features)
        print(f"Predicted label: {label}")
        print("Classificacao efetuada sem quebras estruturais.")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
